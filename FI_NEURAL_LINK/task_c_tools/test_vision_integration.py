import unittest
from unittest.mock import MagicMock, patch
import sys
from PIL import Image

# Mock dependencies before importing
mock_pyautogui = MagicMock()
sys.modules["pyautogui"] = mock_pyautogui
mock_mouseinfo = MagicMock()
sys.modules["mouseinfo"] = mock_mouseinfo
mock_pywinauto = MagicMock()
sys.modules["pywinauto"] = mock_pywinauto
mock_mss = MagicMock()
sys.modules["mss"] = mock_mss
mock_pytesseract = MagicMock()
sys.modules["pytesseract"] = mock_pytesseract

from FI_NEURAL_LINK.task_c_tools.tool_router import ToolRouter
from FI_NEURAL_LINK.task_b_dashboard.panels.stop_panel import STOP_EVENT

class TestVisionIntegration(unittest.TestCase):
    def setUp(self):
        STOP_EVENT.clear()
        self.router = ToolRouter()

    @patch("FI_NEURAL_LINK.task_a_agent_brain.screen_perception.screen_perception.capture_screen")
    @patch("FI_NEURAL_LINK.task_a_agent_brain.screen_perception.screen_perception.extract_text_ocr")
    def test_read_screen_action(self, mock_ocr, mock_capture):
        mock_capture.return_value = Image.new("RGB", (100, 100))
        mock_ocr.return_value = "Hello World"

        result = self.router.execute("read_screen", {})

        self.assertTrue(result["ok"])
        self.assertEqual(result["result"], "Hello World")
        mock_capture.assert_called_once()
        mock_ocr.assert_called_once()

    @patch("FI_NEURAL_LINK.task_a_agent_brain.screen_perception.screen_perception.capture_screen")
    @patch("FI_NEURAL_LINK.task_a_agent_brain.screen_perception.screen_perception.ask_gemini_vision")
    def test_analyze_screen_action(self, mock_vision, mock_capture):
        mock_capture.return_value = Image.new("RGB", (100, 100))
        mock_vision.return_value = "The screen shows a dashboard."

        result = self.router.execute("analyze_screen", {"question": "What is on the screen?"})

        self.assertTrue(result["ok"])
        self.assertEqual(result["result"], "The screen shows a dashboard.")
        mock_vision.assert_called_once_with(mock_capture.return_value, "What is on the screen?")

if __name__ == "__main__":
    unittest.main()
