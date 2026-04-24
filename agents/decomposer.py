import json
from services.llm_client import generate_response
from utils.json_parser import parse_llm_json
from core.config import get_model

def route_goal(goal: str, cache_block: str = "", context_block: str = "") -> str:
    """
    Acts as a Router Brain using Gemini Flash Lite.
    Classifies the goal as 'short' or 'long' and dispatches accordingly.
    """
    cache_instr = f"\n\n{cache_block}\nUse the CACHE if it matches the current goal exactly." if cache_block else ""
    ctx_instr = f"\n\n{context_block}\nCONTEXTUAL AWARENESS: Prefer the 'Active Window' for actions. If a recording is present, use it as a template for 'same action' or 'replay' requests." if context_block else ""

    system_prompt = (
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
        "Valid functions: click, type_text, launch_app, read_screen, analyze_screen, open_url, click_element, type_in_element, wait, save_webpage_structure, smart_web_action, drag_and_drop.\n"
        "- click_element(window_title, control_title)\n"
        "- type_in_element(window_title, control_title, text)\n"
        "- drag_and_drop(start_x, start_y, end_x, end_y)\n"
        "CRITICAL: Always insert a dynamic 'wait' step after 'launch_app' or 'open_url' (estimate seconds based on likely load time) before any follow-up UI action.\n"
        "When launching a browser (msedge.exe or chrome.exe), ALWAYS include the \"--new-window\" flag in the 'args' list to ensure a clean workspace. If the user provides a URL, append it to the args list after the flag.\n"
        "When 'heading over' to a URL, you MUST always call 'save_webpage_structure' after opening it to ensure the local knowledge base is updated.\n"
        "LOGIN AWARENESS: Many sites (Gmail, AI Studio) may already be logged in. "
        "Before typing credentials, check if the page is already at the dashboard or inbox. If so, SKIP typing and proceed to the next relevant action.\n"
        "For complex tasks like 'type X into the search bar', ALWAYS prefer 'smart_web_action' which combines scraping and element discovery. "
        "Signature: smart_web_action(url_domain: str, instruction: str, expected_title_re: str).\n"
        "STRICT RULE: Each 'smart_web_action' must perform exactly ONE atomic UI interaction. "
        "Combining multiple steps (e.g., 'type something AND click start') into a single smart_web_action is FORBIDDEN. "
        "If a goal requires multiple steps, you MUST emit a list of separate function_calls. "
        "Correct: [{'name': 'smart_web_action', 'args': {'instruction': 'type hello'}}, {'name': 'smart_web_action', 'args': {'instruction': 'click search'}}] "
        "Incorrect: [{'name': 'smart_web_action', 'args': {'instruction': 'type hello and click search'}}]\n"
        "REPETITION: If the user asks to repeat an action multiple times (e.g., 'do X 10 times'), you MUST expand the list of function_calls to include all repetitions.\n"
        "RECORDING: If the user asks to 'repeat my recording' or 'do the recorded task', emit a JSON with \"task_type\": \"replay_recording\" and \"repeat_count\": X.\n"
        "If a recording context is provided, you should treat it as the 'template' for the current goal. If the user says 'do the same but with X', use the elements and actions from the recording but modify the 'text' or 'instruction' parameter accordingly. DO NOT open new windows if the recording or active window already shows the target application.\n"
        "The instruction must be highly specific, referencing element IDs or names from your mental model of the structure if possible: e.g., 'type explain how you work into the email input field with id identifierId'.\n"
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
        f"{cache_instr}"
        f"{ctx_instr}"
    )

    response_text = generate_response(system_prompt, goal, model_name=get_model("router"))

    # Log the prompt and response for debugging
    import logging
    logger = logging.getLogger("AgentCore")
    logger.debug(f"--- ROUTER PROMPT ---\n{goal}\n-------------------")
    logger.debug(f"--- ROUTER RESPONSE ---\n{response_text}\n-------------------")

    # Raw response text is returned for logging
    return response_text

def parse_decision(raw_response: str) -> dict:
    """Parses the JSON response into a dictionary."""
    return parse_llm_json(raw_response)
