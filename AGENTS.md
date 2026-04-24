# AGENTS.md — FI_NEURAL_LINK

## What this project is
FI_NEURAL_LINK is a Windows desktop automation agent. A user types a
natural-language command into a cyberpunk overlay dashboard; the agent
decomposes the goal into steps, perceives the screen, and executes
actions using mouse/keyboard/Windows UI tools.

## Module map

| Folder | What it owns | Key entry point |
|--------|-------------|-----------------|
| agents/ | Gemini LLM calls, goal decomposition, screen OCR/vision, loop detection | AgentCore in agents/agent.py |
| ui/ | tkinter overlay UI, command input, live log, emergency stop | Dashboard in ui/main_window.py |
| tools/ | PyAutoGUI, pywinauto, subprocess, webbrowser, rate limiting, credentials | ToolRouter in tools/router.py |

## How the three modules connect
1. User types a command → Dashboard.set_on_submit fires → AgentCore.run_goal(command)
2. AgentCore decomposes goal into steps → for each step calls ToolRouter.execute(action, params)
3. ToolRouter checks STOP_EVENT and rate limiter before every action
4. AgentCore logs results back to Dashboard.log(text, level)
5. If STOP_EVENT is set (emergency stop pressed), all tool calls halt immediately

## Integration instructions for an AI
- All modules are as top-level packages.
- Import order: task_c_tools first (defines STOP_EVENT), then task_a, then task_b
- The single shared state object is STOP_EVENT from ui/panels/stop_panel.py
- All tool functions return {"ok": bool, "result": str} — always check ok before proceeding
- AgentCore.run_goal returns a list of step result dicts
- Do not instantiate multiple Dashboard instances — it is a singleton UI

## Environment variables required
- GEMINI_API_KEY — Google Gemini API key

## Dependencies
google-generativeai, pyautogui, pywinauto, mss, Pillow, pytesseract, psutil