import os
import re
import json
import shutil
try:
    import winreg
except ImportError:
    winreg = None
import logging
from difflib import get_close_matches
from agents.decomposer import route_goal, parse_decision
from services.llm_client import generate_response
from utils.json_parser import parse_llm_json
from core.guard import LoopGuard
from services.cache import CacheManager
from core.config import get_model
from ui.panels.stop_panel import STOP_EVENT
from tools.automation.recorder import get_recorded_summary

# ---------------------------------------------------------------------------
# APP ALIAS MAP
# Keys are lowercase natural names Gemini might output.
# Values are the exe name used to look up via PATH / Registry at runtime.
# ---------------------------------------------------------------------------
APP_ALIASES: dict[str, str] = {
    # ── Browsers ────────────────────────────────────────────────────────────
    "chrome":                   "chrome.exe",
    "google chrome":            "chrome.exe",
    "chromium":                 "chromium.exe",
    "firefox":                  "firefox.exe",
    "mozilla firefox":          "firefox.exe",
    "edge":                     "msedge.exe",
    "microsoft edge":           "msedge.exe",
    "opera":                    "opera.exe",
    "brave":                    "brave.exe",
    "brave browser":            "brave.exe",
    "vivaldi":                  "vivaldi.exe",
    "tor browser":              "firefox.exe",       # Tor is Firefox-based

    # ── Microsoft Office ────────────────────────────────────────────────────
    "word":                     "WINWORD.EXE",
    "microsoft word":           "WINWORD.EXE",
    "excel":                    "EXCEL.EXE",
    "microsoft excel":          "EXCEL.EXE",
    "powerpoint":               "POWERPNT.EXE",
    "microsoft powerpoint":     "POWERPNT.EXE",
    "outlook":                  "OUTLOOK.EXE",
    "microsoft outlook":        "OUTLOOK.EXE",
    "onenote":                  "ONENOTE.EXE",
    "microsoft onenote":        "ONENOTE.EXE",
    "access":                   "MSACCESS.EXE",
    "microsoft access":         "MSACCESS.EXE",
    "publisher":                "MSPUB.EXE",
    "teams":                    "Teams.exe",
    "microsoft teams":          "Teams.exe",

    # ── Windows Built-ins ───────────────────────────────────────────────────
    "notepad":                  "notepad.exe",
    "wordpad":                  "wordpad.exe",
    "calculator":               "calc.exe",
    "calc":                     "calc.exe",
    "paint":                    "mspaint.exe",
    "ms paint":                 "mspaint.exe",
    "file explorer":            "explorer.exe",
    "explorer":                 "explorer.exe",
    "task manager":             "Taskmgr.exe",
    "control panel":            "control.exe",
    "settings":                 "ms-settings:",     # URI scheme
    "cmd":                      "cmd.exe",
    "command prompt":           "cmd.exe",
    "powershell":               "powershell.exe",
    "windows powershell":       "powershell.exe",
    "powershell 7":             "pwsh.exe",
    "pwsh":                     "pwsh.exe",
    "registry editor":          "regedit.exe",
    "regedit":                  "regedit.exe",
    "snipping tool":            "SnippingTool.exe",
    "snip":                     "SnippingTool.exe",
    "sticky notes":             "stikynot.exe",
    "character map":            "charmap.exe",
    "disk cleanup":             "cleanmgr.exe",
    "defragment":               "dfrgui.exe",
    "event viewer":             "eventvwr.exe",
    "device manager":           "devmgmt.msc",
    "disk management":          "diskmgmt.msc",
    "services":                 "services.msc",
    "msconfig":                 "msconfig.exe",
    "system info":              "msinfo32.exe",
    "remote desktop":           "mstsc.exe",
    "magnifier":                "magnify.exe",
    "narrator":                 "Narrator.exe",
    "on screen keyboard":       "osk.exe",
    "clock":                    "timedate.cpl",
    "sound":                    "mmsys.cpl",

    # ── Code Editors / IDEs ─────────────────────────────────────────────────
    "vs code":                  "Code.exe",
    "vscode":                   "Code.exe",
    "visual studio code":       "Code.exe",
    "visual studio":            "devenv.exe",
    "pycharm":                  "pycharm64.exe",
    "intellij":                 "idea64.exe",
    "intellij idea":            "idea64.exe",
    "android studio":           "studio64.exe",
    "sublime text":             "sublime_text.exe",
    "sublime":                  "sublime_text.exe",
    "atom":                     "atom.exe",
    "notepad++":                "notepad++.exe",
    "vim":                      "vim.exe",
    "neovim":                   "nvim.exe",
    "cursor":                   "cursor.exe",

    # ── Communication ───────────────────────────────────────────────────────
    "discord":                  "Discord.exe",
    "slack":                    "slack.exe",
    "zoom":                     "Zoom.exe",
    "skype":                    "Skype.exe",
    "telegram":                 "Telegram.exe",
    "whatsapp":                 "WhatsApp.exe",
    "signal":                   "Signal.exe",

    # ── Media ───────────────────────────────────────────────────────────────
    "spotify":                  "Spotify.exe",
    "vlc":                      "vlc.exe",
    "vlc media player":         "vlc.exe",
    "windows media player":     "wmplayer.exe",
    "media player":             "wmplayer.exe",
    "itunes":                   "iTunes.exe",
    "audacity":                 "audacity.exe",
    "obs":                      "obs64.exe",
    "obs studio":               "obs64.exe",
    "handbrake":                "HandBrake.exe",

    # ── Image / Design ──────────────────────────────────────────────────────
    "photoshop":                "Photoshop.exe",
    "adobe photoshop":          "Photoshop.exe",
    "illustrator":              "Illustrator.exe",
    "adobe illustrator":        "Illustrator.exe",
    "premiere":                 "Adobe Premiere Pro.exe",
    "adobe premiere":           "Adobe Premiere Pro.exe",
    "after effects":            "AfterFX.exe",
    "lightroom":                "lightroom.exe",
    "gimp":                     "gimp-2.10.exe",
    "inkscape":                 "inkscape.exe",
    "figma":                    "Figma.exe",
    "blender":                  "blender.exe",

    # ── Utilities ───────────────────────────────────────────────────────────
    "7zip":                     "7zFM.exe",
    "7-zip":                    "7zFM.exe",
    "winrar":                   "WinRAR.exe",
    "winzip":                   "winzip64.exe",
    "steam":                    "steam.exe",
    "epic games":               "EpicGamesLauncher.exe",
    "epic":                     "EpicGamesLauncher.exe",
    "battle.net":               "Battle.net.exe",
    "nvidia control panel":     "nvcplui.exe",
    "afterburner":              "MSIAfterburner.exe",
    "cpu-z":                    "cpuz_x64.exe",
    "gpu-z":                    "GPU-Z.exe",
    "hwinfo":                   "HWiNFO64.exe",
    "putty":                    "putty.exe",
    "winscp":                   "WinSCP.exe",
    "filezilla":                "filezilla.exe",
    "virtualbox":               "VirtualBox.exe",
    "vmware":                   "vmware.exe",
    "docker":                   "Docker Desktop.exe",
    "postman":                  "Postman.exe",
    "insomnia":                 "Insomnia.exe",
    "git":                      "git.exe",
    "github desktop":           "GitHubDesktop.exe",
    "sourcetree":               "SourceTree.exe",
    "winmerge":                 "WinMerge.exe",
    "everything":               "Everything.exe",
    "powertoys":                "PowerToys.exe",
    "autohotkey":               "AutoHotkeyU64.exe",
    "malwarebytes":             "MBAMService.exe",
    "ccleaner":                 "CCleaner64.exe",
    "recuva":                   "Recuva64.exe",
    "crystaldiskinfo":          "DiskInfo64.exe",
    "bitwarden":                "Bitwarden.exe",
    "keepass":                  "KeePass.exe",
    "notion":                   "Notion.exe",
    "obsidian":                 "Obsidian.exe",
    "onenote":                  "ONENOTE.EXE",
    "anki":                     "anki.exe",
    "calibre":                  "calibre.exe",
    "kindle":                   "Kindle.exe",
}

