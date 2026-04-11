"""
This module provides functions to launch applications and URLs, and manage processes.
Every function in this module returns a dictionary with the following format:
{
    "ok": bool,      # True if the operation was successful, False otherwise.
    "result": str    # A descriptive message of the outcome or the error encountered.
}

If the global STOP_EVENT from FI_NEURAL_LINK.task_b_dashboard.panels.stop_panel is set,
all operations will be halted and return an error status.
"""

import subprocess
import webbrowser
import psutil
from FI_NEURAL_LINK.task_b_dashboard.panels.stop_panel import STOP_EVENT

def open_url(url: str) -> dict:
    """Opens the given URL in the default web browser."""
    if STOP_EVENT.is_set():
        return {"ok": False, "result": "Halted by STOP_EVENT"}

    if not (url.startswith("http://") or url.startswith("https://")):
        return {"ok": False, "result": "Invalid URL"}

    try:
        webbrowser.open(url)
        return {"ok": True, "result": f"Opened URL: {url}"}
    except Exception as e:
        return {"ok": False, "result": str(e)}

def launch_app(path: str, args: list = []) -> dict:
    """Launches an application with the given arguments."""
    if STOP_EVENT.is_set():
        return {"ok": False, "result": "Halted by STOP_EVENT"}

    try:
        subprocess.Popen([path] + args)
        return {"ok": True, "result": f"Launched app: {path} with args {args}"}
    except Exception as e:
        return {"ok": False, "result": str(e)}

def kill_process(name: str) -> dict:
    """Finds and terminates a process by its name."""
    if STOP_EVENT.is_set():
        return {"ok": False, "result": "Halted by STOP_EVENT"}

    try:
        killed_count = 0
        for proc in psutil.process_iter(['name']):
            if proc.info['name'] == name:
                proc.terminate()
                killed_count += 1

        if killed_count > 0:
            return {"ok": True, "result": f"Terminated {killed_count} process(es) named '{name}'"}
        else:
            return {"ok": False, "result": f"No process named '{name}' found"}
    except Exception as e:
        return {"ok": False, "result": str(e)}
