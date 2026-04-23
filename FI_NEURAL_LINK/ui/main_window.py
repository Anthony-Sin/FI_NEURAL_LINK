import tkinter as tk
import threading
from FI_NEURAL_LINK.ui.overlay.overlay_window import OverlayWindow
from FI_NEURAL_LINK.ui.panels.header_panel import HeaderPanel
from FI_NEURAL_LINK.ui.panels.middle_panels import MiddlePanels
from FI_NEURAL_LINK.ui.panels.command_bar import CommandBar
from FI_NEURAL_LINK.ui.theme import CYBER_BLACK, CYBER_YELLOW, CYBER_PINK, CYBER_WHITE
from FI_NEURAL_LINK.ui.voice_system import VoiceSystem
from FI_NEURAL_LINK.tools.automation.recorder import start_recording, stop_recording

class Dashboard:
    def __init__(self):
        self.root = OverlayWindow()

        # Sidebar container with left yellow border
        self.sidebar = tk.Frame(self.root, bg=CYBER_BLACK, highlightthickness=0)
        self.sidebar.pack(fill="both", expand=True)

        self.left_border = tk.Frame(self.sidebar, bg=CYBER_YELLOW, width=2)
        self.left_border.pack(side="left", fill="y")

        self.main_frame = tk.Frame(self.sidebar, bg=CYBER_BLACK)
        self.main_frame.pack(side="left", fill="both", expand=True)

        # 1. TOP: HUD (yellow top border + controls + status)
        self.header = HeaderPanel(self.main_frame)
        self.header.pack(fill="x")

        # 2. MIDDLE: Activity log
        self.middle = MiddlePanels(self.main_frame)
        self.middle.pack(fill="both", expand=True)

        # 3. BOTTOM: Command input
        self.command_bar = CommandBar(self.main_frame)
        self.command_bar.pack(fill="x", side="bottom")

        # Voice integration
        self.voice = VoiceSystem(
            log_callback=self._voice_log,
            submit_callback=self._handle_voice_submit
        )
        self.command_bar.mic_btn.bind("<Button-1>", lambda e: self.voice.start_listening())
        self.header.rec_btn.bind("<Button-1>", lambda e: self._toggle_recording())

        # Wire window controls
        self.header.min_btn.bind("<Button-1>", lambda e: self.root.minimize())
        self.header.close_btn.bind("<Button-1>", lambda e: self.root.hide())

        self.root.bind_drag_to_all(self.root)

    # ── Public API ────────────────────────────────────────────────────────────

    def start(self):
        threading.Thread(target=self.root.mainloop, daemon=True).start()

    def log(self, text: str, level: str = "info", retry_count: int = 0, api_calls: int = 0):
        self.middle.add_log(text, level)
        if "STEP" in text.upper() or "EXECUTOR ACTION" in text.upper():
            self.header.set_doing(text)

        if api_calls > 0:
            self.header.set_api_calls(api_calls)

        # Auto-trigger timer from logs (e.g., "Waited for 5 seconds")
        import re
        match = re.search(r'(\d+(?:\.\d+)?)\s+seconds?', text, re.IGNORECASE)
        if match and any(keyword in text.upper() for keyword in ["WAIT", "TIMER", "SLEEP"]):
            seconds = int(float(match.group(1)))
            self.header.start_timer(seconds)

    def set_on_submit(self, callback):
        def wrapped(text):
            self.middle.set_last_prompt(text)
            self._check_for_timer(text)
            if callback:
                callback(text)
        self.command_bar.on_submit = wrapped

    # ── Internal ──────────────────────────────────────────────────────────────

    def _check_for_timer(self, text: str):
        import re
        # Support both 'timer 5' and 'timer 5 minutes'
        match = re.search(r'timer\s*(\d+(?:\.\d+)?)\s*(?:min|minute|sec|second)?', text, re.IGNORECASE)
        if match:
            val = float(match.group(1))
            self.log(f"SETTING TIMER: {val} UNITS", "success")
            self.header.start_timer(int(val * 60))

    def _voice_log(self, text: str, level: str = "info"):
        self.log(text, level)
        if "LISTENING" in text.upper():
            self.command_bar.set_mic_active(True)
        elif any(w in text.upper() for w in ("TRANSCRIBING", "TIMEOUT", "ERROR", "COMMAND")):
            self.command_bar.set_mic_active(False)

    def _handle_voice_submit(self, text: str):
        self._check_for_timer(text)
        if self.command_bar.on_submit:
            self.command_bar.on_submit(text)

    def _toggle_recording(self):
        if self.header.rec_btn.cget("text") == "REC":
            res = start_recording()
            if res.get("ok"):
                self.header.rec_btn.config(text="STOP", fg=CYBER_WHITE, bg=CYBER_PINK)
                self.log("Recording user actions...", "warning")
            else:
                self.log(f"Failed to start recording: {res.get('result')}", "error")
        else:
            res = stop_recording()
            if res.get("ok"):
                self.header.rec_btn.config(text="REC", fg=CYBER_PINK, bg=CYBER_BLACK)
                self.log(f"Recording stopped. Captured {len(res.get('events', []))} events.", "success")
                # In a real app, we might do something with the events here
            else:
                self.log(f"Failed to stop recording: {res.get('result')}", "error")