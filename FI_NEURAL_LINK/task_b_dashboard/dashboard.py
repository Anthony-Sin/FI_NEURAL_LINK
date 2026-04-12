import tkinter as tk
import threading
from FI_NEURAL_LINK.task_b_dashboard.overlay.overlay_window import OverlayWindow
from FI_NEURAL_LINK.task_b_dashboard.panels.header_panel import HeaderPanel
from FI_NEURAL_LINK.task_b_dashboard.panels.middle_panels import MiddlePanels
from FI_NEURAL_LINK.task_b_dashboard.panels.command_bar import CommandBar
from FI_NEURAL_LINK.task_b_dashboard.theme import CYBER_BLACK, CYBER_YELLOW
from FI_NEURAL_LINK.task_b_dashboard.voice_system import VoiceSystem

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

        # Wire window controls
        self.header.min_btn.bind("<Button-1>", lambda e: self.root.minimize())
        self.header.close_btn.bind("<Button-1>", lambda e: self.root.hide())

        self.root.bind_drag_to_all(self.root)

    # ── Public API ────────────────────────────────────────────────────────────

    def start(self):
        threading.Thread(target=self.root.mainloop, daemon=True).start()

    def log(self, text: str, level: str = "info"):
        self.middle.add_log(text, level)
        if "STEP" in text.upper():
            self.header.set_doing(text)

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