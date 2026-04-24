import pytest
import os
import json
from tools.system.terminal import execute_command

def test_terminal_whitelist(monkeypatch, tmp_path):
    # Setup mock config in a temp directory
    data_dir = tmp_path / "data"
    data_dir.mkdir(parents=True)
    config_file = data_dir / "terminal_config.json"

    config = {
        "access_level": "LOW",
        "levels": {
            "LOW": {
                "whitelist": ["dir", "echo"],
                "blacklist": ["rm"]
            }
        }
    }
    config_file.write_text(json.dumps(config))

    # Patch the config path in the module
    import tools.system.terminal as terminal
    monkeypatch.setattr(terminal, "os", MagicMock(path=os.path, exists=os.path.exists))

    # We need to ensure load_terminal_config points to our temp file
    def mock_load():
        with open(config_file, "r") as f:
            return json.load(f)
    monkeypatch.setattr(terminal, "load_terminal_config", mock_load)

    # Test allowed
    # Note: We won't actually execute the subprocess in this unit test to avoid OS dependency
    monkeypatch.setattr("subprocess.Popen", MagicMock())

    res = execute_command("dir C:\\")
    # Even if it fails because Popen is mocked, it should pass the whitelist
    assert "not in whitelist" not in res["result"]

    # Test blocked by whitelist
    res = execute_command("git status")
    assert "not in whitelist" in res["result"]

    # Test blocked by blacklist
    res = execute_command("rm -rf /")
    assert "blocked by blacklist" in res["result"]

from unittest.mock import MagicMock