# Keys exposed to Gemini in the decomposer prompt (short, clean list)
GEMINI_APP_KEYS: list[str] = sorted(APP_ALIASES.keys())


# ---------------------------------------------------------------------------
# APP RESOLVER
# ---------------------------------------------------------------------------

def _registry_lookup(exe_name: str) -> str | None:
    """Look up an exe in HKLM\\SOFTWARE\\Microsoft\\Windows\\CurrentVersion\\App Paths."""
    if winreg is None:
        return None
    try:
        key_path = rf"SOFTWARE\Microsoft\Windows\CurrentVersion\App Paths\{exe_name}"
        with winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, key_path) as key:
            path, _ = winreg.QueryValueEx(key, "")
            if path and os.path.isfile(path):
                return path
    except (FileNotFoundError, OSError, AttributeError):
        pass
    return None


def resolve_app_path(name: str) -> str | None:
    """
    Resolve a natural-language app name or exe name to a full path.

    Resolution order:
      1. Already a valid file path → use as-is
      2. Exact match in APP_ALIASES → get exe name, then try 3-5
      3. Fuzzy match in APP_ALIASES (handles Gemini typos) → get exe name, then try 4-5
      4. shutil.which() → found on system PATH
      5. Windows Registry App Paths lookup
    """
    # 1. Already a real path
    if os.path.isfile(name):
        return name

    name_lower = name.lower().strip()

    # 2. Exact alias lookup
    exe = APP_ALIASES.get(name_lower)

    # 3. Fuzzy alias lookup (catches "chome", "gogle chrome", etc.)
    if not exe:
        matches = get_close_matches(name_lower, APP_ALIASES.keys(), n=1, cutoff=0.6)
        if matches:
            exe = APP_ALIASES[matches[0]]

    # If still nothing, treat name itself as the exe
    if not exe:
        exe = name if name.lower().endswith(".exe") else name + ".exe"

    # Check if it is a URI scheme from aliases
    if ":" in exe and not os.path.isabs(exe) and not exe.startswith((".", "\\", "/")):
        return exe

    # 4. PATH lookup
    found = shutil.which(exe)
    if found:
        return found

    # 5. Registry lookup
    found = _registry_lookup(exe)
    if found:
        return found

    return None


