import unittest
from unittest.mock import MagicMock, patch
from FI_NEURAL_LINK.task_a_agent_brain.agent_core import AgentCore

class TestAgentCore(unittest.TestCase):
    @patch("FI_NEURAL_LINK.task_a_agent_brain.agent_core.decompose_goal")
    def test_run_goal_loop_detection(self, mock_decompose):
        mock_decompose.return_value = [
            {"step_id": 1, "description": "repeat", "tool_hint": "click"},
            {"step_id": 2, "description": "repeat", "tool_hint": "click"},
            {"step_id": 3, "description": "repeat", "tool_hint": "click"},
        ]

        config = {"gemini_api_key": "test", "loop_window": 5}
        agent = AgentCore(config)

        with self.assertRaises(RuntimeError) as context:
            agent.run_goal("repeat loop")

        self.assertIn("Loop detected", str(context.exception))

if __name__ == "__main__":
    unittest.main()
