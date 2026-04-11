"""
This module provides a unified interface for pywinauto window and control operations.
Every function in this module returns a dictionary with the following format:
{
    "ok": bool,      # True if the operation was successful, False otherwise.
    "result": str    # A descriptive message of the outcome or the error encountered.
}

If the global STOP_EVENT from task_b_dashboard.panels.stop_panel is set,
all operations will be halted and return an error status.
"""

from typing import Dict, Union
from pywinauto import Desktop
from task_b_dashboard.panels.stop_panel import STOP_EVENT

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
        app = Desktop(backend="uia").window(title=window_title)
        app.child_window(title=control_title).click_input()
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
        app = Desktop(backend="uia").window(title=window_title)
        app.child_window(title=control_title).type_keys(text, with_spaces=True)
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
