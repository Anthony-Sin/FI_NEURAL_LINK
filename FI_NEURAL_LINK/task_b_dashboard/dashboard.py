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

        # Sidebar Container with left border
        self.sidebar = tk.Frame(self.root, bg=CYBER_BLACK, highlightthickness=0)
        self.sidebar.pack(fill="both", expand=True)

        # Left border line
        self.left_border = tk.Frame(self.sidebar, bg=CYBER_YELLOW, width=2)
        self.left_border.pack(side="left", fill="y")

        self.main_frame = tk.Frame(self.sidebar, bg=CYBER_BLACK)
        self.main_frame.pack(side="left", fill="both", expand=True)

        # 1. TOP: HUD
        self.header = HeaderPanel(self.main_frame)
        self.header.pack(fill="x")

        # 2. MIDDLE: Activity Stack
        self.middle = MiddlePanels(self.main_frame)
        self.middle.pack(fill="both", expand=True)

        # 3. BOTTOM: System Input
        self.command_bar = CommandBar(self.main_frame)
        self.command_bar.pack(fill="x", side="bottom")

        # Voice Integration
        self.voice = VoiceSystem(log_callback=self._voice_log, submit_callback=self._handle_voice_submit)
        self.command_bar.mic_btn.bind("<Button-1>", lambda e: self.voice.start_listening())

        # Wire Control Buttons from Header
        self.header.min_btn.bind("<Button-1>", lambda e: self.root.minimize())
        self.header.close_btn.bind("<Button-1>", lambda e: self.root.hide())

        self.root.bind_drag_to_all(self.root)
        self._sync_sim()

    def _sync_sim(self):
        import random
        val = 98 + random.random() * 2
        self.header.update_progress(val)
        self.root.after(4000, self._sync_sim)

    def start(self):
        threading.Thread(target=self.root.mainloop, daemon=True).start()

    def log(self, text, level="info"):
        self.middle.add_log(text, level)
        if "STEP" in text.upper():
            self.header.set_doing(text)

    def _voice_log(self, text, level="info"):
        self.log(text, level)
        if "LISTENING" in text.upper():
            self.command_bar.set_mic_active(True)
        elif "TRANSCRIBING" in text.upper() or "TIMEOUT" in text.upper() or "ERROR" in text.upper() or "COMMAND" in text.upper():
            self.command_bar.set_mic_active(False)

    def set_on_submit(self, callback):
        def wrapped_callback(text):
            self.middle.set_last_prompt(text)
            self._check_for_timer(text)
            if callback:
                callback(text)
        self.command_bar.on_submit = wrapped_callback

    def _check_for_timer(self, text):
        import re
        match = re.search(r'timer.*?(\d+)', text, re.IGNORECASE)
        if match:
            mins = int(match.group(1))
            self.log(f"SETTING TIMER: {mins} MINUTES", "success")
            self.header.set_doing(f"COUNTDOWN: {mins}M")
            self.header.start_timer(mins * 60)

    def _handle_voice_submit(self, text):
        self._check_for_timer(text)
        if self.command_bar.on_submit:
            self.command_bar.on_submit(text)
