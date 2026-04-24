import unittest
from unittest.mock import patch
import json
from agents.decomposer import route_goal, parse_decision

class TestGoalDecomposer(unittest.TestCase):

    @patch("agents.decomposer.generate_response")
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
        self.assertEqual(result, json.dumps(mock_decision))
        mock_generate_response.assert_called_once()

    @patch("agents.decomposer.generate_response")
    def test_route_goal_with_markdown(self, mock_generate_response):
        # Setup mock with markdown formatting
        mock_decision = {
            "text": "Clicking",
            "function_call": {"name": "click", "args": {"x": 100, "y": 200}}
        }
        raw_val = "```json\n" + json.dumps(mock_decision) + "\n```"
        mock_generate_response.return_value = raw_val

        # Execute
        result = route_goal("Do something")

        # Verify
        self.assertEqual(result, raw_val)

    def test_parse_decision_invalid_json(self):
        # Execute and Verify
        with self.assertRaises(ValueError) as context:
            parse_decision("Not a JSON")
        self.assertIn("Invalid JSON format in LLM response", str(context.exception))

    @patch("agents.decomposer.generate_response")
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
        self.assertEqual(result, json.dumps(mock_decision))

    def test_parse_decision_not_an_object(self):
        # Setup mock returning a list instead of a dict
        raw = json.dumps([{"step": 1}])

        # Execute and Verify
        with self.assertRaises(ValueError) as context:
            parse_decision(raw)
        self.assertIn("LLM response is not a JSON object", str(context.exception))

if __name__ == "__main__":
    unittest.main()
