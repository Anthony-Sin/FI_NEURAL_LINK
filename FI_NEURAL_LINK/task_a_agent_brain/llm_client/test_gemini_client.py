import unittest
from unittest.mock import patch, MagicMock
import os
from FI_NEURAL_LINK.task_a_agent_brain.llm_client.gemini_client import generate_response

class TestGeminiClient(unittest.TestCase):

    @patch.dict(os.environ, {"GEMINI_API_KEY": "test_key"})
    @patch("google.generativeai.configure")
    @patch("google.generativeai.GenerativeModel")
    def test_generate_response_success(self, mock_model_class, mock_configure):
        # Setup mocks
        mock_model_instance = MagicMock()
        mock_model_class.return_value = mock_model_instance
        mock_response = MagicMock()
        mock_response.text = "Mocked Gemini Response"
        mock_model_instance.generate_content.return_value = mock_response

        # Execute
        response = generate_response("System Prompt", "User Message")

        # Verify
        mock_configure.assert_called_once_with(api_key="test_key")
        mock_model_class.assert_called_once_with(
            model_name="gemini-1.5-pro",
            system_instruction="System Prompt"
        )
        mock_model_instance.generate_content.assert_called_once_with(["User Message"])
        self.assertEqual(response, "Mocked Gemini Response")

    @patch.dict(os.environ, {}, clear=True)
    def test_generate_response_no_api_key(self):
        with self.assertRaises(ValueError) as context:
            generate_response("System Prompt", "User Message")
        self.assertIn("GEMINI_API_KEY environment variable is not set.", str(context.exception))

    @patch.dict(os.environ, {"GEMINI_API_KEY": "test_key"})
    @patch("google.generativeai.configure")
    @patch("google.generativeai.GenerativeModel")
    def test_generate_response_api_error(self, mock_model_class, mock_configure):
        # Setup mocks to raise an error
        mock_model_instance = MagicMock()
        mock_model_class.return_value = mock_model_instance
        mock_model_instance.generate_content.side_effect = Exception("API Error")

        # Execute and Verify
        with self.assertRaises(Exception) as context:
            generate_response("System Prompt", "User Message")
        self.assertIn("An unexpected error occurred: API Error", str(context.exception))

if __name__ == "__main__":
    unittest.main()
