import unittest
import json
from unittest.mock import MagicMock, patch
from agents.agent import AgentCore

class TestAgentCore(unittest.TestCase):
    @patch("agents.agent.route_goal")
    @patch("agents.agent.generate_response")
    def test_run_goal_short_task(self, mock_generate, mock_route):
        mock_route.return_value = json.dumps({
            "text": "test",
            "function_call": {"name": "click", "args": {"x": 1, "y": 2}}
        })

        config = {"gemini_api_key": "test"}
        tool_router = MagicMock()
        agent = AgentCore(config, tool_router=tool_router)

        agent.run_goal("short goal")
        tool_router.execute.assert_called_once_with("click", {"x": 1, "y": 2})

    @patch("agents.agent.route_goal")
    @patch("agents.agent.generate_response")
    def test_run_goal_long_task_termination(self, mock_generate, mock_route):
        mock_route.return_value = json.dumps({
            "task_type": "long",
            "goal": "test goal",
            "ui_target": "test",
            "iterable_payload": [],
            "parameters": {}
        })
        mock_generate.return_value = json.dumps({"status": "terminated"})

        config = {"gemini_api_key": "test"}
        agent = AgentCore(config)

        results = agent.run_goal("long goal")
        self.assertEqual(results, [])
        mock_generate.assert_called_once()

if __name__ == "__main__":
    unittest.main()
