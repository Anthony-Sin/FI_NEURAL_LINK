import threading
import os
from dotenv import load_dotenv
from tools.router import ToolRouter
from tools.security.credentials import get_api_key
from agents.agent import AgentCore
from ui.main_window import Dashboard

def main():
    # Load environment variables from .env
    load_dotenv()

    # 1. Initialize ToolRouter
    tool_router = ToolRouter()

    # 2. Initialize Dashboard
    dashboard = Dashboard()

    # 3. Setup AgentCore Configuration
    try:
        api_key = get_api_key("GEMINI_API_KEY")
    except EnvironmentError:
        api_key = "MOCK_KEY"

    config = {
        "gemini_api_key": api_key,
        "max_retries": 3,
        "loop_window": 5
    }

    # 4. Initialize AgentCore
    # We pass the dashboard.log method as the log_callback
    agent = AgentCore(config, tool_router=tool_router, log_callback=dashboard.log)

    # 5. Define the submission handler
    def handle_submit(goal, extra_context=None):
        dashboard.log(f"Received goal: {goal}", "info")

        # Run the agent in a separate thread to keep the UI responsive
        def run_agent():
            try:
                agent.run_goal(goal, extra_context=extra_context)
            except Exception as e:
                dashboard.log(f"Agent error: {str(e)}", "error")

        agent_thread = threading.Thread(target=run_agent, daemon=True)
        agent_thread.start()

    # 6. Connect Dashboard to the handler
    dashboard.set_on_submit(handle_submit)

    # 7. Start the Dashboard

    print("Dashboard initialized. Launching GUI...")
    dashboard.root.deiconify() # Only show the overlay window

    # We use the root mainloop directly in the main thread to ensure the process exits when the window is closed.
    # Note: dashboard.start() used to launch it in a daemon thread, but we'll use this approach instead.
    dashboard.root.mainloop()

if __name__ == "__main__":
    main()
