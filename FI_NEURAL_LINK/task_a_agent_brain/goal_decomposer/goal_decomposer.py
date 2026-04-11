import json
from ..llm_client.gemini_client import generate_response

def decompose_goal(goal: str) -> list[dict]:
    """
    Accepts a plain-English goal and decomposes it into a JSON list of action steps
    using the Gemini LLM.

    Args:
        goal (str): The user's goal in plain English.

    Returns:
        list[dict]: A list of dictionaries representing discrete action steps.

    Raises:
        ValueError: If the model's response is not valid JSON.
    """
    system_prompt = (
        "You are a goal decomposition assistant. Your task is to break down a "
        "user's goal into a sequence of discrete action steps. "
        "Each step must be represented as a JSON object with the following keys:\n"
        "- 'step_id': A unique identifier for the step (e.g., 1, 2, 3).\n"
        "- 'description': A clear description of what needs to be done in this step.\n"
        "- 'tool_hint': The primary tool required for this step. It MUST be one of: "
        "click, type, launch, read_screen, open_url.\n\n"
        "Return ONLY a valid JSON list of these objects."
    )

    response_text = generate_response(system_prompt, goal)

    # Strip potential markdown formatting if the model adds it
    clean_response = response_text.strip()
    if clean_response.startswith("```json"):
        clean_response = clean_response[len("```json"):].strip()
    if clean_response.endswith("```"):
        clean_response = clean_response[:-len("```")].strip()

    try:
        steps = json.loads(clean_response)
        if not isinstance(steps, list):
            raise ValueError("Expected a list of steps from the model.")
        return steps
    except json.JSONDecodeError as e:
        raise ValueError(f"Failed to parse model response as JSON: {str(e)}\nResponse: {response_text}") from e
