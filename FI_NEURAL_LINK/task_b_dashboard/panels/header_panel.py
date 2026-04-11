import tkinter as tk
from ..theme import CYBER_BLUE, CYBER_YELLOW, CYBER_BLACK

class HeaderPanel(tk.Frame):
    def __init__(self, parent):
        super().__init__(parent, bg=CYBER_BLACK)

        # Polished white progress bar (Top, 1px)
        self.progress_canvas = tk.Canvas(self, height=1, bg="#111111", highlightthickness=0)
        self.progress_canvas.pack(fill="x")
        self.bar = self.progress_canvas.create_rectangle(0, 0, 0, 1, fill="#FFFFFF", outline="#FFFFFF")

        # HUD Container
        self.hud = tk.Frame(self, bg=CYBER_BLACK, height=50)
        self.hud.pack(fill="x", pady=(5, 0))
        self.hud.pack_propagate(False)

        # All info aligned to the right as per "98.5 position" logic
        self.right_info = tk.Frame(self.hud, bg=CYBER_BLACK)
        self.right_info.pack(side="right", padx=15)

        # Top line: IDLE indicator
        self.doing_label = tk.Label(
            self.right_info,
            text="IDLE",
            bg=CYBER_BLACK,
            fg=CYBER_BLUE,
            font=("monospace", 8, "bold")
        )
        self.doing_label.pack(side="top", anchor="e")

        # Bottom line: Metric + Buttons
        self.actions_row = tk.Frame(self.right_info, bg=CYBER_BLACK)
        self.actions_row.pack(side="top", anchor="e", pady=(2, 0))

        self.metric_label = tk.Label(
            self.actions_row,
            text="98.2",
            bg=CYBER_BLACK,
            fg=CYBER_YELLOW,
            font=("monospace", 10, "bold")
        )
        self.metric_label.pack(side="left", padx=(0, 15))

        self.min_btn = tk.Label(
            self.actions_row, text="—", bg=CYBER_BLACK, fg=CYBER_YELLOW,
            font=("monospace", 12, "bold"), cursor="hand2"
        )
        self.min_btn.pack(side="left", padx=5)

        self.close_btn = tk.Label(
            self.actions_row, text="X", bg=CYBER_BLACK, fg="#ff003c",
            font=("monospace", 12, "bold"), cursor="hand2"
        )
        self.close_btn.pack(side="left", padx=5)

    def update_progress(self, percent):
        width = self.winfo_width()
        if width > 1:
            self.progress_canvas.coords(self.bar, 0, 0, int(width * (percent/100)), 1)

    def start_timer(self, duration_seconds):
        self._duration = duration_seconds
        self._remaining = duration_seconds
        self._tick()

    def _tick(self):
        if self._remaining > 0:
            percent = (self._remaining / self._duration) * 100
            self.update_progress(percent)
            self._remaining -= 1
            self.after(1000, self._tick)
        else:
            self.update_progress(0)
            self.set_doing("IDLE")

    def set_doing(self, text):
        self.doing_label.config(text=text.upper())
