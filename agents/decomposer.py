import json
from services.llm_client import generate_response
from utils.json_parser import parse_llm_json
from core.config import get_model

# ---------------------------------------------------------------------------
# SHARED BASE PROMPT (no recording awareness)
# ---------------------------------------------------------------------------

_BASE_SYSTEM_PROMPT = (
    "You are a pure intent classifier and dispatcher. Your job is to determine "
    "if a user goal is 'short' (completable in ONE tool call) or 'long' "
    "(requires iteration, waiting, or multiple interactions).\n\n"
    "If the task requires more than one tool call or requires waiting for a UI response, "
    "stop immediately and emit only the handoff JSON. Do not begin execution.\n\n"
    "If SHORT:\n"
    "Emit a JSON object exactly like this (can include multiple function_calls in a list if needed):\n"
    "{\n"
    "  \"text\": \"1. Open Microsoft Edge.\\n2. Navigate to https://google.com.\\n3. Wait for load.\\n4. Save webpage structure.\",\n"
    "  \"function_calls\": [\n"
    "    { \"name\": \"launch_app\", \"args\": { \"path\": \"msedge.exe\", \"args\": [\"https://google.com\"] } },\n"
    "    { \"name\": \"wait\", \"args\": { \"seconds\": 3 } },\n"
    "    { \"name\": \"save_webpage_structure\", \"args\": { \"url\": \"https://google.com\", \"filename\": \"google_structure.json\" } }\n"
    "  ]\n"
    "}\n"
    "Valid functions: click, launch_app, read_screen, analyze_screen, open_url, "
    "click_element, type_in_element, wait, save_webpage_structure, smart_web_action, drag_and_drop.\n"
    "- type_text(text) — types raw keystrokes globally, no window targeting. Use ONLY when no specific element exists.\n"
    "- type_in_element(window_title, control_title, text) — types into a specific UI element. PREFER this over type_text.\n"
    "- click_element(window_title, control_title)\n"
    "- drag_and_drop(start_x, start_y, end_x, end_y)\n"
    "CRITICAL: Always insert a dynamic 'wait' step after 'launch_app' or 'open_url' "
    "(estimate seconds based on likely load time) before any follow-up UI action.\n"
    "When launching a browser (msedge.exe or chrome.exe), ALWAYS include the \"--new-window\" flag "
    "in the 'args' list to ensure a clean workspace. If the user provides a URL, append it after the flag.\n"
    "When 'heading over' to a URL, you MUST always call 'save_webpage_structure' after opening it "
    "to ensure the local knowledge base is updated.\n"
    "LOGIN AWARENESS: Many sites (Gmail, AI Studio) may already be logged in. "
    "Before typing credentials, check if the page is already at the dashboard or inbox. "
    "If so, SKIP typing and proceed to the next relevant action.\n"
    "For complex tasks like 'type X into the search bar', ALWAYS prefer 'smart_web_action' "
    "which combines scraping and element discovery. "
    "Signature: smart_web_action(url_domain: str, instruction: str, expected_title_re: str).\n"
    "STRICT RULE: Each 'smart_web_action' must perform exactly ONE atomic UI interaction. "
    "Combining multiple steps (e.g., 'type something AND click start') into a single "
    "smart_web_action is FORBIDDEN. If a goal requires multiple steps, you MUST emit a list "
    "of separate function_calls.\n"
    "Correct: [{'name': 'smart_web_action', 'args': {'instruction': 'type hello'}}, "
    "{'name': 'smart_web_action', 'args': {'instruction': 'click search'}}]\n"
    "Incorrect: [{'name': 'smart_web_action', 'args': {'instruction': 'type hello and click search'}}]\n"
    "REPETITION: If the user asks to repeat an action multiple times (e.g., 'do X 10 times'), "
    "you MUST expand the list of function_calls to include all repetitions.\n"
    "RECORDING: If the user asks to 'repeat my recording' or 'do the recorded task', "
    "emit a JSON with \"task_type\": \"replay_recording\" and \"repeat_count\": X.\n"
    "The instruction must be highly specific, referencing element IDs or names from your "
    "mental model of the structure if possible: "
    "e.g., 'type explain how you work into the email input field with id identifierId'.\n"
    "Do not explain further, do not list next steps, do not reason out loud.\n\n"
    "If LONG:\n"
    "Emit a JSON object exactly like this:\n"
    "{\n"
    "  \"task_type\": \"long\",\n"
    "  \"goal\": \"<original goal>\",\n"
    "  \"ui_target\": \"<detected application>\",\n"
    "  \"iterable_payload\": [\"<item1>\", \"<item2>\"],\n"
    "  \"parameters\": {}\n"
    "}\n"
    "Forbidden from beginning execution or reasoning about steps. Only emit the handoff.\n\n"
    "Return ONLY the valid JSON object."
)

