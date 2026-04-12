import unittest
from unittest.mock import MagicMock, patch
import sys

# Mock pyautogui before importing ToolRouter because it requires DISPLAY
mock_pyautogui = MagicMock()
sys.modules["pyautogui"] = mock_pyautogui
mock_mouseinfo = MagicMock()
sys.modules["mouseinfo"] = mock_mouseinfo
mock_pywinauto = MagicMock()
sys.modules["pywinauto"] = mock_pywinauto

from FI_NEURAL_LINK.tools.router import ToolRouter
from FI_NEURAL_LINK.ui.panels.stop_panel import STOP_EVENT

class TestToolRouterStopEvent(unittest.TestCase):
    def setUp(self):
        STOP_EVENT.clear()
        self.router = ToolRouter()

    def test_execute_respects_stop_event(self):
        # Set STOP_EVENT
        STOP_EVENT.set()

        # Try to execute an action
        result = self.router.execute("click", {"x": 100, "y": 100})

        # Verify it was halted
        self.assertFalse(result["ok"])
        self.assertEqual(result["result"], "Halted by STOP_EVENT")

        # Clear STOP_EVENT for other tests
        STOP_EVENT.clear()

    @patch("FI_NEURAL_LINK.tools.automation.mouse_keyboard.click")
    def test_execute_without_stop_event(self, mock_click):
        mock_click.return_value = {"ok": True, "result": "Clicked at (100, 100)"}

        result = self.router.execute("click", {"x": 100, "y": 100})

        self.assertTrue(result["ok"])
        self.assertEqual(result["result"], "Clicked at (100, 100)")

if __name__ == "__main__":
    unittest.main()
