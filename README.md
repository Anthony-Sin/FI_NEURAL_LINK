# FI_NEURAL_LINK

FI_NEURAL_LINK is an AI-powered agent orchestrator designed for automated UI interaction and goal execution. It combines a sophisticated "Brain" for goal decomposition, a real-time monitoring Dashboard, and a suite of powerful Automation Tools.

## Project Structure

The project is organized into three main tasks:

### [Task A: Agent Brain](./FI_NEURAL_LINK/task_a_agent_brain/)
The intelligence core of the system.
- **AgentCore**: Orchestrates goal decomposition and execution.
- **Goal Decomposer**: Breaks down natural language goals into actionable JSON steps.
- **Screen Perception**: Uses Gemini Vision for OCR and visual analysis.
- **Loop Guard**: Detects and prevents repetitive action loops.

### [Task B: Dashboard](./FI_NEURAL_LINK/task_b_dashboard/)
A real-time monitoring and control interface built with Tkinter.
- **Real-time Logging**: Tracks agent activity and status.
- **Emergency Stop**: Provides a global `STOP_EVENT` to immediately halt all agent operations.
- **Command Entry**: Allows users to submit new goals to the agent.

### [Task C: Automation Tools](./FI_NEURAL_LINK/task_c_tools/)
A unified set of tools for interacting with the operating system and applications.
- **Mouse & Keyboard**: PyAutoGUI wrapper for basic UI interaction.
- **Windows Control**: Pywinauto wrapper for element-level automation.
- **Launcher**: Manages application startup and URL navigation.
- **Tool Router**: Centralized entry point with built-in **Rate Limiting**.

## Getting Started

### Prerequisites
- Python 3.12+
- Gemini API Key (set as `GEMINI_API_KEY` environment variable)

### Installation
```bash
pip install -r requirements.txt
```
*(Note: Ensure all dependencies like `pyautogui`, `pywinauto`, `psutil`, and `google-generativeai` are installed.)*

### Running the Agent
The main entry point for the application is `main.py`.

```bash
python main.py
```

## Safety Mechanisms
- **STOP_EVENT**: All tools and the agent core check this event before execution.
- **Rate Limiting**: The Tool Router limits execution frequency (default 30 calls / 10s).
- **Fail-Safe**: PyAutoGUI failsafe is enabled; move the mouse to any corner to abort.
