from unittest.mock import MagicMock

class MockUIAWrapper:
    def __init__(self, name="MockElement"):
        self.name = name
    def exists(self, timeout=0): return True
    def click_input(self): pass
    def type_keys(self, text, with_spaces=True): pass

def get_mock_desktop():
    desktop = MagicMock()
    window = MagicMock()
    window.exists.return_value = True
    window.set_focus.return_value = window
    window.child_window.return_value = MockUIAWrapper()
    desktop.window.return_value = window
    return desktop