# ---------------------------------------------------------------------------
# DASHBOARD LOG HANDLER
# ---------------------------------------------------------------------------

class DashboardLogHandler(logging.Handler):
    """Custom logging handler to send logs to the dashboard callback."""

    def __init__(self, callback):
        super().__init__()
        self.callback = callback

    def emit(self, record):
        try:
            msg = self.format(record)
            level = record.levelname.lower()
            retry_count = getattr(record, 'retry_count', 0)
            api_calls = getattr(record, 'api_calls', 0)
            # Support passing extra data to callback if it supports it
            try:
                self.callback(msg, level, retry_count=retry_count, api_calls=api_calls)
            except TypeError:
                self.callback(msg, level)
        except Exception:
            self.handleError(record)


# ---------------------------------------------------------------------------
# AGENT CORE
# ---------------------------------------------------------------------------

class AgentCore:
    """
    Core agent class that manages goal decomposition and execution with loop protection.
    """

    def __init__(self, config: dict, tool_router=None, log_callback=None):
        self._is_busy = False
        self.error_retry_count = 0
        self.max_error_retries = 3
        self.total_api_calls = 0
        """
        Initializes the AgentCore.
        """
        self.config = config
        os.environ["GEMINI_API_KEY"] = config.get("gemini_api_key", "")
        self.loop_guard = LoopGuard(n=config.get("loop_window", 5))
        self.cache_mgr = CacheManager()
        self.cache_mgr.load_cache()
        self.tool_router = tool_router
        self._setup_logging(log_callback)

    # ── Logging ─────────────────────────────────────────────────────────────

    def _setup_logging(self, log_callback):
        self.logger = logging.getLogger("AgentCore")
        self.logger.setLevel(logging.DEBUG)

        if not self.logger.handlers:
            fh = logging.FileHandler("agent_execution.log", encoding="utf-8")
            fh.setLevel(logging.DEBUG)
            fh.setFormatter(logging.Formatter(
                '[%(asctime)s] [%(levelname)s] %(message)s',
                datefmt='%Y-%m-%d %H:%M:%S'
            ))
            self.logger.addHandler(fh)

            if log_callback:
                dh = DashboardLogHandler(log_callback)
                dh.setLevel(logging.INFO)
                dh.setFormatter(logging.Formatter('%(message)s'))
                self.logger.addHandler(dh)
            else:
                ch = logging.StreamHandler()
                ch.setLevel(logging.INFO)
                ch.setFormatter(logging.Formatter('[%(levelname)s] %(message)s'))
                self.logger.addHandler(ch)

    def log(self, text, level="info"):
        """Directly uses the logger instance."""
        # Check if the log callback is a dashboard log to pass extra info
        # We use a hacky way to check if it's the dashboard.log by checking its __name__ or just try to pass it

        level_map = {
            "debug":    logging.DEBUG,
            "info":     logging.INFO,
            "warning":  logging.WARNING,
            "error":    logging.ERROR,
            "critical": logging.CRITICAL,
        }

        # We want to pass extra info if possible, but logging.log doesn't support it directly.
        # The DashboardLogHandler will handle it if we add it to the record.
        self.logger.log(level_map.get(level.lower(), logging.INFO), text, extra={
            'retry_count': self.error_retry_count,
            'api_calls': getattr(self, 'total_api_calls', 0)
        })

    # ── Goal Execution ──────────────────────────────────────────────────────

    def run_goal(self, goal: str) -> list:
        """
        Routes a goal and executes it using the RouterBrain/ExecutorAgent architecture.
        """
        self.log("="*60, "debug")
        self.log(f"NEW GOAL RECEIVED: {goal.upper()}")
        self.log("="*60, "debug")
        self.error_retry_count = 0
        self.total_api_calls = 0
        if self._is_busy:
            self.log("AGENT IS CURRENTLY BUSY. QUEUEING REJECTED.", "warning")
            return []

        self._is_busy = True
        try:
            res = self._perform_goal(goal)
            self.log("Goal execution finalized. Returning to IDLE.")
            return res
        finally:
            self._is_busy = False
            self.log("IDLE", "debug")

    def _get_context_block(self) -> str:
        """Constructs a context block describing the current system state."""
        context = ["CURRENT SYSTEM CONTEXT:"]

        # 1. Active Window
        try:
            from pywinauto import Desktop
            active_win = Desktop(backend="uia").windows(enabled_only=True, visible_only=True)[0]
            context.append(f"- Active Window: '{active_win.window_text()}'")
        except:
            context.append("- Active Window: Unknown")

        # 2. Recording Status — only if a recording actually exists
        from tools.automation.recorder import recorder_instance
        if recorder_instance.events:
            import re
            summary = get_recorded_summary()

            # Normalize contenteditable/group clicks — inject explicit focus + type steps
            # so the model knows to steal focus from tk before typing
            summary = re.sub(
                r"Clicked (?:Edit|Group) '[￼\s]*' at \((\d+), (\d+)\) in (.+?)\n([\s\S]*)",
                lambda m: (
                    f"USE_EXACTLY: click(x={m.group(1)}, y={m.group(2)}) "
                    f"THEN wait(seconds=1) THEN type_text(text=<new_text>)\n"
                    f"REMAINING_ACTIONS:\n{m.group(4)}"
                ),
                summary
            )
            # Strip actions that happened in the agent's own tk window —
            # these are interactions with the agent UI itself, not the target app
            summary = re.sub(r".*\bin tk\b.*\n?", "", summary)

            context.append("- Active Recording detected.")
            context.append(f"- Recorded Actions Summary (Use these exact coordinates for focus):\n{summary}")

            # Logic to help model focus: if last recorded action was a click on an Edit field,
            # and current goal is 'this time type X', we should explicitly suggest clicking those coordinates.
            # This is handled by the model seeing the summary, but we add a hint.
            context.append("\nFOCUS HINT: If replaying/varying a recording, ALWAYS use 'click(x, y)' on the same coordinates where the original click occurred to ensure input focus.")

        return "\n".join(context)
    def _perform_goal(self, goal: str) -> list:
        self.current_goal = goal # Store for retries
        self.log(f"Routing goal: {goal}")
        self.loop_guard.reset()

        # 0. Construct context for the Router
        context_block = self._get_context_block()
        self.logger.debug(f"ROUTING CONTEXT:\n{context_block}")

        # 1. Check cache first
        try:
            cached_plan = self.cache_mgr.match_and_reconstruct(goal)
            if cached_plan:
                self.log("CACHE HIT! Executing macro plan...", "debug")
                # Convert to 'short task' format for _execute_short_task
                decision = {"text": "Executing cached plan", "function_calls": cached_plan}
                results = self._perform_short_task(decision)
                self.cache_mgr.save_cache() # Persist hits
                return results
        except Exception as e:
            self.log(f"Cache matching error: {str(e)}", "warning")

        try:
            cache_block = self.cache_mgr.get_cache_block()
            self.total_api_calls += 1
            # Pass context_block to route_goal
            raw_decision = route_goal(goal, cache_block=cache_block, context_block=context_block)
            self.log(f"RAW ROUTER RESPONSE: {raw_decision}", "debug")
            decision = parse_decision(raw_decision)
        except Exception as e:
            self.log(f"Routing failed: {str(e)}", "error")
            return []

        if "function_call" in decision or "function_calls" in decision:
            results = self._perform_short_task(decision)
            # Record success for cache (Silent)
            if results and all(r["status"] == "completed" for r in results):
                f_calls = decision.get("function_calls") or [decision.get("function_call")]
                f_calls = [f for f in f_calls if f]
                if f_calls:
                    self.cache_mgr.record_success(goal, f_calls)
                    self.cache_mgr.save_cache()
            return results
        elif decision.get("task_type") == "long":
            # Hand off to long task without nesting another busy check
            return self._perform_long_task(decision)
        elif decision.get("task_type") == "replay_recording":
            return self._perform_recording_replay(decision)
        else:
            self.log(f"Unknown decision format: {json.dumps(decision)}", "error")
            return []

    def _execute_short_task(self, decision: dict) -> list:
        """Public wrapper for short task execution."""
        if self._is_busy: return []
        self._is_busy = True
        try:
            return self._perform_short_task(decision)
        finally:
            self._is_busy = False

    def _perform_short_task(self, decision: dict) -> list:
        """Executes a short task immediately via one or more function_calls."""
        text = decision.get("text", "Executing short task")
        self.log(f"Short Task: {text}")

        f_calls = decision.get("function_calls", [])
        if "function_call" in decision:
            f_calls.append(decision["function_call"])

        results = []
        for f_call in f_calls:
            name = f_call.get("name")
            args = f_call.get("args", {})

            # Resolve path for launch_app if needed
            if name == "launch_app" and "path" in args:
                resolved = resolve_app_path(args["path"])
                if resolved:
                    args["path"] = resolved
                    self.log(f"Resolved app path: {resolved}", "debug")

            if self.tool_router:
                tool_result = self.tool_router.execute(name, args)
                status = "completed" if tool_result.get("ok") else "failed"
                self.log(f"Step {name} Result: {tool_result.get('result')}", "info" if tool_result.get("ok") else "error")
                results.append({"description": f"Executed {name}", "status": status, "result": tool_result.get("result")})

                if not tool_result.get("ok"):
                    self.error_retry_count += 1
                    if self.error_retry_count > self.max_error_retries:
                        self.log(f"Reached maximum of {self.max_error_retries} error retries. Shutting down.", "error")
                        print("CRITICAL: could not do task on the terminal", flush=True)
                        break

                    # User requested to ask for help on failure
                    from services.llm_client import request_user_input
                    self.log(f"Step {name} failed: {tool_result.get('result')}. Requesting user intervention.", "warning")
                    user_resp = request_user_input(f"Action '{name}' failed with error: {tool_result.get('result')}. How should I proceed? (Type 'exit' to shut down)")

                    if not user_resp or user_resp.lower() == 'exit':
                        self.log("No response or exit command received. Shutting down task.", "error")
                        print("CRITICAL: could not do task on the terminal", flush=True)
                        break
                    else:
                        self.log(f"Received user instruction: {user_resp}. Retrying goal with new context.")
                        # Use stored goal for retries
                        original_goal = getattr(self, 'current_goal', "unknown goal")
                        return self._perform_goal(f"{original_goal} (Correction: {user_resp})")
            else:
                results.append({"description": f"Executed {name}", "status": "failed", "result": "No tool router"})
                break

        return results

    def _execute_long_task(self, handoff: dict) -> list:
        """Public wrapper for long task execution."""
        if self._is_busy: return []
        self._is_busy = True
        try:
            return self._perform_long_task(handoff)
        finally:
            self._is_busy = False

    def _perform_long_task(self, handoff: dict) -> list:
        """Executes a long task using the strict iterative ExecutorAgent loop."""
        self.log(f"Long Task detected. Handing off to Executor loop.")

        continuation = {
            "goal": handoff.get("goal"),
            "ui_target": handoff.get("ui_target"),
            "remaining_queue": handoff.get("iterable_payload", []),
            "parameters": handoff.get("parameters", {}),
            "last_action_result": None,
            "current_position": 0,
            "status": "starting"
        }

        results = []
        try:
            while not STOP_EVENT.is_set():
                # 1. GENERATE NEXT STEP (Act)
                self.total_api_calls += 1
                executor_output = self._call_executor(continuation)

                if executor_output.get("status") == "terminated":
                    self.log("Goal achieved. Terminating.")
                    break

                if executor_output.get("status") == "human_intervention_required":
                    self.log(f"PAUSED: {executor_output.get('reason')}", "warning")
                    break

                # 2. EXECUTE STEP
                action_desc = executor_output.get("description", "")
                f_call = executor_output.get("function_call", {})
                tool_name = f_call.get("name")
                args = f_call.get("args", {})

                # Resolve path for launch_app if needed
                if tool_name == "launch_app" and "path" in args:
                    resolved = resolve_app_path(args["path"])
                    if resolved:
                        args["path"] = resolved
                        self.log(f"Resolved app path: {resolved}", "debug")

                self.log(f"Executor Action: {action_desc} (Tool: {tool_name})")

                # Loop detection
                if self.loop_guard.check_loop(action_desc):
                    self.log(f"CRITICAL: Infinite loop detected during action: {action_desc}. Halting execution for safety.", "error")
                    raise RuntimeError(f"Infinite loop detected: {action_desc}")
                self.loop_guard.record_action(action_desc)

                if self.tool_router:
                    tool_result = self.tool_router.execute(tool_name, args)

                    if not tool_result.get("ok"):
                        self.error_retry_count += 1
                        if self.error_retry_count > self.max_error_retries:
                            self.log(f"Reached maximum of {self.max_error_retries} error retries. Shutting down.", "error")
                            print("CRITICAL: could not do task on the terminal", flush=True)
                            break

                        from services.llm_client import request_user_input
                        self.log(f"Executor step failed: {tool_result.get('result')}. Requesting user intervention.", "warning")
                        user_resp = request_user_input(f"Action '{tool_name}' failed: {tool_result.get('result')}. How should I proceed? (Type 'exit' to shut down)")

                        if not user_resp or user_resp.lower() == 'exit':
                            self.log("No response or exit command received. Shutting down task.", "error")
                            print("CRITICAL: could not do task on the terminal", flush=True)
                            break
                        else:
                            self.log(f"Received user instruction: {user_resp}. Updating goal context.")
                            continuation["goal"] = f"{continuation['goal']} (Correction: {user_resp})"
                            # Continue loop with updated goal
                            continuation["last_action_result"] = f"User corrected: {user_resp}"
                            continue

                    continuation["last_action_result"] = tool_result.get("result")

                    # 3. OBSERVE & DECIDE (the model chooses in its next turn, but we verify here)
                    # We pass the result back to the model in the next continuation

                    # Check for unexpected UI states if result was a failure or observation was requested
                    # (In a real system, we'd fire an observation tool immediately if the model requested it)
                    # For this implementation, the model decides the observation tool in its turn.

                    # 4. UPDATE CONTINUATION
                    # Update queue and position if model indicated it
                    continuation.update(executor_output.get("continuation_update", {}))
                    continuation["status"] = "resuming"

                    results.append({"description": action_desc, "status": "completed" if tool_result.get("ok") else "failed"})
                else:
                    break
        except Exception as e:
            self.log(f"Executor loop error: {str(e)}", "error")

        return results

    def _call_executor(self, continuation: dict) -> dict:
        """Calls the Gemini model with strict observation cost hierarchy."""
        return parse_llm_json(self._raw_call_executor(continuation))

    def _perform_recording_replay(self, decision: dict) -> list:
        """
        Replays a captured user recording X times.
        Now uses LLM to reason about the recording if instructions are changed.
        """
        from tools.automation.recorder import get_recorded_calls, get_recorded_summary, get_recorded_domain
        recorded_calls = get_recorded_calls()
        recorded_summary = get_recorded_summary()
        recorded_domain = get_recorded_domain()

        if not recorded_calls:
            self.log("No recording found to replay.", "error")
            return []

        repeat_count = decision.get("repeat_count", 1)

        # If user provided extra instruction ("do the same but teal"), hand off to Executor
        if "Instruction" in str(decision) or "Correction" in str(self.current_goal) or "do the same" in self.current_goal.lower():
            self.log(f"Variation requested. Handing off to Executor with recording context.")
            handoff = {
                "task_type": "long",
                "goal": self.current_goal,
                "ui_target": recorded_domain or "Recorded Context",
                "iterable_payload": [f"Iteration {i+1}" for i in range(repeat_count)],
                "parameters": {
                    "recording_summary": recorded_summary,
                    "recorded_domain": recorded_domain
                }
            }
            return self._perform_long_task(handoff)

        self.log(f"Replaying recording {repeat_count} times.")
        all_results = []
        for i in range(repeat_count):
            if STOP_EVENT.is_set(): break
            self.log(f"Starting iteration {i+1}/{repeat_count}")
            res = self._perform_short_task({"text": f"Iteration {i+1}", "function_calls": recorded_calls})
            all_results.extend(res)

            if any(r["status"] == "failed" for r in res):
                self.log(f"Recording failed at iteration {i+1}. Stopping.", "error")
                break

        return all_results

    def _raw_call_executor(self, continuation: dict) -> str:
        """Calls the Gemini model and returns the raw response string."""
        is_resume = continuation.get("status") == "resuming"

        recording_context = ""
        params = continuation.get("parameters", {})
        if "recording_summary" in params:
            recording_context = f"\n\nRECORDED ACTIONS CONTEXT:\n{params['recording_summary']}\nUse this as a guide to achieve the goal."
            if "recorded_domain" in params:
                recording_context += f"\nRecorded Domain: {params['recorded_domain']}"

        # Baked-in observation cost hierarchy
        obs_cost_instructions = (
            "After EVERY tool call, you must explicitly choose one of these four observation strategies:\n"
            "1. timer - use when action has predictable latency (app launching, page loading). Cheap, prefer this.\n"
            "2. screenshot - use when outcome is unpredictable (AI generation completing, form submitting). Expensive, only when necessary.\n"
            "3. read_screen OCR - use when you need to extract specific text from a known region. Medium cost.\n"
            "4. next_action - use only when result was fully deterministic and no verification is needed.\n\n"
            "A screenshot costs a full vision inference — use it only when you cannot predict what the screen looks like. "
            "A timer costs nothing — use it whenever the action has predictable latency. Always prefer the cheaper observation option."
        )

        ui_state_handling = (
            "Handling Unexpected UI States:\n"
            "- Loading spinner visible: extend timer by 2s and re-check via screenshot.\n"
            "- Error message detected: take screenshot, attempt recovery action based on error text.\n"
            "- CAPTCHA detected: immediately emit { \"status\": \"human_intervention_required\", \"reason\": \"captcha_detected\" }.\n"
            "- Unexpected modal: attempt to dismiss via click_element or click, re-verify with screenshot."
        )

        if not is_resume:
            system_prompt = (
                "You are an Executor Agent starting a new task.\n"
                "Goal: {goal}\n"
                "UI Target: {ui_target}\n"
                "Queue: {queue}\n\n"
                "{recording}"
                "Tools: launch_app (path, args), open_url (url), click, type_text, wait, etc.\n"
                "To navigate to a page, use 'launch_app' with 'args' or 'open_url'.\n\n"
                "{obs_cost}\n\n"
                "{ui_state}\n\n"
                "Return a JSON with: 'description', 'function_call': {{'name', 'args'}}, 'continuation_update': {{}}.\n"
                "If finished, return {{'status': 'terminated'}}."
            ).format(
                goal=continuation["goal"],
                ui_target=continuation["ui_target"],
                queue=json.dumps(continuation["remaining_queue"]),
                recording=recording_context,
                obs_cost=obs_cost_instructions,
                ui_state=ui_state_handling
            )
            user_message = "Begin task."
        else:
            system_prompt = (
                "You are resuming an in-progress task. The continuation object below contains everything you need. "
                "Do not re-plan from scratch. Process the first item in the remaining queue, execute your loop, observe, "
                "and either terminate or emit a new continuation.\n\n"
                "{obs_cost}\n\n"
                "{ui_state}"
            ).format(obs_cost=obs_cost_instructions, ui_state=ui_state_handling)
            # Resumed invocations receive ONLY the continuation JSON
            user_message = json.dumps({
                "remaining_queue": continuation["remaining_queue"],
                "last_action_result": continuation["last_action_result"],
                "ui_target": continuation["ui_target"],
                "current_position": continuation["current_position"]
            })

        response = generate_response(system_prompt, user_message, model_name=get_model("executor"))
        self.log(f"RAW EXECUTOR RESPONSE: {response}", "debug")
        return response