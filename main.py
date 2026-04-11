import os
import threading
from FI_NEURAL_LINK.task_b_dashboard.dashboard import Dashboard
from FI_NEURAL_LINK.task_c_tools.tool_router import ToolRouter
from FI_NEURAL_LINK.task_a_agent_brain.agent_core import AgentCore

def main():
    # 1. Initialize ToolRouter
    tool_router = ToolRouter()

    # 2. Initialize Dashboard
    dashboard = Dashboard()

    # 3. Setup AgentCore Configuration
    config = {
        "gemini_api_key": os.environ.get("GEMINI_API_KEY", "MOCK_KEY"),
        "max_retries": 3,
        "loop_window": 5
    }

    # 4. Initialize AgentCore
    # We pass the dashboard.log method as the log_callback
    agent = AgentCore(config, tool_router=tool_router, log_callback=dashboard.log)

    # 5. Define the submission handler
    def handle_submit(goal):
        dashboard.log(f"Received goal: {goal}", "info")

        # Run the agent in a separate thread to keep the UI responsive
        def run_agent():
            try:
                agent.run_goal(goal)
            except Exception as e:
                dashboard.log(f"Agent error: {str(e)}", "error")

        agent_thread = threading.Thread(target=run_agent, daemon=True)
        agent_thread.start()

    # 6. Connect Dashboard to the handler
    dashboard.set_on_submit(handle_submit)

    # 7. Start the Dashboard
    dashboard.log("FI_NEURAL_LINK Initialized. Awaiting command...", "info")

    print("Dashboard initialized. Launching GUI...")

    # We use the root mainloop directly in the main thread to ensure the process exits when the window is closed.
    # Note: dashboard.start() used to launch it in a daemon thread, but we'll use this approach instead.
    dashboard.root.mainloop()

if __name__ == "__main__":
    main()
