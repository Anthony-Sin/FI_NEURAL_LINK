import pytest
import sys
from unittest.mock import MagicMock

@pytest.fixture(autouse=True)
def mock_gui_libs(monkeypatch):
    """Automatically mocks hardware-dependent libraries for all tests."""
    mock_pa = MagicMock()
    mock_pwa = MagicMock()
    mock_mss = MagicMock()

    monkeypatch.setitem(sys.modules, "pyautogui", mock_pa)
    monkeypatch.setitem(sys.modules, "pywinauto", mock_pwa)
    monkeypatch.setitem(sys.modules, "mss", mock_mss)

    return mock_pa, mock_pwa, mock_mss

@pytest.fixture
def mock_config(monkeypatch):
    """Provides a controlled configuration for tests."""
    from FI_NEURAL_LINK import config_manager
    def mock_load():
        return {
            "models": {
                "router": "mock-model",
                "executor": "mock-model"
            },
            "settings": {"save_dir": "test_visited"}
        }
    monkeypatch.setattr(config_manager, "load_config", mock_load)
