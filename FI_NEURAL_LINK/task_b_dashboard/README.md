# FI_NEURAL_LINK Dashboard

This module provides a tkinter-based overlay dashboard for monitoring and controlling the FI_NEURAL_LINK agent.

## Dashboard Class

The `Dashboard` class is the main entry point for the UI.

### Instantiation

```python
from task_b_dashboard.dashboard import Dashboard

db = Dashboard()
db.start()
```

### Public Methods

- `start()`: Launches the dashboard's tkinter mainloop in a daemon thread.
- `log(text: str, level: str)`: Appends a line to the log panel. `level` can be "info", "success", "warn", or "error".
- `set_on_submit(callback)`: Sets the callback function for when a command is submitted through the command panel. The callback should accept a single string argument.

## STOP_EVENT Integration

The dashboard includes an emergency stop button that interacts with a global `STOP_EVENT`.

### Importing STOP_EVENT

```python
from task_b_dashboard.panels.stop_panel import STOP_EVENT
```

### Agent Integration

The agent should check `STOP_EVENT.is_set()` periodically or before performing critical actions. If it is set, the agent should immediately cease operations.

```python
if STOP_EVENT.is_set():
    print("Agent stopped by EMERGENCY STOP")
    return
```

The "Resume" button on the dashboard clears the `STOP_EVENT`, allowing the agent to continue if it is designed to do so.