# ---------------------------------------------------------------------------
# RECORDING-AWARE EXTENSION (appended only when a recording exists)
# ---------------------------------------------------------------------------

_RECORDING_EXTENSION = (
    "\n\n--- RECORDING-AWARE MODE ---\n"
    "A user recording IS present. The following rules override the defaults above:\n"
    "1. NEVER open a new window or navigate to a new URL unless the recording explicitly did so.\n"
    "2. Treat the recording as the exact template — same window, same element, same action sequence.\n"
    "3. If the user says 'do the same but type X', replay the EXACT same element interactions "
    "from the recording but substitute the new text for the old text. Do NOT change anything else.\n"
    "4. The url_domain for any smart_web_action MUST be derived from the recorded domain below. "
    "NEVER guess or hardcode a url_domain that is not in the recording context.\n"
    "5. If the recorded action targeted a specific window, all actions must target that same "
    "window_title. EXCEPTION: 'tk' is the agent's own UI and must NEVER be used as a "
    "window_title target — always use the actual application window from the recording instead.\n"
    "6. CRITICAL: If the recording used individual key presses (Pressed key: m, Pressed key: a ...) "
    "to type text, you MUST use type_in_element with the window_title from the recording. "
    "NEVER use smart_web_action to reproduce key-press-based recordings — the element was already "
    "focused in the recording, so just type directly into that same window and control.\n"
    "7. ABSOLUTE RULE: If the recorded summary contains 'USE_EXACTLY:', you MUST copy those "
    "exact function calls with NO substitutions except replacing <new_text> with the user's "
    "requested text. You are FORBIDDEN from guessing element names like 'prompt-input', "
    "'chat-input', or any other name. The element has no addressable title — type_text is "
    "the ONLY valid typing method here. Any deviation from USE_EXACTLY is a critical error.\n"
    "Do not explain further, do not list next steps, do not reason out loud.\n"
    "Return ONLY the valid JSON object."
)
# ---------------------------------------------------------------------------
# PUBLIC ENTRY POINT
# ---------------------------------------------------------------------------

def route_goal(goal: str, cache_block: str = "", context_block: str = "") -> str:
    """
    Routes a goal using two distinct prompt paths:

    - Plain path     : base prompt only. Used when no recording is active.
    - Recording path : base prompt + _RECORDING_EXTENSION + recording context.
                       Used when a recording is detected in context_block.

    Both paths share _BASE_SYSTEM_PROMPT so function definitions stay consistent.
    """
    import logging
    logger = logging.getLogger("AgentCore")

    cache_instr = (
        f"\n\n{cache_block}\n"
        "Use the CACHE if it matches the current goal exactly."
    ) if cache_block else ""

    # ── Detect whether a recording is present in the context block ──────────
    has_recording = "Active Recording detected" in context_block

    if has_recording:
        # ── RECORDING PATH ───────────────────────────────────────────────────
        # Appends the strict recording rules + full recording context
        ctx_instr = (
            f"\n\n{context_block}\n"
            "CONTEXTUAL AWARENESS: A recording is active. "
            "Prefer the recorded window and elements for ALL actions. "
            "The recorded domain is the ONLY valid url_domain."
        )
        system_prompt = (
            _BASE_SYSTEM_PROMPT
            + _RECORDING_EXTENSION
            + cache_instr
            + ctx_instr
        )
        logger.debug("--- DECOMPOSER: using RECORDING-AWARE prompt path ---")
    else:
        # ── PLAIN PATH ───────────────────────────────────────────────────────
        # Active window context only — no recording noise
        ctx_instr = (
            f"\n\n{context_block}\n"
            "CONTEXTUAL AWARENESS: Prefer the 'Active Window' for actions."
        ) if context_block else ""
        system_prompt = (
            _BASE_SYSTEM_PROMPT
            + cache_instr
            + ctx_instr
        )
        logger.debug("--- DECOMPOSER: using PLAIN prompt path ---")

    # ── Single model call with the correct prompt ────────────────────────────
    response_text = generate_response(system_prompt, goal, model_name=get_model("router"))

    logger.debug(f"--- ROUTER PROMPT ---\n{goal}\n-------------------")
    logger.debug(f"--- ROUTER RESPONSE ---\n{response_text}\n-------------------")

    return response_text


def parse_decision(raw_response: str) -> dict:
    """Parses the JSON response into a dictionary."""
    return parse_llm_json(raw_response)