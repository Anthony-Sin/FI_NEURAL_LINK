# FI_NEURAL_LINK: Neural Desktop Automation Agent

FI_NEURAL_LINK is a cyberpunk-themed, AI-powered desktop automation system that translates natural language commands into discrete OS-level actions. It features a sophisticated dual-agent architecture for efficient and robust task execution.

## 🚀 Dual-Agent Architecture

The system utilizes two distinct AI agents to balance speed, cost, and reliability:

### 1. Router Brain (Classification & Dispatch)
Powered by **Gemini 2.5 Flash Lite**, this agent acts as a pure intent classifier:
- **Short Tasks**: For goals completable in a single tool call, it immediately emits the text description and function call.
- **Long Tasks**: For complex goals, it emits a structured **Handoff JSON** containing the goal, payload (e.g., items to iterate), and UI targets. It stop immediately without reasoning about steps.

### 2. Executor Agent Loop (Observe & Decide)
Powered by **Gemini 1.5 Pro**, this agent manages long-running, iterative tasks:
- **True Agent Loop**: After every tool call, it stops, observes the result, and decides the next move.
- **Decision Hierarchy**: It explicitly chooses between:
    1.  **Timer**: For deterministic waits (e.g., app launching).
    2.  **Screenshot**: For verifying unpredictable UI state changes.
    3.  **Read Screen (OCR)**: For extracting specific text from a region.
    4.  **Next Action**: For certain state transitions.
- **Continuation State**: If a task is unfinished, it emits a **Continuation JSON** to hand off the remaining queue and positional state to the next invocation.

## 🛠 Capabilities & Observation Strategy

### Observation Cost Awareness
The Executor Agent is trained to treat every observation call as expensive (Vision/Inference cost) and every timer as cheap. It always prefers the cheaper option (Timer) when latency is predictable.

### Browser-First UI Automation
The system prioritizes local UI inspection over visual models:
1.  **UI Automation (`click_element`, `type_in_element`)**: Preferred. Uses `pywinauto` to interact with elements by handle/name.
2.  **OCR (`read_screen`)**: Fallback for text extraction.
3.  **Vision (`analyze_screen`)**: Last resort for semantic understanding.

## 🧠 Continuation & Self-Calling Contract
Long tasks use a strict state contract. Each invocation is a stateless worker that receives a continuation object, performs one iteration of the loop, and either terminates or produces a new continuation object. This prevents token waste and keeps reasoning tightly scoped.

## ⚠️ Robust Fallbacks
- **Loading Spinners**: Extend timer and re-check.
- **CAPTCHA / Modals**: Pause for human intervention or attempt to dismiss.
- **Unexpected States**: Trigger recovery actions based on screenshot analysis.

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
