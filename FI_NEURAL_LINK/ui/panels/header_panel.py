import tkinter as tk
from ..theme import CYBER_YELLOW, CYBER_BLACK, CYBER_PINK, CYBER_WHITE

class HeaderPanel(tk.Frame):
    def __init__(self, parent):
        super().__init__(parent, bg=CYBER_BLACK)

        self._duration = 1
        self._remaining = 0

        # ── 1px white progress bar at the very top ───────────────────────────
        self.progress_canvas = tk.Canvas(
            self, height=1, bg=CYBER_BLACK, highlightthickness=0
        )
        self.progress_canvas.pack(fill="x")
        self.progress_bar = self.progress_canvas.create_rectangle(
            0, 0, 0, 1, fill=CYBER_WHITE, outline=""
        )

        # ── Yellow top border ─────────────────────────────────────────────────
        self.top_border = tk.Frame(self, bg=CYBER_YELLOW, height=2)
        self.top_border.pack(fill="x")

        # ── Dashboard Status: IDLE / 98.2 metric ─────────────────────────────
        self.status_row = tk.Frame(self, bg=CYBER_BLACK)
        self.status_row.pack(fill="x", padx=10, pady=(10, 0))

        self.status_label = tk.Label(
            self.status_row,
            text="IDLE 0",
            bg=CYBER_BLACK,
            fg=CYBER_WHITE,
            font=("Consolas", 14, "bold"),
            anchor="w"
        )
        self.status_label.pack(side="left")

        self.metric_label = tk.Label(
            self.status_row,
            text="00.0",
            bg=CYBER_BLACK,
            fg=CYBER_WHITE,
            font=("Consolas", 14, "bold"),
            anchor="e"
        )
        self.metric_label.pack(side="right")
        self._update_metric()

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
        """Updates the 1px white progress bar (0 to 100)."""
        w = self.progress_canvas.winfo_width()
        if w <= 1: # Widget might not be fully rendered yet
            w = 288 # Use fixed dashboard width as fallback
        x1 = (percent / 100.0) * w
        self.progress_canvas.coords(self.progress_bar, 0, 0, x1, 1)

    def set_doing(self, text: str, retry_count: int = 0):
        """Sets the current doing status with context awareness."""
        clean = text.strip().upper()
        suffix = f" {retry_count}" if retry_count > 0 else " 0"

        if "NAVIGAT" in clean or "OPEN" in clean:
            self.status_label.config(text="NAVIGATING" + suffix, fg="#00f0ff") # Blue
        elif "TYPE" in clean or "WRITE" in clean:
            self.status_label.config(text="TYPING" + suffix, fg="#fcee0a") # Yellow
        elif "CLICK" in clean or "PRESS" in clean:
            self.status_label.config(text="INTERACTING" + suffix, fg="#00ff88") # Green
        elif "WAIT" in clean or "SLEEP" in clean:
            self.status_label.config(text="WAITING" + suffix, fg="#ffaa00") # Orange
        elif "ANALYZ" in clean or "VISION" in clean:
            self.status_label.config(text="ANALYZING" + suffix, fg="#ff003c") # Pink
        elif "IDLE" in clean:
            self.status_label.config(text="IDLE" + suffix, fg="#ffffff")
        else:
            self.status_label.config(text="ACTIVE" + suffix, fg="#ffffff")

    def start_timer(self, duration_seconds: int):
        self._duration = max(duration_seconds, 1)
        self._remaining = duration_seconds
        self.set_doing("ACTIVE")
        self._tick()

    def _update_metric(self):
        """Updates the system metric (e.g. CPU usage) to make the HUD feel alive."""
        try:
            import psutil
            cpu = psutil.cpu_percent()
            self.metric_label.config(text=f"{cpu:04.1f}")
        except:
            pass
        self.after(2000, self._update_metric)

    def _tick(self):
        if self._remaining > 0:
            self._remaining -= 1
            # Update progress based on remaining time
            percent = 100 * (1 - (self._remaining / self._duration))
            self.update_progress(percent)
            self.after(1000, self._tick)
        else:
            self.set_doing("IDLE")
            self.update_progress(0)