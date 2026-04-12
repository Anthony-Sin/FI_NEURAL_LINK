from FI_NEURAL_LINK.perception import screen

def read_screen() -> dict:
    """
    Captures the screen and extracts text using OCR.
    """
    try:
        image = screen.capture_screen()
        text = screen.extract_text_ocr(image)
        return {"ok": True, "result": text}
    except Exception as e:
        return {"ok": False, "result": str(e)}

def analyze_screen(question: str) -> dict:
    """
    Captures the screen and asks Gemini Vision a question about it.
    """
    try:
        image = screen.capture_screen()
        answer = screen.ask_gemini_vision(image, question)
        return {"ok": True, "result": answer}
    except Exception as e:
        return {"ok": False, "result": str(e)}
