import base64
import io
import mss
import pytesseract
from PIL import Image
from ..llm_client.gemini_client import generate_response

def capture_screen() -> Image.Image:
    """
    Captures a screenshot of the full screen and returns it as a PIL Image.

    Returns:
        Image.Image: The captured screenshot.
    """
    with mss.mss() as sct:
        # Capture the primary monitor
        monitor = sct.monitors[1]
        screenshot = sct.grab(monitor)
        # Convert to PIL Image
        return Image.frombytes("RGB", screenshot.size, screenshot.bgra, "raw", "BGRX")

def extract_text_ocr(image: Image.Image) -> str:
    """
    Runs pytesseract OCR on the provided image and returns the raw extracted text.

    Args:
        image (Image.Image): The image to process.

    Returns:
        str: The raw text extracted from the image.
    """
    return pytesseract.image_to_string(image)

def ask_gemini_vision(image: Image.Image, question: str) -> str:
    """
    Sends the screenshot to Gemini Vision with a question and
    returns the model's text answer.

    Args:
        image (Image.Image): The screenshot to analyze.
        question (str): The question to ask about the image.

    Returns:
        str: The text response from Gemini Vision.
    """
    # Convert image to bytes
    buffered = io.BytesIO()
    image.save(buffered, format="PNG")
    img_bytes = buffered.getvalue()

    return generate_response("You are a vision assistant.", question, image_data=img_bytes)
