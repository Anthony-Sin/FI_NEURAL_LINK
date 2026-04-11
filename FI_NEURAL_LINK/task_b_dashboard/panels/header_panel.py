import tkinter as tk
from ..theme import CYBER_YELLOW, CYBER_BLACK, CYBER_PINK

class HeaderPanel(tk.Frame):
    def __init__(self, parent):
        super().__init__(parent, bg=CYBER_BLACK)

        self._duration = 1
        self._remaining = 0

        # ── Yellow top border ─────────────────────────────────────────────────
        self.top_border = tk.Frame(self, bg=CYBER_YELLOW, height=2)
        self.top_border.pack(fill="x")

        # ── Single row: FI INITIALIZED. on left │ — ✕ on right ───────────────
        self.ctrl_row = tk.Frame(self, bg=CYBER_BLACK)
        self.ctrl_row.pack(fill="x", padx=10, pady=(5, 5))

        self.fi_label = tk.Label(
            self.ctrl_row,
            text="FI INITIALIZED.",
            bg=CYBER_BLACK,
            fg=CYBER_YELLOW,
            font=("Consolas", 7, "bold"),
            anchor="w"
        )
        self.fi_label.pack(side="left")

        self.close_btn = tk.Label(
            self.ctrl_row, text="✕", bg=CYBER_BLACK, fg=CYBER_PINK,
            font=("Consolas", 11, "bold"), cursor="hand2"
        )
        self.close_btn.pack(side="right")

        self.min_btn = tk.Label(
            self.ctrl_row, text="—", bg=CYBER_BLACK, fg=CYBER_YELLOW,
            font=("Consolas", 11, "bold"), cursor="hand2"
        )
        self.min_btn.pack(side="right", padx=(0, 8))

    # ── Public API (backend unchanged) ───────────────────────────────────────

    def update_progress(self, percent: float):
        pass

    def set_doing(self, text: str):
        pass

    def start_timer(self, duration_seconds: int):
        self._duration = max(duration_seconds, 1)
        self._remaining = duration_seconds
        self._tick()

    def _tick(self):
        if self._remaining > 0:
            self._remaining -= 1
            self.after(1000, self._tick)