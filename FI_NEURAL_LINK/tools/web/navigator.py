import os
import json
import re
from . import scraper
from ..automation import windows_control
from ...brain import llm_client as gemini_client
from ...brain.json_parser import parse_llm_json
from ...brain.memory import FailureMemory
from FI_NEURAL_LINK.core.config import get_model
from FI_NEURAL_LINK.ui.panels.stop_panel import STOP_EVENT

def smart_web_action(url_domain: str, instruction: str, expected_title_re: str = ".*") -> dict:
    """
    Implements a robust act->observe->decide pipeline for web actions.
    Uses UI Automation to extract live DOM and preserves user session.
    """
    import time
    import logging
    logger = logging.getLogger("AgentCore")

    max_attempts = 3
    last_error = ""
    failure_mem = FailureMemory()
    for attempt in range(1, max_attempts + 1):
        if STOP_EVENT.is_set():
            return {"ok": False, "result": "Halted by STOP_EVENT"}

        logger.info(f"Smart Web Action: Attempt {attempt}/{max_attempts}")

        # 1. Extract structure via UI Automation (preserves cookies/session)
        # Search window by expected title or domain name
        search_title = expected_title_re if expected_title_re != ".*" else f".*{url_domain}.*"

        start_time = time.time()
        # If the direct domain search fails, we'll try a broader search inside extract_structure_from_window
        # which now has fallbacks in windows_control._get_window
        obs_res = scraper.extract_structure_from_window(search_title)
        load_time = time.time() - start_time
        logger.info(f"Page structure extracted in {load_time:.2f}s. Adding 3s safety buffer.")
        time.sleep(3) # User requested 3s safety buffer

        # Update web_visited folder during interactive sessions
        if obs_res.get("ok"):
            try:
                # We reuse the filename convention or create one from domain
                clean_domain = url_domain.replace(".", "_")
                scraper.save_webpage_structure(url=f"uia_capture://{url_domain}", filename=f"live_{clean_domain}.json")
            except:
                pass # Non-critical if background save fails

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

        # Prioritize relevant elements to keep within token limits but capture what's important
        priority_elements = []
        other_elements = []

        keywords = instruction.lower().split()

        for el in elements:
            text = (el.get("title") or el.get("name") or "").lower()
            e_type = el["type"].lower()

            entry = {
                "type": el["type"],
                "text": el.get("title") or el.get("name"),
                "auto_id": el.get("auto_id"),
                "class": el.get("class")
            }

            # High priority: matches instruction keywords or is a common interactive type
            if any(k in text for k in keywords) or e_type in ["edit", "button", "combobox"]:
                priority_elements.append(entry)
            else:
                other_elements.append(entry)

        # Build compact structure with a preference for prioritized elements
        final_elements = (priority_elements + other_elements)[:150]

        compact_structure = {
            "title": current_title,
            "elements": final_elements
        }

        system_prompt = (
            "You are a web element locator. Given a JSON representation of a LIVE browser window "
            "and an instruction, identify the best matching element and the action to perform.\n\n"
            "STRICT ATOMIC RULE: You MUST perform exactly ONE interaction (click or type) per response. "
            "If the instruction implies multiple steps (e.g. 'type X and click Y'), ONLY pick the FIRST step. "
            "The system will re-scrape for the subsequent steps.\n\n"
            "Return ONLY a JSON object:\n"
            "{\n"
            "  \"action\": \"click_element\" or \"type_in_element\",\n"
            "  \"control_title\": \"exact title/name or auto_id\",\n"
            "  \"text\": \"text to type (if applicable)\"\n"
            "}"
        )

        user_msg = f"Structure: {json.dumps(compact_structure)}\nInstruction: {instruction}"

        # Add failure memory to prompt
        failure_block = failure_mem.get_failure_block(url_domain)
        if failure_block:
            user_msg = f"{failure_block}\n\n{user_msg}"

        if last_error:
            user_msg += f"\nNote from previous attempt: {last_error}"

        logger.debug(f"--- SMART WEB ACTION PROMPT ---\n{user_msg}\n-------------------------------")

        try:
            response = gemini_client.generate_response(system_prompt, user_msg, model_name=get_model("web_navigator"))
            decision = parse_llm_json(response)

            # 4. Execute
            action = decision.get("action")
            ctrl_title = decision.get("control_title")
            text = decision.get("text")

            if action == "click_element":
                # Use current_title instead of search_title to be more specific once window is found
                res = windows_control.click_element(current_title, ctrl_title)
            elif action == "type_in_element":
                # Detect if the instruction or context implies Enter
                should_enter = any(k in instruction.lower() for k in ["enter", "return", "submit", "start"])
                res = windows_control.type_in_element(current_title, ctrl_title, text, enter=should_enter)
            else:
                return {"ok": False, "result": f"Unknown action: {action}"}

            if res.get("ok"):
                logger.info("Action successful. Observing changes...")
                time.sleep(2)
                post_obs = scraper.extract_structure_from_window(current_title)
                if post_obs.get("ok"):
                    new_elements = post_obs.get("elements", [])
                    # Simple detection of new elements (e.g. popups)
                    if len(new_elements) > len(elements):
                        logger.info(f"Detected {len(new_elements) - len(elements)} new elements. Possible popup.")
                return res
            else:
                last_error = res.get('result')
                failure_mem.record_failure(url_domain, instruction, last_error)
                logger.warning(f"Action failed: {last_error}. Retrying...")
                time.sleep(3)

        except Exception as e:
            logger.error(f"Analysis or execution error: {str(e)}")
            time.sleep(3)

    return {"ok": False, "result": f"Failed after {max_attempts} attempts."}
