"""
This module routes action requests to the appropriate tool functions.
It incorporates rate limiting and supports actions from mouse_keyboard, windows_control, and launcher modules.
"""

from FI_NEURAL_LINK.task_c_tools.pyautogui_wrapper import mouse_keyboard
from FI_NEURAL_LINK.task_c_tools.pywinauto_wrapper import windows_control
from FI_NEURAL_LINK.task_c_tools import launcher, vision
from FI_NEURAL_LINK.task_c_tools.safety.rate_limiter import DEFAULT_LIMITER
from FI_NEURAL_LINK.task_b_dashboard.panels.stop_panel import STOP_EVENT

class ToolRouter:
    def __init__(self):
        # Action mapping
        self.actions = {
            "click": mouse_keyboard.click,
            "double_click": mouse_keyboard.double_click,
            "right_click": mouse_keyboard.right_click,
            "type_text": mouse_keyboard.type_text,
            "press_key": mouse_keyboard.press_key,
            "hotkey": mouse_keyboard.hotkey,
            "move_to": mouse_keyboard.move_to,
            "scroll": mouse_keyboard.scroll,
            "open_url": launcher.open_url,
            "launch_app": launcher.launch_app,
            "kill_process": launcher.kill_process,
            "wait": launcher.wait,
            "find_window": windows_control.find_window,
            "click_element": windows_control.click_element,
            "type_in_element": windows_control.type_in_element,
            "get_window_text": windows_control.get_window_text,
            "read_screen": vision.read_screen,
            "analyze_screen": vision.analyze_screen
        }

    def execute(self, action: str, params: dict) -> dict:
        """
        Executes the specified action with the provided parameters if rate limits allow and STOP_EVENT is not set.
        """
        if STOP_EVENT.is_set():
            return {"ok": False, "result": "Halted by STOP_EVENT"}

        if not DEFAULT_LIMITER.is_allowed():
            return {"ok": False, "result": "Rate limit exceeded"}

        func = self.actions.get(action)
        if not func:
            # Try to see if it's an alias or if tool_hint was used instead of exact action name
            # For example 'launch' instead of 'launch_app'
            if action == "launch":
                func = self.actions.get("launch_app")
            elif action == "type":
                func = self.actions.get("type_text")
            elif action == "timer":
                func = self.actions.get("wait")

        if not func:
            return {"ok": False, "result": f"Unknown action: {action}"}

        try:
            DEFAULT_LIMITER.record_call()
            # Unpack params as keyword arguments
            return func(**params)
        except Exception as e:
            return {"ok": False, "result": str(e)}
