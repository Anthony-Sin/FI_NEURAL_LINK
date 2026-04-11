import tkinter as tk
from ..theme import CYBER_BLUE, CYBER_YELLOW, CYBER_BLACK

class HeaderPanel(tk.Frame):
    def __init__(self, parent):
        super().__init__(parent, bg=CYBER_BLACK)

        # Sync Status Bar (Thin 2px top bar)
        self.progress_canvas = tk.Canvas(self, height=4, bg="#1a1a00", highlightthickness=0)
        self.progress_canvas.pack(fill="x")
        self.bar = self.progress_canvas.create_rectangle(0, 0, 100, 4, fill=CYBER_YELLOW, outline=CYBER_YELLOW)

        # HUD Container
        self.hud = tk.Frame(self, bg="#1a1a00", height=30)
        self.hud.pack(fill="x")
        self.hud.pack_propagate(False)

        self.doing_label = tk.Label(
            self.hud,
            text="CURRENTLY_DOING",
            bg="#1a1a00",
            fg=CYBER_BLUE,
            font=("monospace", 8, "bold")
        )
        self.doing_label.pack(side="left", padx=10)

        self.percent_label = tk.Label(
            self.hud,
            text="99.0%",
            bg="#1a1a00",
            fg=CYBER_YELLOW,
            font=("monospace", 10, "bold")
        )
        self.percent_label.pack(side="right", padx=10)

    def update_progress(self, percent):
        self.percent_label.config(text=f"{percent:.1f}%")
        width = self.winfo_width()
        if width > 1:
            self.progress_canvas.coords(self.bar, 0, 0, int(width * (percent/100)), 4)
