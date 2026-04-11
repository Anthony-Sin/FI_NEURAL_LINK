import unittest
from unittest.mock import MagicMock, patch
from FI_NEURAL_LINK.task_a_agent_brain.loop_guard import LoopGuard

class TestLoopGuard(unittest.TestCase):
    def test_loop_detection(self):
        lg = LoopGuard(n=5)
        lg.record_action("click button")
        lg.record_action("click button")
        # Third time should detect a loop
        self.assertTrue(lg.check_loop("click button"))

        lg.record_action("type text")
        lg.record_action("type text")
        lg.record_action("type text")
        lg.record_action("type text")
        # actions: ["click button", "type text", "type text", "type text", "type text"]
        # "click button" is now only there once.
        self.assertFalse(lg.check_loop("click button"))

    def test_window_trimming(self):
        lg = LoopGuard(n=2)
        lg.record_action("a")
        lg.record_action("b")
        lg.record_action("c")
        self.assertEqual(lg.actions, ["b", "c"])

    def test_reset(self):
        lg = LoopGuard()
        lg.record_action("a")
        lg.reset()
        self.assertEqual(lg.actions, [])

if __name__ == "__main__":
    unittest.main()
