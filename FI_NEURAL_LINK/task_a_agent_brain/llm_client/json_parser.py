import json
import logging

logger = logging.getLogger("AgentCore")

def clean_json_response(text: str) -> str:
    """Strips markdown formatting from a JSON string."""
    clean = text.strip()
    if clean.startswith("```json"):
        clean = clean[7:].strip()
    elif clean.startswith("```"):
        clean = clean[3:].strip()
    if clean.endswith("```"):
        clean = clean[:-3].strip()
    return clean

def parse_llm_json(text: str) -> dict:
    """Cleans and parses a JSON string from an LLM response."""
    cleaned = clean_json_response(text)
    try:
        data = json.loads(cleaned)
        if not isinstance(data, dict):
            raise ValueError("LLM response is not a JSON object")
        return data
    except json.JSONDecodeError as e:
        logger.error(f"Failed to parse LLM JSON: {str(e)}\nRaw text: {text}")
        raise ValueError(f"Invalid JSON format in LLM response: {str(e)}") from e
