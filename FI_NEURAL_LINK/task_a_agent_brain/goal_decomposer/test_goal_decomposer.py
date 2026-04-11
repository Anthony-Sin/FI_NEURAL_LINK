import unittest
from unittest.mock import patch
import json
from FI_NEURAL_LINK.task_a_agent_brain.goal_decomposer.goal_decomposer import route_goal

class TestGoalDecomposer(unittest.TestCase):

    @patch("FI_NEURAL_LINK.task_a_agent_brain.goal_decomposer.goal_decomposer.generate_response")
    def test_route_goal_success(self, mock_generate_response):
        # Setup mock
        mock_decision = {
            "text": "Open browser",
            "function_call": {"name": "launch_app", "args": {"path": "chrome.exe"}}
        }
        mock_generate_response.return_value = json.dumps(mock_decision)

        # Execute
        result = route_goal("Open Google")

        # Verify
        self.assertEqual(result, mock_decision)
        mock_generate_response.assert_called_once()

    @patch("FI_NEURAL_LINK.task_a_agent_brain.goal_decomposer.goal_decomposer.generate_response")
    def test_route_goal_with_markdown(self, mock_generate_response):
        # Setup mock with markdown formatting
        mock_decision = {
            "text": "Clicking",
            "function_call": {"name": "click", "args": {"x": 100, "y": 200}}
        }
        mock_generate_response.return_value = "```json\n" + json.dumps(mock_decision) + "\n```"

        # Execute
        result = route_goal("Do something")

        # Verify
        self.assertEqual(result, mock_decision)

    @patch("FI_NEURAL_LINK.task_a_agent_brain.goal_decomposer.goal_decomposer.generate_response")
    def test_route_goal_invalid_json(self, mock_generate_response):
        # Setup mock with invalid JSON
        mock_generate_response.return_value = "Not a JSON"

        # Execute and Verify
        with self.assertRaises(ValueError) as context:
            route_goal("Invalid goal")
        self.assertIn("Failed to parse model response as JSON", str(context.exception))

    @patch("FI_NEURAL_LINK.task_a_agent_brain.goal_decomposer.goal_decomposer.generate_response")
    def test_route_goal_long_handoff(self, mock_generate_response):
        # Setup mock
        mock_decision = {
            "task_type": "long",
            "goal": "multi step goal",
            "ui_target": "browser",
            "iterable_payload": ["item1"],
            "parameters": {}
        }
        mock_generate_response.return_value = json.dumps(mock_decision)

        # Execute
        result = route_goal("Long goal")

        # Verify
        self.assertEqual(result, mock_decision)

    @patch("FI_NEURAL_LINK.task_a_agent_brain.goal_decomposer.goal_decomposer.generate_response")
    def test_route_goal_not_an_object(self, mock_generate_response):
        # Setup mock returning a list instead of a dict
        mock_generate_response.return_value = json.dumps([{"step": 1}])

        # Execute and Verify
        with self.assertRaises(ValueError) as context:
            route_goal("Invalid goal")
        self.assertIn("Expected a JSON object from the model.", str(context.exception))

if __name__ == "__main__":
    unittest.main()
