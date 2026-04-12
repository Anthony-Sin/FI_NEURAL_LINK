import os
import json
import re
from . import web_scraper
from .pywinauto_wrapper import windows_control
from ..task_a_agent_brain.llm_client import gemini_client
from FI_NEURAL_LINK.config_manager import get_model
from FI_NEURAL_LINK.task_b_dashboard.panels.stop_panel import STOP_EVENT

def smart_web_action(url_domain: str, instruction: str, expected_title_re: str = ".*") -> dict:
    """
    Implements a robust act->observe->decide pipeline for web actions.
    Uses UI Automation to extract live DOM and preserves user session.
    """
    import time
    import logging
    logger = logging.getLogger("AgentCore")

    max_attempts = 5
    for attempt in range(1, max_attempts + 1):
        if STOP_EVENT.is_set():
            return {"ok": False, "result": "Halted by STOP_EVENT"}

        logger.info(f"Smart Web Action: Attempt {attempt}/{max_attempts}")

        # 1. Extract structure via UI Automation (preserves cookies/session)
        # Search window by expected title or domain name
        search_title = expected_title_re if expected_title_re != ".*" else f".*{url_domain}.*"

        # If the direct domain search fails, we'll try a broader search inside extract_structure_from_window
        # which now has fallbacks in windows_control._get_window
        obs_res = web_scraper.extract_structure_from_window(search_title)

        if not obs_res.get("ok"):
            logger.warning(f"Window not found or structured failed: {obs_res.get('result')}. Waiting 3s...")
            time.sleep(3)
            continue

        # 2. Check if right page
        current_title = obs_res.get("title", "")
        if "Sign in" in current_title or "Login" in current_title:
            return {"ok": False, "result": f"Login page detected ('{current_title}'). Human intervention required."}

        # Check if title matches expectations
        # (Very basic regex-like check)
        if expected_title_re != ".*" and not re.search(expected_title_re, current_title, re.I):
            logger.warning(f"Page title mismatch. Expected: {expected_title_re}, Got: {current_title}. Waiting 3s...")
            time.sleep(3)
            continue

        # 3. Filter and analyze
        elements = obs_res.get("elements", [])
        filtered = []
        for el in elements:
            filtered.append({
                "type": el["type"],
                "text": el.get("title") or el.get("name"),
                "auto_id": el.get("auto_id")
            })

        compact_structure = {
            "title": current_title,
            "elements": filtered[:100] # Cap to prevent token bloat
        }

        system_prompt = (
            "You are a web element locator. Given a JSON representation of a LIVE browser window "
            "and an instruction, identify the best matching element and the action to perform.\n\n"
            "Return ONLY a JSON object:\n"
            "{\n"
            "  \"action\": \"click_element\" or \"type_in_element\",\n"
            "  \"control_title\": \"exact title/name or auto_id\",\n"
            "  \"text\": \"text to type (if applicable)\"\n"
            "}"
        )

        user_msg = f"Structure: {json.dumps(compact_structure)}\nInstruction: {instruction}"
        logger.debug(f"--- SMART WEB ACTION PROMPT ---\n{user_msg}\n-------------------------------")

        try:
            response = gemini_client.generate_response(system_prompt, user_msg, model_name=get_model("web_navigator"))
            clean_response = response.strip()
            if clean_response.startswith("```json"): clean_response = clean_response[7:].strip()
            if clean_response.endswith("```"): clean_response = clean_response[:-3].strip()

            decision = json.loads(clean_response)

            # 4. Execute
            action = decision.get("action")
            ctrl_title = decision.get("control_title")
            text = decision.get("text")

            if action == "click_element":
                # Use current_title instead of search_title to be more specific once window is found
                res = windows_control.click_element(current_title, ctrl_title)
            elif action == "type_in_element":
                res = windows_control.type_in_element(current_title, ctrl_title, text)
            else:
                return {"ok": False, "result": f"Unknown action: {action}"}

            if res.get("ok"):
                return res
            else:
                logger.warning(f"Action failed: {res.get('result')}. Retrying...")
                time.sleep(3)

        except Exception as e:
            logger.error(f"Analysis or execution error: {str(e)}")
            time.sleep(3)

    return {"ok": False, "result": f"Failed after {max_attempts} attempts."}
