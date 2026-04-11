"""
This module provides tool-router-compatible wrappers for screen perception functions.
"""

from FI_NEURAL_LINK.task_a_agent_brain.screen_perception import screen_perception
from FI_NEURAL_LINK.task_b_dashboard.panels.stop_panel import STOP_EVENT

def read_screen() -> dict:
    """Captures the screen and extracts text using OCR."""
    if STOP_EVENT.is_set():
        return {"ok": False, "result": "Halted by STOP_EVENT"}

    try:
        img = screen_perception.capture_screen()
        text = screen_perception.extract_text_ocr(img)
        return {"ok": True, "result": text}
    except Exception as e:
        return {"ok": False, "result": f"OCR failed: {str(e)}"}

def analyze_screen(question: str) -> dict:
    """Captures the screen and asks Gemini Vision a question about it."""
    if STOP_EVENT.is_set():
        return {"ok": False, "result": "Halted by STOP_EVENT"}

    try:
        img = screen_perception.capture_screen()
        answer = screen_perception.ask_gemini_vision(img, question)
        return {"ok": True, "result": answer}
    except Exception as e:
        return {"ok": False, "result": f"Vision analysis failed: {str(e)}"}
