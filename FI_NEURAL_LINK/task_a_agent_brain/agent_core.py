import os
import re
import json
import shutil
import winreg
import logging
from difflib import get_close_matches
from .goal_decomposer.goal_decomposer import decompose_goal
from .loop_guard import LoopGuard
from FI_NEURAL_LINK.task_b_dashboard.panels.stop_panel import STOP_EVENT

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
    try:
        key_path = rf"SOFTWARE\Microsoft\Windows\CurrentVersion\App Paths\{exe_name}"
        with winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, key_path) as key:
            path, _ = winreg.QueryValueEx(key, "")
            if path and os.path.isfile(path):
                return path
    except (FileNotFoundError, OSError):
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
        """
        Initializes the AgentCore.

        Args:
            config (dict): Configuration containing:
                - gemini_api_key (str): The API key for Gemini.
                - max_retries (int): Maximum number of retries for actions.
                - loop_window (int): The window size for loop detection.
            tool_router (ToolRouter, optional): The tool router to execute actions.
            log_callback (callable, optional): A callback function for logging.
        """
        self.config = config
        os.environ["GEMINI_API_KEY"] = config.get("gemini_api_key", "")
        self.loop_guard = LoopGuard(n=config.get("loop_window", 5))
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
        """Legacy log method for compatibility, redirects to logger."""
        level_map = {
            "debug":    logging.DEBUG,
            "info":     logging.INFO,
            "warning":  logging.WARNING,
            "error":    logging.ERROR,
            "critical": logging.CRITICAL,
        }
        self.logger.log(level_map.get(level.lower(), logging.INFO), text)

    # ── Parameter Extraction ────────────────────────────────────────────────

    def _extract_params(self, tool_hint: str, description: str) -> dict:
        """
        Extract tool parameters from a step description.
        For launch steps, uses resolve_app_path() with fuzzy matching
        so Gemini typos and vague names are handled gracefully.
        """
        params = {}

        # ── open_url ────────────────────────────────────────────────────────
        if tool_hint == "open_url":
            url_match = re.search(r'https?://[^\s]+', description)
            if url_match:
                params["url"] = url_match.group(0)
            else:
                domain_match = re.search(r'[a-zA-Z0-9.-]+\.[a-z]{2,}', description)
                if domain_match:
                    params["url"] = "https://" + domain_match.group(0)

        # ── launch / launch_app ─────────────────────────────────────────────
        elif tool_hint in ["launch", "launch_app"]:
            resolved = None

            # 1. Gemini gave us a real path already (e.g. C:\...\chrome.exe)
            path_match = re.search(r'[A-Za-z]:\\[^\s]+\.exe', description, re.IGNORECASE)
            if path_match:
                candidate = path_match.group(0)
                if os.path.isfile(candidate):
                    resolved = candidate

            # 2. Strip action verbs and resolve what remains
            if not resolved:
                stripped = re.sub(
                    r'\b(launch|open|start|run|execute|the|browser|application|app)\b',
                    '', description, flags=re.IGNORECASE
                ).strip(" .")
                resolved = resolve_app_path(stripped)

            # 3. Full description as fallback
            if not resolved:
                resolved = resolve_app_path(description.strip())

            if not resolved:
                self.log(
                    f"Could not resolve a valid executable from: '{description}'. "
                    f"Hint: valid app keys are e.g. {', '.join(list(APP_ALIASES.keys())[:8])}...",
                    "error"
                )
                params["path"] = ""
            else:
                self.log(f"Resolved launch path: '{resolved}'", "debug")
                params["path"] = resolved

            params["args"] = []

        # ── type / type_text ────────────────────────────────────────────────
        elif tool_hint in ["type", "type_text"]:
            text_match = re.search(r'["\'](.*?)["\']', description)
            if text_match:
                params["text"] = text_match.group(1)
            else:
                params["text"] = re.sub(
                    r'\b(type|write|enter|input)\b', '', description,
                    flags=re.IGNORECASE
                ).strip()

        # ── click ───────────────────────────────────────────────────────────
        elif tool_hint == "click":
            coord_match = re.search(r'(\d+)\s*,\s*(\d+)', description)
            if coord_match:
                params["x"] = int(coord_match.group(1))
                params["y"] = int(coord_match.group(2))
            else:
                params["x"] = 0
                params["y"] = 0

        # ── scroll ──────────────────────────────────────────────────────────
        elif tool_hint == "scroll":
            direction = "down"
            if re.search(r'\bup\b', description, re.IGNORECASE):
                direction = "up"
            amount_match = re.search(r'(\d+)', description)
            params["direction"] = direction
            params["amount"] = int(amount_match.group(1)) if amount_match else 3

        # ── key / hotkey ─────────────────────────────────────────────────
        elif tool_hint in ["key", "hotkey", "press"]:
            # e.g. "Press Ctrl+C" or "Press the Enter key"
            key_match = re.search(
                r'(ctrl|alt|shift|win|enter|escape|tab|space|backspace|delete|'
                r'f\d{1,2}|[a-z0-9])',
                description, re.IGNORECASE
            )
            params["key"] = key_match.group(0).lower() if key_match else ""

        # ── screenshot ──────────────────────────────────────────────────────
        elif tool_hint == "screenshot":
            filename_match = re.search(r'[\w\-]+\.png', description, re.IGNORECASE)
            params["filename"] = filename_match.group(0) if filename_match else "screenshot.png"

        return params

    # ── Goal Execution ──────────────────────────────────────────────────────

    def run_goal(self, goal: str) -> list:
        """
        Decomposes a goal into steps and executes them,
        checking for loops and STOP_EVENT between each step.

        Args:
            goal (str): The high-level goal to achieve.

        Returns:
            list: A list of result dicts for each executed step.

        Raises:
            RuntimeError: If a loop is detected or STOP_EVENT is set.
        """
        self.log(f"Starting goal: {goal}")

        try:
            steps = decompose_goal(goal)
            self.log(f"Goal decomposed into {len(steps)} steps.")
            self.log(f"Raw decomposition: {json.dumps(steps)}", "debug")
        except Exception as e:
            self.log(f"Decomposition failed: {str(e)}", "error")
            return []

        results = []

        for step in steps:
            # Emergency stop check
            if STOP_EVENT.is_set():
                self.log("Emergency stop detected. Halting execution.", "error")
                break

            action_desc = step.get("description", "")
            tool_hint   = step.get("tool_hint", "")
            step_id     = step.get("step_id")

            self.log(f"Executing step {step_id}: {action_desc} (Tool: {tool_hint})")

            # Loop guard check
            if self.loop_guard.check_loop(action_desc):
                error_msg = f"Loop detected — agent halted. Last action: {action_desc}"
                self.log(error_msg, "error")
                raise RuntimeError(error_msg)

            self.loop_guard.record_action(action_desc)

            result = {
                "step_id":    step_id,
                "description": action_desc,
                "tool_used":  tool_hint,
                "status":     "skipped",
                "result":     "No tool router available",
            }

            if self.tool_router:
                params = self._extract_params(tool_hint, action_desc)
                self.log(f"Extracted parameters: {params}", "debug")

                tool_result    = self.tool_router.execute(tool_hint, params)
                result["status"] = "completed" if tool_result.get("ok") else "failed"
                result["result"] = tool_result.get("result", "")

                if not tool_result.get("ok"):
                    self.log(f"Step {step_id} failed: {result['result']}", "error")
                else:
                    self.log(f"Step {step_id} completed: {result['result']}")
            else:
                self.log(f"Step {step_id} skipped: No tool router", "warning")

            results.append(result)

            if result["status"] == "failed":
                self.log("Stopping execution due to step failure.", "error")
                break

        self.log("Goal execution finished.")
        return results