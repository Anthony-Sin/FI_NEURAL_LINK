"""
This module provides a unified interface for pywinauto window and control operations.
Every function in this module returns a dictionary with the following format:
{
    "ok": bool,      # True if the operation was successful, False otherwise.
    "result": str    # A descriptive message of the outcome or the error encountered.
}

If the global STOP_EVENT from FI_NEURAL_LINK.task_b_dashboard.panels.stop_panel is set,
all operations will be halted and return an error status.
"""

from typing import Dict, Union
from pywinauto import Desktop
from FI_NEURAL_LINK.task_b_dashboard.panels.stop_panel import STOP_EVENT

def find_window(title_regex: str) -> Dict[str, Union[bool, str]]:
    """
    Find a window matching the given title regex.
    Returns a success dict if at least one window is found.
    """
    if STOP_EVENT.is_set():
        return {"ok": False, "result": "Halted by STOP_EVENT"}
    try:
        windows = Desktop(backend="uia").windows(title_re=title_regex)
        if windows:
            return {"ok": True, "result": f"Found {len(windows)} window(s) matching '{title_regex}'"}
        else:
            return {"ok": False, "result": f"No window found matching '{title_regex}'"}
    except Exception as e:
        return {"ok": False, "result": str(e)}

def click_element(window_title: str, control_title: str) -> Dict[str, Union[bool, str]]:
    """
    Find a window by title and click a control within it by its title.
    """
    if STOP_EVENT.is_set():
        return {"ok": False, "result": "Halted by STOP_EVENT"}
    try:
        # Use regex for title finding
        desktop = Desktop(backend="uia")
        win = desktop.window(title_re=window_title)

        # Wait for window and bring to front
        win.wait('ready', timeout=10)
        win.set_focus()

        # Find element with auto_id, name, or title
        ctrl = win.child_window(title=control_title, control_type="Button")
        if not ctrl.exists():
            ctrl = win.child_window(title=control_title)

        ctrl.click_input()
        return {"ok": True, "result": f"Clicked element '{control_title}' in window '{window_title}'"}
    except Exception as e:
        return {"ok": False, "result": str(e)}

def type_in_element(window_title: str, control_title: str, text: str) -> Dict[str, Union[bool, str]]:
    """
    Find a window by title and type text into a control within it by its title.
    """
    if STOP_EVENT.is_set():
        return {"ok": False, "result": "Halted by STOP_EVENT"}
    try:
        desktop = Desktop(backend="uia")
        win = desktop.window(title_re=window_title)

        # Wait for window and bring to front
        win.wait('ready', timeout=10)
        win.set_focus()

        # Find element
        ctrl = win.child_window(title=control_title, control_type="Edit")
        if not ctrl.exists():
            ctrl = win.child_window(title=control_title)

        ctrl.type_keys(text, with_spaces=True, click_before=True)
        return {"ok": True, "result": f"Typed '{text}' into element '{control_title}' in window '{window_title}'"}
    except Exception as e:
        return {"ok": False, "result": str(e)}

def get_window_text(window_title: str) -> Dict[str, Union[bool, str]]:
    """
    Find a window by title and return its texts.
    """
    if STOP_EVENT.is_set():
        return {"ok": False, "result": "Halted by STOP_EVENT"}
    try:
        app = Desktop(backend="uia").window(title=window_title)
        texts = app.texts()
        return {"ok": True, "result": str(texts)}
    except Exception as e:
        return {"ok": False, "result": str(e)}
