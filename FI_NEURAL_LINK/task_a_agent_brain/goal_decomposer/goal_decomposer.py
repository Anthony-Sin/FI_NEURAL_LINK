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
        "If SHORT:\n"
        "- Emit a single JSON object with 'type': 'short', 'description': 'one-line desc', "
        "'tool_hint': 'tool', and 'params': {args}.\n"
        "- Valid tool_hints: click, type, launch, read_screen, analyze_screen, open_url, click_element, type_in_element.\n"
        "- Do not explain, do not reason, do not list next steps.\n\n"
        "If LONG (requires more than one tool call or waiting for UI):\n"
        "- Stop immediately and emit a structured handoff JSON object with 'type': 'long', "
        "'goal': the original goal, 'task_type': 'category', 'payload': [iterable items or empty], "
        "'ui_target': 'main app/window', 'initial_params': {}.\n"
        "- Forbidden from beginning execution or reasoning about steps.\n\n"
        "Return ONLY the valid JSON object."
    )

    response_text = generate_response(system_prompt, goal, model_name="gemini-2.5-flash-lite")

    # Strip potential markdown formatting if the model adds it
    clean_response = response_text.strip()
    if clean_response.startswith("```json"):
        clean_response = clean_response[len("```json"):].strip()
    if clean_response.endswith("```"):
        clean_response = clean_response[:-len("```")].strip()

    try:
        decision = json.loads(clean_response)
        if not isinstance(decision, dict):
            raise ValueError("Expected a JSON object from the model.")
        return decision
    except json.JSONDecodeError as e:
        raise ValueError(f"Failed to parse model response as JSON: {str(e)}\nResponse: {response_text}") from e
