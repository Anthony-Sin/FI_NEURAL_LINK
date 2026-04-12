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
        control_types = ["Button", "Edit", "Text", "ListItem", "MenuItem", "Hyperlink", "Document"]

    # Strategy 1: exact title/name/auto_id with type constraint
    for c_type in control_types:
        for attr in ['title', 'auto_id', 'control_id', 'best_match', 'name']:
            try:
                kwargs = {attr: identifier, 'control_type': c_type}
                ctrl = win.child_window(**kwargs)
                if ctrl.exists(timeout=1):
                    return ctrl
            except: continue

    # Strategy 2: exact identifier without type constraint
    for attr in ['title', 'auto_id', 'control_id', 'best_match', 'name']:
        try:
            kwargs = {attr: identifier}
            ctrl = win.child_window(**kwargs)
            if ctrl.exists(timeout=1):
                return ctrl
        except: continue

    # Strategy 3: Regex match on title/name
    try:
        ctrl = win.child_window(title_re=f".*{identifier}.*")
        if ctrl.exists(timeout=1):
            return ctrl
    except: pass

    try:
        ctrl = win.child_window(name_re=f".*{identifier}.*")
        if ctrl.exists(timeout=1):
            return ctrl
    except: pass

    # Strategy 4: Search in descendants (expensive but thorough)
    try:
        for child in win.descendants():
            if identifier in [child.window_text(), child.element_info.name, child.element_info.automation_id]:
                if control_types and child.element_info.control_type not in control_types:
                    continue
                return child
    except: pass

    return None

def _get_window(window_title_re: str):
    """Internal helper to find a window with fallbacks."""
    desktop = Desktop(backend="uia")

    # Strategy 1: Direct match
    try:
        win = desktop.window(title_re=window_title_re)
        if win.exists(timeout=2):
            return win
    except: pass

    # Strategy 2: If it looks like a domain, try common browser suffixes
    if "." in window_title_re:
        clean_domain = window_title_re.replace(".*", "")
        fallbacks = [
            f".*{clean_domain}.*",
            f".*Microsoft Edge.*",
            f".*Google Chrome.*"
        ]
        for fb in fallbacks:
            try:
                win = desktop.window(title_re=fb)
                if win.exists(timeout=1):
                    return win
            except: continue

    # Strategy 3: Just find ANY window that might be a browser if we are desperate
    try:
        for win in desktop.windows():
            title = win.window_text()
            if any(b in title for b in ["Edge", "Chrome", "Firefox"]):
                return win
    except: pass

    return None

def click_element(window_title: str, control_title: str) -> Dict[str, Union[bool, str]]:
    """
    Find a window by title and click a control within it using multiple discovery strategies.
    """
    if STOP_EVENT.is_set():
        return {"ok": False, "result": "Halted by STOP_EVENT"}
    try:
        # Be loose with window matching
        win = _get_window(f".*{window_title}.*")
        if not win:
             return {"ok": False, "result": f"Could not find window matching '{window_title}'"}

        win.wait('ready', timeout=10)
        win.set_focus()

        ctrl = _find_element(win, control_title, ["Button", "Hyperlink", "Text", "MenuItem"])
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
        win = _get_window(f".*{window_title}.*")
        if not win:
             return {"ok": False, "result": f"Could not find window matching '{window_title}'"}

        win.wait('ready', timeout=10)
        win.set_focus()

        ctrl = _find_element(win, control_title, ["Edit", "Document", "Text", "ComboBox"])
        if ctrl:
            # More robust typing: click, clear (ctrl+a, backspace), then type
            ctrl.click_input()
            ctrl.type_keys("^a{BACKSPACE}", with_spaces=True)
            ctrl.type_keys(text, with_spaces=True)
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
        desktop = Desktop(backend="uia")
        win = desktop.window(title_re=f".*{window_title}.*")
        texts = win.texts()
        return {"ok": True, "result": str(texts)}
    except Exception as e:
        return {"ok": False, "result": str(e)}

def get_window_elements(window_title_re: str) -> dict:
    """
    Walks the UI tree of a window and extracts interactive elements.
    """
    if STOP_EVENT.is_set():
        return {"ok": False, "result": "Halted by STOP_EVENT"}
    try:
        win = _get_window(window_title_re)
        if not win:
             return {"ok": False, "result": f"Could not find window matching '{window_title_re}'"}

        elements = []
        # We walk only top-level children and some common types to keep it small
        # In a real app we might need deeper walking
        for child in win.descendants():
            c_type = child.element_info.control_type
            if c_type in ["Button", "Edit", "Text", "Hyperlink", "ListItem", "MenuItem", "CheckBox"]:
                elements.append({
                    "type": c_type,
                    "title": child.window_text(),
                    "auto_id": child.element_info.automation_id,
                    "name": child.element_info.name,
                    "class": child.element_info.class_name
                })

        return {
            "ok": True,
            "title": win.window_text(),
            "elements": elements
        }
    except Exception as e:
        return {"ok": False, "result": str(e)}
