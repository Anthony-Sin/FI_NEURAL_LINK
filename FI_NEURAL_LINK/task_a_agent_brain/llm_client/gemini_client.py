"""
This module provides a client for interacting with the Google Gemini API.
It requires the GEMINI_API_KEY environment variable to be set.
"""

from dotenv import load_dotenv
import os
import google.generativeai as genai
from google.api_core import exceptions
import logging
from FI_NEURAL_LINK.config_manager import get_model

logger = logging.getLogger("AgentCore")

def generate_response(system_prompt: str, user_message: str, image_data: bytes = None, model_name: str = None) -> str:
    """
    Connects to the Google Gemini API and returns the model's text response.

    Args:
        system_prompt (str): The system prompt to set the context for the model.
        user_message (str): The user message to send to the model.
        image_data (bytes, optional): Optional image bytes for multimodal input.
        model_name (str): The name of the model to use.

    Returns:
        str: The model's text response.

    Raises:
        ValueError: If GEMINI_API_KEY is not set.
        Exception: If there is an error with the API call.
    """
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        raise ValueError("GEMINI_API_KEY environment variable is not set.")

    try:
        genai.configure(api_key=api_key)

        if not model_name:
            model_name = get_model("executor")

        model = genai.GenerativeModel(
            model_name=model_name,
            system_instruction=system_prompt
        )

        content = [user_message]
        if image_data:
            content.append({"mime_type": "image/png", "data": image_data})

        # Log prompt for debugging to both file and dashboard
        logger.debug(f"--- GEMINI API CALL (Model: {model_name}) ---")
        logger.debug(f"SYSTEM: {system_prompt}")
        logger.debug(f"USER: {user_message}")

        response = model.generate_content(content)

        if not response.text:
            raise Exception("The model returned an empty response.")

        return response.text
    except exceptions.GoogleAPICallError as e:
        raise Exception(f"Gemini API call failed: {str(e)}") from e
    except Exception as e:
        raise Exception(f"An unexpected error occurred: {str(e)}") from e
