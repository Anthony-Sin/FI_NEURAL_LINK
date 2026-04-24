"""
This module provides a client for interacting with the Google Gemini API.
It requires the GEMINI_API_KEY environment variable to be set.
"""

import os
import google.generativeai as genai
from google.api_core import exceptions
import logging
from core.config import get_model

logger = logging.getLogger("AgentCore")

def request_user_input(prompt_text: str) -> str:
    """
    Asks the user for input via the terminal as a fallback.
    In a GUI environment, the Dashboard overrides this or provides a way to capture it.
    """
    print(f"\n[USER INTERVENTION REQUIRED]: {prompt_text}")
    try:
        return input("> ")
    except EOFError:
        return "exit"

def generate_response(system_prompt: str, user_message: str, image_data: bytes = None, model_name: str = None) -> str:
    """
    Connects to the Google Gemini API and returns the model's text response.
    Includes built-in retry logic for transient errors.
    """
    import time
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        raise ValueError("GEMINI_API_KEY environment variable is not set.")

    max_retries = 3
    base_delay = 2

    for attempt in range(max_retries):
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

            # Log prompt for debugging
            logger.debug(f"--- GEMINI API CALL (Model: {model_name}, Attempt: {attempt+1}) ---")
            logger.debug(f"SYSTEM PROMPT:\n{system_prompt}")
            logger.debug(f"USER MESSAGE:\n{user_message}")
            if image_data:
                logger.debug("IMAGE DATA: [Image provided]")

            response = model.generate_content(content)

            if not response.text:
                raise Exception("The model returned an empty response.")

            return response.text

        except (exceptions.GoogleAPICallError, exceptions.RetryError) as e:
            if attempt == max_retries - 1:
                raise Exception(f"Gemini API call failed after {max_retries} attempts: {str(e)}") from e

            # Exponential backoff
            sleep_time = base_delay * (2 ** attempt)
            logger.warning(f"Gemini API transient error: {str(e)}. Retrying in {sleep_time}s...")
            time.sleep(sleep_time)

        except Exception as e:
            # Re-raise non-transient errors immediately
            raise Exception(f"An unexpected error occurred: {str(e)}") from e
