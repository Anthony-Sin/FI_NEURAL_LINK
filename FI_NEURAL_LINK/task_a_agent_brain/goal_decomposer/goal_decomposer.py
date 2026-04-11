import json
from ..llm_client.gemini_client import generate_response
from FI_NEURAL_LINK.config_manager import get_model

def route_goal(goal: str) -> dict:
    """
    Acts as a Router Brain using Gemini Flash Lite.
    Classifies the goal as 'short' or 'long' and dispatches accordingly.
    """
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
        "Valid functions: click, type_text, launch_app, read_screen, analyze_screen, open_url, click_element, type_in_element, wait, save_webpage_structure, smart_web_action.\n"
        "CRITICAL: Always insert a dynamic 'wait' step after 'launch_app' or 'open_url' (estimate seconds based on likely load time) before any follow-up UI action.\n"
        "When 'heading over' to a URL, you MUST always call 'save_webpage_structure' after opening it.\n"
        "For complex tasks like 'type X into the search bar', use 'smart_web_action' which combines scraping and element discovery. "
        "Signature: smart_web_action(url: str, instruction: str). "
        "The instruction must be specific: e.g., 'type explain how you work into the search bar'.\n"
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

    response_text = generate_response(system_prompt, goal, model_name=get_model("router"))

    # Strip potential markdown formatting if the model adds it
    clean_response = response_text.strip()
    if clean_response.startswith("```json"):
        clean_response = clean_response[7:].strip()
    if clean_response.endswith("```"):
        clean_response = clean_response[:-3].strip()

    # Raw response is handled by AgentCore for logging
    return clean_response

def parse_decision(clean_response: str) -> dict:
    """Parses the cleaned JSON response into a dictionary."""
    try:
        decision = json.loads(clean_response)
        if not isinstance(decision, dict):
            raise ValueError("Expected a JSON object from the model.")
        return decision
    except json.JSONDecodeError as e:
        raise ValueError(f"Failed to parse model response as JSON: {str(e)}\nResponse: {clean_response}") from e
