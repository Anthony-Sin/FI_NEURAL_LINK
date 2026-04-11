import json
from ..llm_client.gemini_client import generate_response

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
        "Emit a JSON object exactly like this:\n"
        "{\n"
        "  \"text\": \"I will open Chrome and go to Google.\",\n"
        "  \"function_call\": {\n"
        "    \"name\": \"launch_app\",\n"
        "    \"args\": { \"path\": \"chrome.exe\", \"args\": [\"https://google.com\"] }\n"
        "  }\n"
        "}\n"
        "Valid functions: click, type_text, launch_app, read_screen, analyze_screen, open_url, click_element, type_in_element, wait.\n"
        "To open a browser to a specific URL in one step, use 'launch_app' with the URL in 'args'. "
        "Use 'open_url' only if the browser is already known to be open.\n"
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

    response_text = generate_response(system_prompt, goal, model_name="gemini-2.5-flash-lite")

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
