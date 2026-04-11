# Task C: Automation Tools

This directory contains a suite of automation tools for UI interaction, application management, and system safety.

## Unified Return Format

All tool functions return a dictionary in the following format:

```json
{
    "ok": boolean,
    "result": "string message or error description"
}
```

## Tool Modules

### 1. Mouse & Keyboard (`pyautogui_wrapper/mouse_keyboard.py`)
Wraps PyAutoGUI for basic UI interactions.
- `click(x, y)`
- `double_click(x, y)`
- `right_click(x, y)`
- `type_text(text, interval=0.05)`
- `press_key(key)`
- `hotkey(*keys)`
- `move_to(x, y)`
- `scroll(x, y, clicks)`

### 2. Windows Control (`pywinauto_wrapper/windows_control.py`)
Wraps pywinauto for element-level Windows automation.
- `find_window(title_regex)`
- `click_element(window_title, control_title)`
- `type_in_element(window_title, control_title, text)`
- `get_window_text(window_title)`

### 3. Launcher (`launcher.py`)
Manages external applications and URLs.
- `open_url(url)`: Validates that URL starts with `http://` or `https://`.
- `launch_app(path, args=[])`
- `kill_process(name)`: Terminates process by name.

## Tool Router

The `ToolRouter` class in `tool_router.py` provides a single entry point for all actions.

### Supported Action Strings and Params

| Action | Parameters |
|---|---|
| `click` | `x`, `y` |
| `double_click` | `x`, `y` |
| `right_click` | `x`, `y` |
| `type_text` | `text`, `interval` (optional) |
| `press_key` | `key` |
| `hotkey` | `keys` (as arguments) |
| `move_to` | `x`, `y` |
| `scroll` | `x`, `y`, `clicks` |
| `open_url` | `url` |
| `launch_app` | `path`, `args` (optional) |
| `kill_process` | `name` |
| `find_window` | `title_regex` |
| `click_element` | `window_title`, `control_title` |
| `type_in_element` | `window_title`, `control_title`, `text` |
| `get_window_text` | `window_title` |

## Safety Features

### STOP_EVENT
Every tool function checks a global `STOP_EVENT` (imported from `task_b_dashboard.panels.stop_panel`) before execution. If the event is set, the tool will immediately return `{"ok": False, "result": "Halted by STOP_EVENT"}` without performing the action.

### Rate Limiting
The `ToolRouter` uses a `RateLimiter` (from `safety/rate_limiter.py`) to prevent excessive tool calls.
- **Default Limit**: 30 calls per 10 seconds.
- If the limit is exceeded, the router returns `{"ok": False, "result": "Rate limit exceeded"}`.

### Fail-Safe
- PyAutoGUI's `FAILSAFE` is set to `True`. Moving the mouse to any corner of the screen will trigger an exception, which the tool will catch and return as an error.
- All tools catch exceptions and return them in the `result` field.
