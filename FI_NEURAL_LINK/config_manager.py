import json
import os

CONFIG_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), "config.json")

def load_config() -> dict:
    """Loads the system configuration from config.json and .env."""
    config = {
        "models": {
            "router": "gemini-2.5-flash-lite",
            "executor": "gemini-1.5-pro",
            "web_navigator": "gemini-1.5-pro"
        },
        "settings": {
            "save_dir": os.environ.get("WEB_VISITED_DIR", "web_visited")
        }
    }

    if os.path.exists(CONFIG_PATH):
        with open(CONFIG_PATH, 'r') as f:
            file_config = json.load(f)
            # Deep merge simple
            if "models" in file_config:
                config["models"].update(file_config["models"])
            if "settings" in file_config:
                config["settings"].update(file_config["settings"])

    return config

def get_model(key: str) -> str:
    """Returns the model name for a specific component."""
    config = load_config()
    return config.get("models", {}).get(key, "gemini-1.5-flash")
