import tkinter as tk
import threading
from FI_NEURAL_LINK.task_b_dashboard.overlay.overlay_window import OverlayWindow
from FI_NEURAL_LINK.task_b_dashboard.panels.command_panel import CommandPanel
from FI_NEURAL_LINK.task_b_dashboard.panels.log_panel import LogPanel
from FI_NEURAL_LINK.task_b_dashboard.panels.status_bar import StatusBar
from FI_NEURAL_LINK.task_b_dashboard.panels.progress_timer import ProgressTimer
from FI_NEURAL_LINK.task_b_dashboard.voice_system import VoiceSystem
from FI_NEURAL_LINK.task_b_dashboard.theme import CYBER_BLACK, CYBER_YELLOW, CYBER_PINK, FONT_MONO_LARGE

class Dashboard:
    def __init__(self):
        self.root = OverlayWindow()

        # Header Frame
        header = tk.Frame(self.root, bg=CYBER_BLACK)
        header.pack(fill="x", padx=10, pady=5)

        title_label = tk.Label(
            header,
            text="FI_NEURAL_LINK",
            bg=CYBER_BLACK,
            fg=CYBER_YELLOW,
            font=FONT_MONO_LARGE
        )
        title_label.pack(side="left")

        # Control Buttons
        controls = tk.Frame(header, bg=CYBER_BLACK)
        controls.pack(side="right")

        self.min_btn = tk.Label(
            controls, text="—", bg=CYBER_BLACK, fg=CYBER_YELLOW,
            font=("monospace", 12, "bold"), cursor="hand2", padx=5
        )
        self.min_btn.pack(side="left")
        self.min_btn.bind("<Button-1>", lambda e: self.root.minimize())

        self.close_btn = tk.Label(
            controls, text="X", bg=CYBER_BLACK, fg=CYBER_PINK,
            font=("monospace", 12, "bold"), cursor="hand2", padx=5
        )
        self.close_btn.pack(side="right")
        self.close_btn.bind("<Button-1>", lambda e: self.root.hide())

        # 1. TOP: Status Bar
        self.status_bar = StatusBar(self.root)
        self.status_bar.pack(fill="x")

        # 2. LOGS: Center
        self.log_panel = LogPanel(self.root)
        self.log_panel.pack(fill="both", expand=True)

        # 3. MIDDLE: Command Input
        self.command_panel = CommandPanel(self.root)
        self.command_panel.pack(fill="x")

        # 4. BOTTOM: Progress & Status
        self.progress_timer = ProgressTimer(self.root)
        self.progress_timer.pack(fill="x")

        # Voice System Integration
        self.voice_system = VoiceSystem(
            log_callback=self.log,
            submit_callback=lambda cmd: self.command_panel.on_submit(cmd) if self.command_panel.on_submit else None
        )
        self.command_panel.voice_btn.bind("<Button-1>", lambda e: self.voice_system.start_listening())

        # Apply recursive drag binding to all components
        self.root.bind_drag_to_all(self.root)

    def start(self):
        # Launches the tkinter mainloop in a daemon thread
        threading.Thread(target=self.root.mainloop, daemon=True).start()

    def log(self, text, level="info"):
        self.log_panel.append_line(text, level)

        # Parse for timer duration (e.g., "25 minutes")
        import re
        match = re.search(r'(\d+)\s*minutes?', text, re.IGNORECASE)
        if match:
            minutes = int(match.group(1))
            self.progress_timer.start_timer(minutes * 60)
            self.progress_timer.set_doing(f"ESTIMATED COMPLETION: {minutes} MIN")

    def set_on_submit(self, callback):
        def wrapped_submit(goal):
            self.status_bar.increment_counter()
            self.progress_timer.set_doing(f"EXECUTING: {goal[:20]}...")
            if callback:
                callback(goal)

        self.command_panel.on_submit = wrapped_submit
