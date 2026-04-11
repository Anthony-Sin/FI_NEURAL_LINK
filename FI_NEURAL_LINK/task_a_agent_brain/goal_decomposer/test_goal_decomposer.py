import unittest
from unittest.mock import patch
import json
from FI_NEURAL_LINK.task_a_agent_brain.goal_decomposer.goal_decomposer import decompose_goal

class TestGoalDecomposer(unittest.TestCase):

    @patch("FI_NEURAL_LINK.task_a_agent_brain.goal_decomposer.goal_decomposer.generate_response")
    def test_decompose_goal_success(self, mock_generate_response):
        # Setup mock
        mock_steps = [
            {"step_id": 1, "description": "Open browser", "tool_hint": "launch"},
            {"step_id": 2, "description": "Go to google.com", "tool_hint": "open_url"}
        ]
        mock_generate_response.return_value = json.dumps(mock_steps)

        # Execute
        result = decompose_goal("Open Google")

        # Verify
        self.assertEqual(result, mock_steps)
        mock_generate_response.assert_called_once()

    @patch("FI_NEURAL_LINK.task_a_agent_brain.goal_decomposer.goal_decomposer.generate_response")
    def test_decompose_goal_with_markdown(self, mock_generate_response):
        # Setup mock with markdown formatting
        mock_steps = [
            {"step_id": 1, "description": "Step 1", "tool_hint": "click"}
        ]
        mock_generate_response.return_value = "```json\n" + json.dumps(mock_steps) + "\n```"

        # Execute
        result = decompose_goal("Do something")

        # Verify
        self.assertEqual(result, mock_steps)

    @patch("FI_NEURAL_LINK.task_a_agent_brain.goal_decomposer.goal_decomposer.generate_response")
    def test_decompose_goal_invalid_json(self, mock_generate_response):
        # Setup mock with invalid JSON
        mock_generate_response.return_value = "Not a JSON"

        # Execute and Verify
        with self.assertRaises(ValueError) as context:
            decompose_goal("Invalid goal")
        self.assertIn("Failed to parse model response as JSON", str(context.exception))

    @patch("FI_NEURAL_LINK.task_a_agent_brain.goal_decomposer.goal_decomposer.generate_response")
    def test_decompose_goal_not_a_list(self, mock_generate_response):
        # Setup mock returning a dict instead of a list
        mock_generate_response.return_value = json.dumps({"step": 1})

        # Execute and Verify
        with self.assertRaises(ValueError) as context:
            decompose_goal("Invalid goal")
        self.assertIn("Expected a list of steps from the model.", str(context.exception))

if __name__ == "__main__":
    unittest.main()
