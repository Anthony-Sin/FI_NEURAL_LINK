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

import re
import time
from typing import Dict, Union
from pywinauto import Desktop
import pyautogui
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
    """Internal helper to find an element by multiple strategies. Returns a resolved wrapper."""
    if control_types is None:
        control_types = ["Button", "Edit", "Text", "ListItem", "MenuItem", "Hyperlink", "Document", "ComboBox"]

    # Use a very short timeout for iterative checks
    T = 0.1

    # Strategy 0: If it looks like an auto_id (starts with 'view_' or matches specific format)
    if identifier.startswith("view_") or identifier == "RootWebArea":
        try:
            spec = win.child_window(auto_id=identifier)
            if spec.exists(timeout=T): return spec.wait('exists', timeout=T)
        except: pass

    # Strategy 1 & 2: exact title/name/auto_id (checking most likely first)
    for attr in ['auto_id', 'name', 'title', 'control_id', 'best_match']:
        try:
            # Try with type constraint first
            for c_type in control_types:
                spec = win.child_window(**{attr: identifier, 'control_type': c_type})
                if spec.exists(timeout=T):
                    return spec.wait('exists', timeout=T)
            # Then without type constraint
            spec = win.child_window(**{attr: identifier})
            if spec.exists(timeout=T):
                return spec.wait('exists', timeout=T)
        except: continue

    # Strategy 3: Regex match on title/name
    try:
        spec = win.child_window(title_re=f".*{re.escape(identifier)}.*")
        if spec.exists(timeout=T): return spec.wait('exists', timeout=T)
    except: pass

    try:
        spec = win.child_window(name_re=f".*{re.escape(identifier)}.*")
        if spec.exists(timeout=T): return spec.wait('exists', timeout=T)
    except: pass

    # Strategy 4: Search in descendants (One pass, in-memory filtering)
    try:
        for child in win.descendants():
            info = child.element_info
            # Check for partial or exact match in multiple fields
            fields = [child.window_text(), info.name, info.automation_id, info.class_name]
            if any(identifier == f or (f and identifier in f) for f in fields):
                if control_types and info.control_type not in control_types:
                    continue
                return child
    except: pass

    return None

def _resolve_win(obj, name: str = "window"):
    """Helper to resolve a Specification to a Wrapper if needed."""
    if hasattr(obj, 'wait'):
        return obj.wait('ready', timeout=10)
    return obj

def _get_window(window_title_re: str):
    """Internal helper to find a window with fallbacks. Returns a WindowSpecification."""
    desktop = Desktop(backend="uia")

    # Strategy 1: Direct match (regex and literal)
    try:
        # Escape common title characters but allow .*
        safe_title = window_title_re.replace("(", r"\(").replace(")", r"\)")
        win = desktop.window(title_re=safe_title)
        if win.exists(timeout=2): return win
    except: pass

    try:
        # Literal match (handles parentheses etc in titles)
        clean_title = window_title_re.replace(".*", "")
        for w in desktop.windows():
            if clean_title and clean_title in w.window_text():
                return desktop.window(handle=w.handle)
    except: pass

    # Strategy 2: If it looks like a domain, try common browser suffixes
    if "." in window_title_re:
        clean_domain = window_title_re.replace(".*", "")
        fallbacks = [
            f".*{re.escape(clean_domain)}.*",
            f".*Microsoft Edge.*",
            f".*Google Chrome.*"
        ]
        for fb in fallbacks:
            try:
                win = desktop.window(title_re=fb)
                if win.exists(timeout=1): return win
            except: continue

    # Strategy 3: Just find ANY window that might be a browser if we are desperate
    try:
        for win in desktop.windows():
            title = win.window_text()
            if any(b in title for b in ["Edge", "Chrome", "Firefox"]):
                return desktop.window(handle=win.handle)
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
        win_obj = _get_window(f".*{window_title}.*")
        if not win_obj:
             return {"ok": False, "result": f"Could not find window matching '{window_title}'"}

        win = _resolve_win(win_obj)
        win.set_focus()

        ctrl = _find_element(win, control_title, ["Button", "Hyperlink", "Text", "MenuItem"])
        if ctrl:
            ctrl.click_input()
            return {"ok": True, "result": f"Clicked element '{control_title}'"}

        return {"ok": False, "result": f"Could not find element '{control_title}' in '{window_title}'"}
    except Exception as e:
        return {"ok": False, "result": str(e)}

def type_in_element(window_title: str, control_title: str, text: str, enter: bool = False) -> Dict[str, Union[bool, str]]:
    """
    Find a window by title and type text into a control within it using multiple discovery strategies.
    Supports pressing enter after typing.
    """
    if STOP_EVENT.is_set():
        return {"ok": False, "result": "Halted by STOP_EVENT"}
    try:
        win_obj = _get_window(f".*{window_title}.*")
        if not win_obj:
             return {"ok": False, "result": f"Could not find window matching '{window_title}'"}

        win = _resolve_win(win_obj)
        win.set_focus()

        ctrl = _find_element(win, control_title, ["Edit", "Document", "Text", "ComboBox", "ListItem"])
        if ctrl:
            # More robust typing: ensure focus, click, clear, then type with a small pause
            ctrl.set_focus()
            ctrl.click_input()
            time.sleep(1.0) # Longer wait for web apps to react to click

            # Use multiple methods for maximum compatibility
            try:
                # 1. Clear field
                ctrl.type_keys("^a{BACKSPACE}", with_spaces=True, pause=0.1)

                # 2. Type text via pywinauto
                ctrl.type_keys(text, with_spaces=True, pause=0.1)

                # 3. Verification & PyAutoGUI fallback
                time.sleep(0.5)
                # Check if it worked (loose check as some inputs hide values)
                val = str(ctrl.window_text())
                if text not in val:
                    # Fallback to direct hardware simulation
                    pyautogui.write(text, interval=0.02)

                if enter:
                    ctrl.type_keys("{ENTER}")

            except:
                # Deep fallback
                try: ctrl.set_edit_text(text)
                except:
                    # Last ditch effort: simple click and type
                    ctrl.click_input()
                    pyautogui.write(text, interval=0.02)

                if enter:
                    pyautogui.press("enter")

            return {"ok": True, "result": f"Typed '{text}' into '{control_title}'" + (" and pressed Enter" if enter else "")}

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
    Includes a readiness check for web documents.
    """
    if STOP_EVENT.is_set():
        return {"ok": False, "result": "Halted by STOP_EVENT"}
    try:
        win_obj = _get_window(window_title_re)
        if not win_obj:
             return {"ok": False, "result": f"Could not find window matching '{window_title_re}'"}

        win = _resolve_win(win_obj)

        # Readiness check: wait for web document area to appear if it's a browser
        if any(b in str(win.window_text()) for b in ["Edge", "Chrome", "Firefox"]):
            try:
                # RootWebArea is common for Chrome/Edge documents
                win.child_window(control_type="Document").wait('exists', timeout=5)
            except: pass # Continue anyway if it doesn't appear

        elements = []
        # We walk only top-level children and some common types to keep it small
        # In a real app we might need deeper walking
        for child in win.descendants():
            c_type = child.element_info.control_type
            if c_type in ["Button", "Edit", "Text", "Hyperlink", "ListItem", "MenuItem", "CheckBox", "Document", "ComboBox"]:
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
