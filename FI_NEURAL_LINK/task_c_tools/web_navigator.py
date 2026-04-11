import os
import json
from . import web_scraper
from .pywinauto_wrapper import windows_control
from ..task_a_agent_brain.llm_client import gemini_client
from FI_NEURAL_LINK.config_manager import get_model
from FI_NEURAL_LINK.task_b_dashboard.panels.stop_panel import STOP_EVENT

def smart_web_action(url: str, instruction: str, structure_filename: str = "temp_structure.json") -> dict:
    """
    Saves webpage structure, filters it for token efficiency, analyzes it via Gemini
    to find the right element, and performs the requested action.
    """
    if STOP_EVENT.is_set():
        return {"ok": False, "result": "Halted by STOP_EVENT"}

    try:
        config = get_model("router") # Just to trigger config load if needed, but we use load_config
        from FI_NEURAL_LINK.config_manager import load_config
        cfg = load_config()
        save_dir_name = cfg.get("settings", {}).get("save_dir", "web_visited")

        # 1. Save structure
        save_res = web_scraper.save_webpage_structure(url, structure_filename)
        if not save_res["ok"]:
            return save_res

        # 2. Read and filter structure for token efficiency
        save_path = os.path.join(os.getcwd(), save_dir_name, structure_filename)
        with open(save_path, 'r', encoding='utf-8') as f:
            structure = json.load(f)

        # Keep only essential fields for LLM
        filtered_elements = []
        for el in structure.get("elements", []):
            filtered_el = {
                "type": el["type"],
                "text": el.get("text"),
                "id": el.get("id"),
                "name": el.get("name"),
                "placeholder": el.get("placeholder")
            }
            # Remove null values
            filtered_el = {k: v for k, v in filtered_el.items() if v is not None}
            filtered_elements.append(filtered_el)

        compact_structure = {
            "title": structure.get("title"),
            "elements": filtered_elements
        }

        # 3. Analyze via Gemini Pro to find element and action
        system_prompt = (
            "You are a web element locator. Given a JSON representation of a webpage's structure "
            "and an instruction, identify the best matching element and the action to perform.\n\n"
            "Return ONLY a JSON object:\n"
            "{\n"
            "  \"action\": \"click_element\" or \"type_in_element\",\n"
            "  \"window_title\": \"exact or regex title\",\n"
            "  \"control_title\": \"exact title/name from attributes\",\n"
            "  \"text\": \"text to type (if applicable)\"\n"
            "}"
        )

        user_msg = f"Structure: {json.dumps(compact_structure)}\nInstruction: {instruction}"

        # Logging exact prompt to file and dashboard
        import logging
        logger = logging.getLogger("AgentCore")
        logger.debug(f"--- SMART WEB ACTION PROMPT ---")
        logger.debug(user_msg)

        response = gemini_client.generate_response(system_prompt, user_msg, model_name=get_model("web_navigator"))

        # Clean JSON
        clean_response = response.strip()
        if clean_response.startswith("```json"): clean_response = clean_response[7:].strip()
        if clean_response.endswith("```"): clean_response = clean_response[:-3].strip()

        decision = json.loads(clean_response)

        # 4. Execute action
        action = decision.get("action")
        win_title = decision.get("window_title", ".*")
        ctrl_title = decision.get("control_title")
        text = decision.get("text")

        if action == "click_element":
            res = windows_control.click_element(win_title, ctrl_title)
            return {"ok": res.get("ok", False), "result": str(res.get("result", res))}
        elif action == "type_in_element":
            res = windows_control.type_in_element(win_title, ctrl_title, text)
            return {"ok": res.get("ok", False), "result": str(res.get("result", res))}
        else:
            return {"ok": False, "result": f"Unknown action from discovery: {action}"}

    except Exception as e:
        return {"ok": False, "result": f"Smart web action failed: {str(e)}"}
