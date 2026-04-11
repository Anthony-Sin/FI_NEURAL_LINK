import tkinter as tk
from tkinter import ttk
from ..theme import CYBER_YELLOW, CYBER_BLACK, CYBER_BLUE, FONT_FUTURISTIC_SMALL

class ProgressTimer(tk.Frame):
    def __init__(self, parent):
        super().__init__(parent, bg=CYBER_BLACK)

        self.container = tk.Frame(self, bg=CYBER_BLACK)
        self.container.pack(fill="x", padx=10, pady=5)

        # Currently Doing
        self.doing_label = tk.Label(
            self.container,
            text="CURRENTLY_DOING",
            bg=CYBER_BLACK,
            fg=CYBER_BLUE,
            font=FONT_FUTURISTIC_SMALL
        )
        self.doing_label.pack(side="left")

        self.status_text = tk.Label(
            self.container,
            text="IDLE",
            bg=CYBER_BLACK,
            fg=CYBER_YELLOW,
            font=FONT_FUTURISTIC_SMALL
        )
        self.status_text.pack(side="right")

        # Progress Bar
        self.style = ttk.Style()
        self.style.configure(
            "Cyber.Horizontal.TProgressbar",
            thickness=6,
            troughcolor=CYBER_BLACK,
            background=CYBER_YELLOW,
            bordercolor=CYBER_BLACK
        )

        self.progress = ttk.Progressbar(
            self,
            style="Cyber.Horizontal.TProgressbar",
            orient="horizontal",
            mode="determinate"
        )
        self.progress.pack(fill="x", padx=10, pady=(0, 5))

        self._pulse_state = False
        self._is_active = False

    def set_doing(self, text, active=True):
        self.status_text.config(text=text.upper())
        self._is_active = active
        if active: self._pulse_label()

    def _pulse_label(self):
        if self._is_active:
            color = "#0099aa" if self._pulse_state else CYBER_BLUE
            self.doing_label.config(fg=color)
            self._pulse_state = not self._pulse_state
            self.after(800, self._pulse_label)

    def start_timer(self, duration_seconds):
        self.progress["maximum"] = duration_seconds
        self.progress["value"] = duration_seconds
        self._tick(duration_seconds)

    def _tick(self, remaining):
        if remaining > 0 and self._is_active:
            self.progress["value"] = remaining
            self.after(1000, lambda: self._tick(remaining - 1))
        else:
            self.progress["value"] = 0
            self.set_doing("IDLE", False)
