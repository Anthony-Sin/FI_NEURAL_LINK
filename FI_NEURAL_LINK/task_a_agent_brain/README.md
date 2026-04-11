# Task A Agent Brain

This directory contains the core intelligence components of the agent.

## Components

### AgentCore
The `AgentCore` class is the central orchestrator that manages goal decomposition and execution.

#### Instantiation
To instantiate `AgentCore`, provide a configuration dictionary:

```python
from FI_NEURAL_LINK.task_a_agent_brain.agent_core import AgentCore

config = {
    "gemini_api_key": "YOUR_API_KEY",
    "max_retries": 3,
    "loop_window": 5
}
agent = AgentCore(config)
```

#### Configuration Keys
- `gemini_api_key` (str): Required. Your Google Gemini API key.
- `max_retries` (int): Optional. The maximum number of times to retry a failed action.
- `loop_window` (int): Optional. The number of recent actions to track for loop detection (default is 5).

#### Methods

##### `run_goal(goal: str) -> list`
Decomposes a plain-English goal into discrete action steps and executes them. It uses a `LoopGuard` to prevent infinite loops of repetitive actions.

- **Parameters**: `goal` (str) - The high-level objective.
- **Returns**: A list of result dictionaries, each containing:
    - `step_id`: Identifier of the step.
    - `description`: What was done.
    - `status`: Outcome of the step (e.g., "completed").
    - `tool_used`: The tool hint associated with the step.
- **Raises**: `RuntimeError` if a loop is detected.

### Screen Perception
Located in `screen_perception/`, this module handles screenshot capture, OCR, and visual analysis using Gemini Vision.

### Goal Decomposer
Located in `goal_decomposer/`, this module breaks down user goals into structured JSON action steps.

### Loop Guard
The `LoopGuard` class tracks action history to detect and halt repetitive behaviors.
