import os
from .goal_decomposer.goal_decomposer import decompose_goal
from .loop_guard import LoopGuard

class AgentCore:
    """
    Core agent class that manages goal decomposition and execution with loop protection.
    """

    def __init__(self, config: dict):
        """
        Initializes the AgentCore.

        Args:
            config (dict): Configuration containing:
                - gemini_api_key (str): The API key for Gemini.
                - max_retries (int): Maximum number of retries for actions.
                - loop_window (int): The window size for loop detection.
        """
        self.config = config
        os.environ["GEMINI_API_KEY"] = config.get("gemini_api_key", "")
        self.loop_guard = LoopGuard(n=config.get("loop_window", 5))

    def run_goal(self, goal: str) -> list:
        """
        Decomposes a goal into steps and executes them, checking for loops.

        Args:
            goal (str): The high-level goal to achieve.

        Returns:
            list: A list of result dictionaries for each executed step.

        Raises:
            RuntimeError: If a repetitive loop is detected.
        """
        steps = decompose_goal(goal)
        results = []

        for step in steps:
            action = step.get("description", "")

            # Check for loops before executing
            if self.loop_guard.check_loop(action):
                raise RuntimeError(f"Loop detected — agent halted. Last action: {action}")

            # Record the action
            self.loop_guard.record_action(action)

            # Mock execution result
            result = {
                "step_id": step.get("step_id"),
                "description": action,
                "status": "completed",
                "tool_used": step.get("tool_hint")
            }
            results.append(result)

        return results
