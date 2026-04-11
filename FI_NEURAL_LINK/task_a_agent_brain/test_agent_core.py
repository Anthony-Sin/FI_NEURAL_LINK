import unittest
import json
from unittest.mock import MagicMock, patch
from FI_NEURAL_LINK.task_a_agent_brain.agent_core import AgentCore

class TestAgentCore(unittest.TestCase):
    @patch("FI_NEURAL_LINK.task_a_agent_brain.agent_core.route_goal")
    @patch("FI_NEURAL_LINK.task_a_agent_brain.agent_core.generate_response")
    def test_run_goal_short_task(self, mock_generate, mock_route):
        mock_route.return_value = {"type": "short", "description": "test", "tool_hint": "click", "params": {"x": 1, "y": 2}}

        config = {"gemini_api_key": "test"}
        tool_router = MagicMock()
        agent = AgentCore(config, tool_router=tool_router)

        agent.run_goal("short goal")
        tool_router.execute.assert_called_once_with("click", {"x": 1, "y": 2})

    @patch("FI_NEURAL_LINK.task_a_agent_brain.agent_core.route_goal")
    @patch("FI_NEURAL_LINK.task_a_agent_brain.agent_core.generate_response")
    def test_run_goal_long_task_termination(self, mock_generate, mock_route):
        mock_route.return_value = {"type": "long", "goal": "test goal", "payload": []}
        mock_generate.return_value = json.dumps({"status": "terminated"})

        config = {"gemini_api_key": "test"}
        agent = AgentCore(config)

        results = agent.run_goal("long goal")
        self.assertEqual(results, [])
        mock_generate.assert_called_once()

if __name__ == "__main__":
    unittest.main()
