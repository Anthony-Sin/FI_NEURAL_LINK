import tkinter as tk
import threading
import re
from FI_NEURAL_LINK.task_b_dashboard.overlay.overlay_window import OverlayWindow
from FI_NEURAL_LINK.task_b_dashboard.panels.header_panel import HeaderPanel
from FI_NEURAL_LINK.task_b_dashboard.panels.command_bar import CommandBar
from FI_NEURAL_LINK.task_b_dashboard.panels.middle_panels import MiddlePanels
from FI_NEURAL_LINK.task_b_dashboard.panels.progress_timer import ProgressTimer
from FI_NEURAL_LINK.task_b_dashboard.panels.stop_panel import StopPanel
from FI_NEURAL_LINK.task_b_dashboard.voice_system import VoiceSystem
from FI_NEURAL_LINK.task_b_dashboard.theme import CYBER_BLACK, CYBER_YELLOW

class Dashboard:
    def __init__(self):
        self.root = OverlayWindow()

        # Main Canvas for background grid
        self.main_canvas = tk.Canvas(self.root, bg=CYBER_BLACK, highlightthickness=0)
        self.main_canvas.place(x=0, y=0, relwidth=1, relheight=1)
        self._animate_grid()

        # Layout Container
        self.layout = tk.Frame(self.root, bg=CYBER_BLACK, highlightthickness=1, highlightbackground=CYBER_YELLOW)
        self.layout.pack(fill="both", expand=True, padx=5, pady=5)

        # 1. TOP: Model Indicator & Prompt Counter
        self.header = HeaderPanel(self.layout)
        self.header.pack(fill="x")

        # 2. MIDDLE: Command Bar & Suggestions
        self.command_bar = CommandBar(self.layout)
        self.command_bar.pack(fill="x")

        # 3. OUTPUT: modular panels (Logs)
        self.middle = MiddlePanels(self.layout)
        self.middle.pack(fill="both", expand=True)

        # 4. BOTTOM: Timer & Status
        self.timer_status = ProgressTimer(self.layout)
        self.timer_status.pack(fill="x")

        # 5. HIDDEN: Emergency Stop (Bottommost)
        self.stop_panel = StopPanel(self.layout)
        self.stop_panel.pack(fill="x")

        # System Controls
        self.min_btn = tk.Label(self.header.container, text="—", bg=CYBER_BLACK, fg=CYBER_YELLOW, cursor="hand2")
        self.min_btn.pack(side="right", padx=5)
        self.min_btn.bind("<Button-1>", lambda e: self.root.minimize())

        # Voice Integration
        self.voice = VoiceSystem(
            log_callback=self.log,
            submit_callback=lambda t: self.command_bar.on_submit(t) if self.command_bar.on_submit else None
        )
        self.command_bar.mic_canvas.bind("<Button-1>", lambda e: self.voice.start_listening())

        # Quick Action (Lightning Bolt)
        self.command_bar.bolt_canvas.bind("<Button-1>", self._quick_action)

        self.root.bind_drag_to_all(self.root)

        # State
        self._timer_remaining = 0

    def _animate_grid(self):
        self.main_canvas.delete("grid")
        for i in range(0, 420, 40):
            self.main_canvas.create_line(i, 0, i, 750, fill="#050505", tags="grid")
        for i in range(0, 750, 40):
            self.main_canvas.create_line(0, i, 420, i, fill="#050505", tags="grid")
        self.root.after(2000, self._animate_grid)

    def _quick_action(self, event):
        self.log("SYSTEM RECALIBRATION TRIGGERED")
        self.header.increment_prompt()

    def start(self):
        threading.Thread(target=self.root.mainloop, daemon=True).start()

    def log(self, text, level="info"):
        self.middle.add_log(text, level)

        # Timer parsing
        match = re.search(r'(\d+)\s*minutes?', text, re.IGNORECASE)
        if match:
            mins = int(match.group(1))
            self._timer_remaining = mins * 60
            self.timer_status.start_timer(self._timer_remaining)
            self.timer_status.set_doing(f"COUNTDOWN: {mins}M")
            self._tick_timer()
        else:
            self.timer_status.set_doing(text[:20])

    def _tick_timer(self):
        if self._timer_remaining > 0:
            self._timer_remaining -= 1
            # Simulation for reproduction
            self.header.update_progress(98.9)
            self.root.after(1000, self._tick_timer)

    def set_on_submit(self, callback):
        def wrapped_submit(goal):
            self.header.increment_prompt()
            self.timer_status.set_doing(f"GOAL: {goal[:15]}...")
            if callback: callback(goal)
        self.command_bar.on_submit = wrapped_submit
