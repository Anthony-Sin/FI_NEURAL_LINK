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

        threading.Thread(target=run_agent, daemon=True).start()

    # 6. Connect Dashboard to the handler
    dashboard.set_on_submit(handle_submit)

    # 7. Start the Dashboard
    dashboard.log("FI_NEURAL_LINK Initialized. Awaiting command...", "info")

    # In this environment, we might not be able to actually run the tkinter mainloop
    # so we'll just print a message.
    print("Dashboard initialized. Entry point ready.")

    # For actual usage, you would call:
    # dashboard.root.mainloop()
    # But dashboard.start() already launches it in a thread.
    dashboard.start()

    # Keep the main thread alive if needed, or just let it finish if dashboard.start() is enough.
    # Since dashboard.start() uses a daemon thread, we should probably keep the main thread alive.
    import time
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("Shutting down...")

if __name__ == "__main__":
    main()
