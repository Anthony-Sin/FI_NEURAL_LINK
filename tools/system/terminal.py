import subprocess
import json
import os

def load_terminal_config():
    config_path = os.path.join("data", "terminal_config.json")
    if os.path.exists(config_path):
        with open(config_path, "r") as f:
            return json.load(f)
    # Default strict fallback
    return {
        "access_level": "LOW",
        "levels": {
            "LOW": {"whitelist": ["dir", "ls", "echo"], "blacklist": ["rm", "del"]}
        }
    }

def execute_command(command: str) -> dict:
    """Executes a PowerShell command based on the configured security level."""
    config = load_terminal_config()
    level = config.get("access_level", "LOW")
    level_rules = config.get("levels", {}).get(level, {})

    whitelist = level_rules.get("whitelist", [])
    blacklist = level_rules.get("blacklist", [])

    # Validation
    if level != "FULL":
        # Check blacklist first
        for blocked in blacklist:
            if blocked in command.lower():
                return {"ok": False, "result": f"Command blocked by blacklist for level {level}: {blocked}"}

        # Check whitelist
        if "*" not in whitelist:
            allowed = False
            for white in whitelist:
                if command.lower().startswith(white.lower()):
                    allowed = True
                    break
            if not allowed:
                return {"ok": False, "result": f"Command not in whitelist for level {level}"}

    try:
        # Execute via PowerShell
        process = subprocess.Popen(
            ["powershell", "-Command", command],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )
        stdout, stderr = process.communicate(timeout=30)

        if process.returncode == 0:
            return {"ok": True, "result": stdout.strip() or "Command executed successfully (no output)."}
        else:
            return {"ok": False, "result": stderr.strip() or f"Command failed with exit code {process.returncode}"}

    except subprocess.TimeoutExpired:
        process.kill()
        return {"ok": False, "result": "Command timed out after 30 seconds."}
    except Exception as e:
        return {"ok": False, "result": f"Terminal execution error: {str(e)}"}
