# FI_NEURAL_LINK Testing System

This directory contains the testing suite for the Neural Desktop Automation Agent. Due to the nature of the project (OS-level automation), many components require a GUI environment which is not available in all CI/CD contexts.

## 📁 Structure
- `unit/`: Pure logic tests (LLM parsing, cache logic, security filters).
- `mocks/`: Infrastructure for mocking `pywinauto`, `pyautogui`, and `mss` to allow "headless" testing of automation logic.

## 🧪 Running Tests
```bash
pytest
```

## 🛠 Mocking Strategy
We use `unittest.mock` and custom mock fixtures in `conftest.py` to intercept calls to hardware-dependent libraries. This allows us to verify that the `AgentCore` is emitting the correct instructions even when the actions aren't physically performed.
