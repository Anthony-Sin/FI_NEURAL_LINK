import requests
from bs4 import BeautifulSoup
import json
import os
from FI_NEURAL_LINK.config_manager import load_config
from FI_NEURAL_LINK.task_c_tools.pywinauto_wrapper import windows_control
from FI_NEURAL_LINK.task_b_dashboard.panels.stop_panel import STOP_EVENT

def extract_structure_from_window(window_title_re: str) -> dict:
    """
    Uses UI Automation to extract the 'live' structure of a browser window.
    This preserves the user's active session and cookies.
    """
    return windows_control.get_window_elements(window_title_re)

def save_webpage_structure(url: str, filename: str = "webpage_structure.json") -> dict:
    """
    Retrieves the real HTML of a webpage, extracts its interactive elements,
    and saves the structure to a JSON file in the configured directory.
    """
    if STOP_EVENT.is_set():
        return {"ok": False, "result": "Halted by STOP_EVENT"}

    try:
        config = load_config()
        save_dir_name = config.get("settings", {}).get("save_dir", "web_visited")

        # Check if this is a UIA capture request from smart_web_action
        if url.startswith("uia_capture://"):
            domain = url.replace("uia_capture://", "")
            obs_res = extract_structure_from_window(f".*{domain}.*")
            if obs_res.get("ok"):
                structure = obs_res
            else:
                return obs_res
        else:
            response = requests.get(url, timeout=10)
            response.raise_for_status()

            soup = BeautifulSoup(response.text, 'html.parser')

            structure = {
                "url": url,
                "title": soup.title.string if soup.title else "No Title",
                "meta": [],
                "elements": []
            }

            # Extract meta tags
            for meta in soup.find_all('meta'):
                structure["meta"].append(meta.attrs)

            # Extract interactive elements
            # Buttons
            for btn in soup.find_all(['button', 'input']):
                if btn.name == 'button' or btn.get('type') in ['button', 'submit', 'reset']:
                    structure["elements"].append({
                        "type": "button",
                        "text": btn.get_text().strip() or btn.get('value') or btn.get('name'),
                        "attributes": btn.attrs
                    })

            # Text Inputs
            for inp in soup.find_all('input'):
                if inp.get('type') in ['text', 'search', 'email', 'password', 'url', 'number']:
                    structure["elements"].append({
                        "type": "text_input",
                        "placeholder": inp.get('placeholder'),
                        "name": inp.get('name'),
                        "id": inp.get('id'),
                        "attributes": inp.attrs
                    })

            # Forms
            for form in soup.find_all('form'):
                structure["elements"].append({
                    "type": "form",
                    "action": form.get('action'),
                    "method": form.get('method'),
                    "attributes": form.attrs
                })

            # Links
            for link in soup.find_all('a', href=True):
                structure["elements"].append({
                    "type": "link",
                    "text": link.get_text().strip(),
                    "href": link.get('href'),
                    "attributes": link.attrs
                })

        # Save to configured directory
        save_dir = os.path.join(os.getcwd(), save_dir_name)
        if not os.path.exists(save_dir):
            os.makedirs(save_dir)

        filepath = os.path.join(save_dir, filename)

        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(structure, f, indent=2, ensure_ascii=False)

        return {"ok": True, "result": f"Webpage structure saved to {filepath}"}

    except Exception as e:
        return {"ok": False, "result": f"Failed to save webpage structure: {str(e)}"}
