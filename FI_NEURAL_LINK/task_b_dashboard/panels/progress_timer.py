import tkinter as tk
from tkinter import ttk
from ..theme import CYBER_YELLOW, CYBER_BLACK, CYBER_BLUE, FONT_MONO_SMALL

class ProgressTimer(tk.Frame):
    def __init__(self, parent):
        super().__init__(parent, bg=CYBER_BLACK)

        # Currently Doing Status
        self.status_frame = tk.Frame(self, bg=CYBER_BLACK)
        self.status_frame.pack(fill="x", padx=10, pady=(5, 0))

        self.doing_label = tk.Label(
            self.status_frame,
            text="CURRENTLY_DOING",
            bg=CYBER_BLACK,
            fg=CYBER_BLUE,
            font=FONT_MONO_SMALL
        )
        self.doing_label.pack(side="left")

        self.status_text = tk.Label(
            self.status_frame,
            text="IDLE",
            bg=CYBER_BLACK,
            fg=CYBER_YELLOW,
            font=FONT_MONO_SMALL
        )
        self.status_text.pack(side="right")

        # Progress Bar Styling
        self.style = ttk.Style()
        self.style.theme_use('default')
        self.style.configure(
            "Cyber.Horizontal.TProgressbar",
            thickness=10,
            troughcolor=CYBER_BLACK,
            background=CYBER_YELLOW,
            bordercolor=CYBER_YELLOW,
            lightcolor=CYBER_YELLOW,
            darkcolor=CYBER_YELLOW
        )

        self.progress = ttk.Progressbar(
            self,
            style="Cyber.Horizontal.TProgressbar",
            orient="horizontal",
            length=400,
            mode="determinate"
        )
        self.progress.pack(fill="x", padx=10, pady=5)

        self._pulse_state = False
        self._is_active = False

    def set_doing(self, text, active=True):
        self.status_text.config(text=text.upper())
        self._is_active = active
        if active:
            self._pulse_doing()
        else:
            self.doing_label.config(fg=CYBER_BLUE)

    def _pulse_doing(self):
        if self._is_active:
            alpha = 0.4 if self._pulse_state else 1.0
            # Simulating alpha with color dimming since tk labels don't support alpha
            color = "#0099aa" if self._pulse_state else CYBER_BLUE
            self.doing_label.config(fg=color)
            self._pulse_state = not self._pulse_state
            self.after(800, self._pulse_doing)

    def start_timer(self, duration_seconds):
        self.progress["maximum"] = duration_seconds
        self.progress["value"] = duration_seconds
        self._tick_timer(duration_seconds)

    def _tick_timer(self, remaining):
        if remaining > 0:
            self.progress["value"] = remaining
            self.after(1000, lambda: self._tick_timer(remaining - 1))
        else:
            self.progress["value"] = 0
            self.set_doing("COMPLETED", False)
