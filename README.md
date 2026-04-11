# FI_NEURAL_LINK: Neural Desktop Automation Agent

FI_NEURAL_LINK is a cyberpunk-themed, AI-powered desktop automation system that translates natural language commands into discrete OS-level actions. It features a strict dual-agent architecture designed for maximum efficiency and reliability.

## 🚀 Strict Dual-Agent Architecture

### 1. Router Brain (Classification & Dispatch)
Powered by **Gemini 2.5 Flash Lite**, this agent acts as a pure intent classifier:
- **Single Reasoning Pass**: Receives raw user goals and classifies them as short or long.
- **Short Tasks**: Emits a single `text` + `function_call` block for immediate execution.
- **Long Tasks**: Emits only a **Handoff JSON** with no execution, reasoning, or step listing.
- **Contract**: "If the task requires more than one tool call or requires waiting for a UI response, stop immediately and emit only the handoff JSON. Do not begin execution."

### 2. Executor Agent (Observe & Decide)
Powered by **Gemini 1.5 Pro**, this agent manages complex, iterative tasks through a robust loop:
- **Agent Loop**: Act → Observe → Decide → Act.
- **Explicit Observation Strategy**: After every tool call, the model chooses one of:
    1.  **timer**: Preferred for predictable latency (cheap).
    2.  **screenshot**: Used for unpredictable outcomes (expensive vision inference).
    3.  **read_screen (OCR)**: Used for extracting specific text.
    4.  **next_action**: Used for fully deterministic transitions.
- **Decision Hierarchy**: Baked into the system prompt to enforce cost-aware observation.

## 🧠 Continuation & Self-Calling Contract
Long tasks maintain state via a strict continuation contract:
- **Stateless Invocations**: Each call is a single iteration.
- **Continuation JSON**: Contains only the remaining queue, last action result, UI target, and current position.
- **Two System Prompts**: Separate "Start" and "Resume" prompts ensure the model never re-plans from scratch or wastes tokens on redundant history.

## 🛠 Unexpected UI State Handling
The system implements fully realized logic for messy real-world UIs:
- **Loading Spinners**: Extend timers and re-verify via screenshot.
- **Error Detection**: Automatic screenshot capture and recovery attempts based on error text.
- **CAPTCHAs**: Immediate pause and signal for human intervention (`human_intervention_required`).
- **Unexpected Modals**: Attempted dismissal via UI automation and re-verification.

## 🧠 Capabilities & Tool Priority
1.  **UI Automation (`click_element`, `type_in_element`)**: Primary method for browser-based tasks.
2.  **OCR (`read_screen`)**: Secondary fallback for text extraction.
3.  **Vision (`analyze_screen`)**: Final fallback for semantic understanding.

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
