import os
import re
from .goal_decomposer.goal_decomposer import decompose_goal
from .loop_guard import LoopGuard
from FI_NEURAL_LINK.task_b_dashboard.panels.stop_panel import STOP_EVENT

class AgentCore:
    """
    Core agent class that manages goal decomposition and execution with loop protection.
    """

    def __init__(self, config: dict, tool_router=None, log_callback=None):
        """
        Initializes the AgentCore.

        Args:
            config (dict): Configuration containing:
                - gemini_api_key (str): The API key for Gemini.
                - max_retries (int): Maximum number of retries for actions.
                - loop_window (int): The window size for loop detection.
            tool_router (ToolRouter, optional): The tool router to execute actions.
            log_callback (callable, optional): A callback function for logging.
        """
        self.config = config
        os.environ["GEMINI_API_KEY"] = config.get("gemini_api_key", "")
        self.loop_guard = LoopGuard(n=config.get("loop_window", 5))
        self.tool_router = tool_router
        self.log_callback = log_callback

    def log(self, text, level="info"):
        if self.log_callback:
            self.log_callback(text, level)
        else:
            print(f"[{level.upper()}] {text}")

    def _extract_params(self, tool_hint: str, description: str) -> dict:
        """
        Heuristic-based parameter extraction from action description.
        """
        params = {}
        if tool_hint == "open_url":
            # Extract URL
            url_match = re.search(r'https?://[^\s]+', description)
            if url_match:
                params["url"] = url_match.group(0)
            else:
                # Fallback: look for something that looks like a domain
                domain_match = re.search(r'[a-zA-Z0-9.-]+\.[a-z]{2,}', description)
                if domain_match:
                    params["url"] = "https://" + domain_match.group(0)

        elif tool_hint in ["launch", "launch_app"]:
            # Extract path (very crude)
            params["path"] = description.replace("Launch ", "").replace("launch ", "").strip()
            params["args"] = []

        elif tool_hint in ["type", "type_text"]:
            # Extract text (often inside quotes)
            text_match = re.search(r'["\'](.*?)["\']', description)
            if text_match:
                params["text"] = text_match.group(1)
            else:
                params["text"] = description.replace("Type ", "").replace("type ", "").strip()

        elif tool_hint == "click":
            # Extract coordinates if present
            coord_match = re.search(r'(\d+)\s*,\s*(\d+)', description)
            if coord_match:
                params["x"] = int(coord_match.group(1))
                params["y"] = int(coord_match.group(2))
            else:
                # Default to current position or something safe
                params["x"] = 0
                params["y"] = 0

        return params

    def run_goal(self, goal: str) -> list:
        """
        Decomposes a goal into steps and executes them, checking for loops and STOP_EVENT.

        Args:
            goal (str): The high-level goal to achieve.

        Returns:
            list: A list of result dictionaries for each executed step.

        Raises:
            RuntimeError: If a repetitive loop is detected or if halted by STOP_EVENT.
        """
        self.log(f"Starting goal: {goal}")
        try:
            steps = decompose_goal(goal)
        except Exception as e:
            self.log(f"Decomposition failed: {str(e)}", "error")
            return []

        results = []

        for step in steps:
            if STOP_EVENT.is_set():
                self.log("Emergency stop detected. Halting execution.", "error")
                break

            action_desc = step.get("description", "")
            tool_hint = step.get("tool_hint", "")
            step_id = step.get("step_id")

            self.log(f"Executing step {step_id}: {action_desc} (Tool: {tool_hint})")

            # Check for loops before executing
            if self.loop_guard.check_loop(action_desc):
                error_msg = f"Loop detected — agent halted. Last action: {action_desc}"
                self.log(error_msg, "error")
                raise RuntimeError(error_msg)

            # Record the action
            self.loop_guard.record_action(action_desc)

            result = {
                "step_id": step_id,
                "description": action_desc,
                "tool_used": tool_hint,
                "status": "skipped",
                "result": "No tool router available"
            }

            if self.tool_router:
                params = self._extract_params(tool_hint, action_desc)

                tool_result = self.tool_router.execute(tool_hint, params)
                result["status"] = "completed" if tool_result.get("ok") else "failed"
                result["result"] = tool_result.get("result", "")

                if not tool_result.get("ok"):
                    self.log(f"Step {step_id} failed: {result['result']}", "error")
                else:
                    self.log(f"Step {step_id} completed: {result['result']}")
            else:
                self.log(f"Step {step_id} skipped: No tool router", "warning")

            results.append(result)

            if result["status"] == "failed":
                self.log("Stopping execution due to step failure.", "error")
                break

        self.log("Goal execution finished.")
        return results
