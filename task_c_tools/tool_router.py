"""
This module routes action requests to the appropriate tool functions.
It incorporates rate limiting and supports actions from mouse_keyboard, windows_control, and launcher modules.
"""

from task_c_tools.pyautogui_wrapper import mouse_keyboard
from task_c_tools.pywinauto_wrapper import windows_control
from task_c_tools import launcher
from task_c_tools.safety.rate_limiter import DEFAULT_LIMITER

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
            "find_window": windows_control.find_window,
            "click_element": windows_control.click_element,
            "type_in_element": windows_control.type_in_element,
            "get_window_text": windows_control.get_window_text
        }

    def execute(self, action: str, params: dict) -> dict:
        """
        Executes the specified action with the provided parameters if rate limits allow.
        """
        if not DEFAULT_LIMITER.is_allowed():
            return {"ok": False, "result": "Rate limit exceeded"}

        func = self.actions.get(action)
        if not func:
            return {"ok": False, "result": f"Unknown action: {action}"}

        try:
            DEFAULT_LIMITER.record_call()
            # Unpack params as keyword arguments
            return func(**params)
        except Exception as e:
            return {"ok": False, "result": str(e)}
