# FI_NEURAL_LINK: Neural Desktop Automation Agent

FI_NEURAL_LINK is a cyberpunk-themed, AI-powered desktop automation system that translates natural language commands into discrete OS-level actions. It features a strict dual-agent architecture designed for maximum efficiency and reliability.

## 🚀 Strict Dual-Agent Architecture

### 1. Router Brain (Classification & Dispatch)
Powered by **Gemini 2.5 Flash Lite**, this agent acts as a pure intent classifier:
- **Single Reasoning Pass**: Receives raw user goals and classifies them as short or long.
- **Short Tasks**: Emits a `text` summary and a list of `function_calls` for immediate sequential execution.
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

## 🧠 Navigation & Web Analysis Strategy
The agent follows a strict protocol for web-based tasks:
1.  **Webpage Structure Extraction**: When navigating to a URL, the agent MUST call `save_webpage_structure`. This tool uses `BeautifulSoup` to extract interactive elements (buttons, inputs, links) and saves a `webpage_structure.json` file in the root directory.
2.  **Locality over Vision**: The agent prioritizes searching the saved structure to find element titles and attributes for local UI Automation.

## ⚠️ Unexpected UI State Handling
The system implements fully realized logic for messy real-world UIs:
- **Loading Spinners**: Extend timers and re-verify via screenshot.
- **Error Detection**: Automatic screenshot capture and recovery attempts based on error text.
- **CAPTCHAs**: Immediate pause and signal for human intervention (`human_intervention_required`).
- **Unexpected Modals**: Attempted dismissal via UI automation and re-verification.

## 🧠 Capabilities & Tool Priority
1.  **UI Automation (`click_element`, `type_in_element`)**: Primary method for browser-based tasks.
2.  **OCR (`read_screen`)**: Secondary fallback for text extraction.
3.  **Vision (`analyze_screen`)**: Final fallback for semantic understanding.

## 🚩 Limitations
- **Brittle Scraping**: `save_webpage_structure` uses `requests`, which may fail on authenticated or dynamic JavaScript-heavy pages where a real browser session is required.
- **Stateless Router**: The Router Brain does not have access to previous execution results, which can lead to suboptimal routing if a task evolves.
- **Minimal Feedback in Short Tasks**: Short tasks execute a fire-and-forget sequence without intermediate observation, unlike the robust Executor Agent loop.

## 💡 Architectural Suggestions for Improvement
1.  **In-Browser Scraper**: Replace the `requests`-based scraper with a UI Automation script that extracts the DOM directly from the active Microsoft Edge/Chrome window to preserve user sessions and cookies.
2.  **Multimodal Router**: Feed a current screen thumbnail into the Router Brain to allow it to make better "Short" vs "Long" decisions based on the actual UI state.
3.  **Unified State Machine**: Merge the short and long task execution paths into a single state machine where the Router Brain simply initializes the state for the Executor Agent.

## 🛠 Getting Started

### Prerequisites
- Python 3.12+
- Gemini API Key (set as `GEMINI_API_KEY` environment variable)
- Tesseract OCR installed on the system

### Installation
```bash
pip install -r requirements.txt
pip install beautifulsoup4 requests
```

### Running the Agent
```bash
python main.py
```
