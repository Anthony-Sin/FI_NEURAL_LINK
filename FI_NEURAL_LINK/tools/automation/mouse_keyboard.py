"""
This module provides a unified interface for PyAutoGUI mouse and keyboard operations.
Every function in this module returns a dictionary with the following format:
{
    "ok": bool,      # True if the operation was successful, False otherwise.
    "result": str    # A descriptive message of the outcome or the error encountered.
}

If the global STOP_EVENT from FI_NEURAL_LINK.ui.panels.stop_panel is set,
all operations will be halted and return an error status.
"""

import pyautogui
from FI_NEURAL_LINK.ui.panels.stop_panel import STOP_EVENT

# Enable PyAutoGUI fail-safe feature
pyautogui.FAILSAFE = True

def click(x, y):
    """Perform a mouse click at the specified coordinates."""
    if STOP_EVENT.is_set():
        return {"ok": False, "result": "Halted by STOP_EVENT"}
    try:
        pyautogui.click(x, y)
        return {"ok": True, "result": f"Clicked at ({x}, {y})"}
    except Exception as e:
        return {"ok": False, "result": str(e)}

def double_click(x, y):
    """Perform a mouse double-click at the specified coordinates."""
    if STOP_EVENT.is_set():
        return {"ok": False, "result": "Halted by STOP_EVENT"}
    try:
        pyautogui.doubleClick(x, y)
        return {"ok": True, "result": f"Double clicked at ({x}, {y})"}
    except Exception as e:
        return {"ok": False, "result": str(e)}

def right_click(x, y):
    """Perform a mouse right-click at the specified coordinates."""
    if STOP_EVENT.is_set():
        return {"ok": False, "result": "Halted by STOP_EVENT"}
    try:
        pyautogui.rightClick(x, y)
        return {"ok": True, "result": f"Right clicked at ({x}, {y})"}
    except Exception as e:
        return {"ok": False, "result": str(e)}

def type_text(text, interval=0.05):
    """Type the given text with a specified interval between keystrokes."""
    if STOP_EVENT.is_set():
        return {"ok": False, "result": "Halted by STOP_EVENT"}
    try:
        pyautogui.write(text, interval=interval)
        return {"ok": True, "result": f"Typed text: {text}"}
    except Exception as e:
        return {"ok": False, "result": str(e)}

def press_key(key):
    """Press a single keyboard key."""
    if STOP_EVENT.is_set():
        return {"ok": False, "result": "Halted by STOP_EVENT"}
    try:
        pyautogui.press(key)
        return {"ok": True, "result": f"Pressed key: {key}"}
    except Exception as e:
        return {"ok": False, "result": str(e)}

def hotkey(keys: list):
    """Press a combination of keys (e.g., ['ctrl', 'c'])."""
    if STOP_EVENT.is_set():
        return {"ok": False, "result": "Halted by STOP_EVENT"}
    try:
        pyautogui.hotkey(*keys)
        return {"ok": True, "result": f"Pressed hotkey: {keys}"}
    except Exception as e:
        return {"ok": False, "result": str(e)}

def move_to(x, y):
    """Move the mouse cursor to the specified coordinates."""
    if STOP_EVENT.is_set():
        return {"ok": False, "result": "Halted by STOP_EVENT"}
    try:
        pyautogui.moveTo(x, y)
        return {"ok": True, "result": f"Moved to ({x}, {y})"}
    except Exception as e:
        return {"ok": False, "result": str(e)}

def scroll(x, y, clicks):
    """Scroll the mouse wheel at the specified coordinates."""
    if STOP_EVENT.is_set():
        return {"ok": False, "result": "Halted by STOP_EVENT"}
    try:
        pyautogui.scroll(clicks, x=x, y=y)
        return {"ok": True, "result": f"Scrolled {clicks} clicks at ({x}, {y})"}
    except Exception as e:
        return {"ok": False, "result": str(e)}

def drag_and_drop(start_x, start_y, end_x, end_y, duration=1.0):
    """Perform a drag and drop operation from start to end coordinates."""
    if STOP_EVENT.is_set():
        return {"ok": False, "result": "Halted by STOP_EVENT"}
    try:
        pyautogui.moveTo(start_x, start_y)
        pyautogui.dragTo(end_x, end_y, duration=duration, button='left')
        return {"ok": True, "result": f"Dragged from ({start_x}, {start_y}) to ({end_x}, {end_y})"}
    except Exception as e:
        return {"ok": False, "result": str(e)}
