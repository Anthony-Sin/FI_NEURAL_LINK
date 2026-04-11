from FI_NEURAL_LINK.task_a_agent_brain.screen_perception import screen_perception

def read_screen() -> dict:
    """
    Captures the screen and extracts text using OCR.
    """
    try:
        image = screen_perception.capture_screen()
        text = screen_perception.extract_text_ocr(image)
        return {"ok": True, "result": text}
    except Exception as e:
        return {"ok": False, "result": str(e)}

def analyze_screen(question: str) -> dict:
    """
    Captures the screen and asks Gemini Vision a question about it.
    """
    try:
        image = screen_perception.capture_screen()
        answer = screen_perception.ask_gemini_vision(image, question)
        return {"ok": True, "result": answer}
    except Exception as e:
        return {"ok": False, "result": str(e)}
