import os
import threading
import time
from FI_NEURAL_LINK.task_b_dashboard.dashboard import Dashboard
from FI_NEURAL_LINK.task_c_tools.tool_router import ToolRouter
from FI_NEURAL_LINK.task_a_agent_brain.agent_core import AgentCore

def main():
    # 1. Initialize ToolRouter
    tool_router = ToolRouter()

    # 2. Initialize Dashboard (creates the Tk root, but does NOT start mainloop yet)
    dashboard = Dashboard()

    # 3. Setup AgentCore Configuration
    config = {
        "gemini_api_key": os.environ.get("GEMINI_API_KEY", "MOCK_KEY"),
        "max_retries": 3,
        "loop_window": 5
    }

    # 4. Initialize AgentCore
    agent = AgentCore(config, tool_router=tool_router, log_callback=dashboard.log)

    # 5. Define the submission handler
    def handle_submit(goal):
        dashboard.log(f"Received goal: {goal}", "info")

        def run_agent():
            try:
                agent.run_goal(goal)
            except Exception as e:
                dashboard.log(f"Agent error: {str(e)}", "error")

        threading.Thread(target=run_agent, daemon=True).start()

    # 6. Connect Dashboard to the handler
    dashboard.set_on_submit(handle_submit)

    # 7. Log and then run mainloop ON THE MAIN THREAD
    dashboard.log("FI_NEURAL_LINK Initialized. Awaiting command...", "info")
    print("Dashboard initialized. Entry point ready.")

    # This blocks here on the main thread — which is exactly what Tkinter needs on Windows
    dashboard.root.mainloop()

if __name__ == "__main__":
    main()