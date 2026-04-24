# FI_NEURAL_LINK: Neural Desktop Automation Agent

FI_NEURAL_LINK is a cyberpunk-themed, AI-powered desktop automation system that translates natural language commands into discrete OS-level actions. It features a strict dual-agent architecture designed for maximum efficiency, reliability, and low latency.

## 🛠 Project Structure

The project is organized into modular components:

- **`agents/`**: Contains the core logic for goal decomposition (`decomposer.py`) and the execution loop (`agent.py`).
- **`services/`**: Infrastructure services including LLM interaction (`llm_client.py`), caching (`cache.py`), and failure memory (`memory.py`).
- **`tools/`**: OS-level automation tools for windows control, browser navigation, and terminal execution.
- **`ui/`**: A cyberpunk-themed tkinter dashboard for interaction and monitoring.
- **`perception/`**: Screen capture and OCR capabilities.
- **`core/`**: System-wide configuration and safety guards.
- **`utils/`**: Helper utilities like JSON parsing.

## 🧠 Navigation & Automation Strategy

The system operates on a dual-agent model:

1.  **Router Brain**: A fast classifier that handles routine tasks or dispatches complex goals to the Executor.
2.  **Executor Agent**: Manages complex, multi-step tasks through a robust **Act → Observe → Decide** loop.

## 🛠 Getting Started

### Prerequisites
- Python 3.12+
- Gemini API Key (set as `GEMINI_API_KEY`)
- Tesseract OCR installed

### Installation
```bash
pip install -r requirements.txt
```

### Running the Agent
```bash
python main.py
```

## 🧠 Key Features
- **Intelligent Caching**: sub-100ms dispatch for recurring commands.
- **Loop Protection**: Prevents infinite execution loops in unpredictable UIs.
- **Cyberpunk HUD**: Real-time monitoring of agent activity and OS metrics.
- **Dual-Agent Architecture**: Balanced between speed and reliability.
