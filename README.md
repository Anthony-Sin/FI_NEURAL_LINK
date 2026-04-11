# FI_NEURAL_LINK: Neural Desktop Automation Agent

FI_NEURAL_LINK is a cyberpunk-themed, AI-powered desktop automation system that translates natural language commands into discrete OS-level actions. It leverages Google Gemini for high-level reasoning and visual perception, integrated with a suite of automation tools for direct hardware and UI interaction.

## 🚀 The Full Pipeline

The system follows a strict, linear pipeline to process user intent:

1.  **Input Capture**: The user enters a goal via the **Cyberpunk Dashboard** (text input in `CommandBar`) or via the **Voice System** (audio capture and transcription).
2.  **Goal Submission**: The dashboard triggers a callback that hands the goal to `AgentCore.run_goal(goal)`.
3.  **Decomposition**: `AgentCore` invokes the `GoalDecomposer`. This component sends the goal to the **Gemini LLM** (`gemini-2.5-flash-lite`) with a specialized system prompt, instructing it to break the goal into a JSON list of discrete steps.
4.  **Step Iteration**: `AgentCore` iterates through the generated steps. For each step:
    *   **Loop Protection**: `LoopGuard` checks if the action is repeating too frequently to prevent infinite loops.
    *   **Parameter Extraction**: `AgentCore` uses regex-based heuristics to extract specific parameters (URLs, app paths, coordinates, text, window/control titles) from the step's natural language description.
    *   **Tool Routing**: The `tool_hint` (see Execution Contexts) and extracted parameters are passed to the `ToolRouter`.
5.  **Execution**: The `ToolRouter` verifies the **Global STOP_EVENT** and the **Rate Limiter** before dispatching the command to the underlying automation wrappers (PyAutoGUI, pywinauto, or custom launchers).
6.  **Logging & Output**: Each step's result (success/failure) is logged back to the dashboard's **Activity Log** in real-time.

## 🧠 Execution Contexts (ECs) & Browser Strategy

In FI_NEURAL_LINK, **Execution Contexts** are represented by the `tool_hint` assigned to each decomposed step. The LLM selects the most appropriate EC based on the required action, following a specific priority hierarchy for browser-based tasks:

### Browser-First Strategy (Chrome, Edge, Brave, Firefox)
To ensure reliability and maintain user sessions (cookies), the agent prioritizes local UI inspection over visual models:
1.  **UI Automation (`click_element`, `type_in_element`)**: Preferred. Inspects the browser window via `pywinauto` to locate and interact with elements by their handles or names.
2.  **OCR (`read_screen`)**: Fallback. Extracts visible text from the screen if UI elements are not directly accessible.
3.  **Vision (`analyze_screen`)**: Last Resort. Uses Gemini Vision to semantically interpret the screen when both UI Automation and OCR fail.

### General Contexts
*   **`launch` / `open_url`**: App/Browser context for starting new tasks.
*   **`click` / `type`**: Direct hardware interaction context for basic coordinate-based manipulation.
*   **`read_screen`**: OCR context for extracting text-based state from the display.
*   **`analyze_screen`**: Vision context for high-level semantic understanding of the UI.

## 🛠 Capabilities & Models

### Models Used
*   **Google Gemini 2.5 Flash Lite**: Core LLM for goal decomposition and natural language understanding.
*   **Google Gemini Vision**: Used for multimodal screen analysis and semantic UI perception.
*   **Tesseract OCR**: Used for fast, local text extraction from screen captures.

### Capabilities
*   **Deep UI Inspection**: Can "look inside" Windows applications and browsers to find buttons and fields by title.
*   **Multimodal Perception**: Can "see" and interpret the screen to answer questions or find elements.
*   **Cross-App Automation**: Controls any Windows application via element-level (pywinauto) or coordinate-level (PyAutoGUI) interaction.
*   **Dynamic App Resolution**: Resolves natural language app names (e.g., "chrome") to full filesystem paths via registry and PATH lookups.
*   **Emergency Interruption**: Global `STOP_EVENT` allows immediate cessation of all automated activities.

## ⚠️ Limitations

*   **Linear Execution**: The system currently follows a static plan generated at the start; it does not dynamically re-plan if a step fails or the environment changes unexpectedly.
*   **Regex Parameter Parsing**: Parameter extraction from LLM descriptions relies on regex, which can be brittle if the LLM's phrasing deviates significantly.
*   **Headless constraints**: While the logic is robust, visual components (Dashboard/Tkinter) require a display environment.
*   **Static Rate Limiting**: The 30 calls / 10s limit is global and does not distinguish between "safe" actions and sensitive ones.

## 💡 Architectural Suggestions for Improvement

1.  **Dynamic Re-Planning**: Implement a feedback loop where the outcome of `read_screen` or `analyze_screen` is fed back into the LLM to adjust the remaining steps in the plan.
2.  **Semantic Parameter Extraction**: Instead of regex, use a second LLM pass to extract structured parameters from step descriptions to improve reliability.
3.  **Visual Verification**: Automatically perform an `analyze_screen` check after critical actions (like `click`) to verify the UI state changed as expected.
4.  **Action Priority Queue**: Enhance the `ToolRouter` with a priority-based rate limiter, allowing critical "STOP" or "READ" actions while throttling high-frequency "TYPE" or "CLICK" sequences.

## 🛠 Getting Started

### Prerequisites
- Python 3.12+
- Gemini API Key (set as `GEMINI_API_KEY` environment variable)
- Tesseract OCR installed on the system

### Installation
```bash
pip install -r requirements.txt
```

### Running the Agent
```bash
python main.py
```
