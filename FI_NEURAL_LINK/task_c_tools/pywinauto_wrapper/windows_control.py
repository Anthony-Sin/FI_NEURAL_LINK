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

def _find_element(win, identifier: str, control_types: list = None):
    """Internal helper to find an element by multiple strategies."""
    if control_types is None:
        control_types = ["Button", "Edit", "Text", "ListItem", "MenuItem", "Hyperlink"]

    # Strategy 1: exact title/name/auto_id with type constraint
    for c_type in control_types:
        for attr in ['title', 'auto_id', 'control_id', 'best_match']:
            try:
                kwargs = {attr: identifier, 'control_type': c_type}
                ctrl = win.child_window(**kwargs)
                if ctrl.exists(timeout=1):
                    return ctrl
            except: continue

    # Strategy 2: exact identifier without type constraint
    for attr in ['title', 'auto_id', 'control_id', 'best_match']:
        try:
            kwargs = {attr: identifier}
            ctrl = win.child_window(**kwargs)
            if ctrl.exists(timeout=1):
                return ctrl
        except: continue

    # Strategy 3: Regex match
    try:
        ctrl = win.child_window(title_re=f".*{identifier}.*")
        if ctrl.exists(timeout=1):
            return ctrl
    except: pass

    return None

def click_element(window_title: str, control_title: str) -> Dict[str, Union[bool, str]]:
    """
    Find a window by title and click a control within it using multiple discovery strategies.
    """
    if STOP_EVENT.is_set():
        return {"ok": False, "result": "Halted by STOP_EVENT"}
    try:
        desktop = Desktop(backend="uia")
        # Be loose with window matching
        win = desktop.window(title_re=f".*{window_title}.*")

        win.wait('ready', timeout=10)
        win.set_focus()

        ctrl = _find_element(win, control_title, ["Button", "Hyperlink", "Text"])
        if ctrl:
            ctrl.click_input()
            return {"ok": True, "result": f"Clicked element '{control_title}'"}

        return {"ok": False, "result": f"Could not find element '{control_title}' in '{window_title}'"}
    except Exception as e:
        return {"ok": False, "result": str(e)}

def type_in_element(window_title: str, control_title: str, text: str) -> Dict[str, Union[bool, str]]:
    """
    Find a window by title and type text into a control within it using multiple discovery strategies.
    """
    if STOP_EVENT.is_set():
        return {"ok": False, "result": "Halted by STOP_EVENT"}
    try:
        desktop = Desktop(backend="uia")
        win = desktop.window(title_re=f".*{window_title}.*")

        win.wait('ready', timeout=10)
        win.set_focus()

        ctrl = _find_element(win, control_title, ["Edit", "Document", "Text"])
        if ctrl:
            ctrl.type_keys(text, with_spaces=True, click_before=True)
            return {"ok": True, "result": f"Typed '{text}' into '{control_title}'"}

        return {"ok": False, "result": f"Could not find input element '{control_title}'"}
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
