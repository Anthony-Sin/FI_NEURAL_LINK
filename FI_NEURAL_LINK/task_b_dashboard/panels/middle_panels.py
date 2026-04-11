import tkinter as tk
from ..theme import CYBER_YELLOW, CYBER_BLACK, CYBER_PINK

class ActivityBar(tk.Frame):
    def __init__(self, parent, text):
        super().__init__(parent, bg=CYBER_BLACK)

        # Left yellow border (2px)
        self.border = tk.Frame(self, bg=CYBER_YELLOW, width=2)
        self.border.pack(side="left", fill="y")

        # Content container
        self.content = tk.Frame(self, bg="#0d0d00", padx=10, pady=6) # bg-cyber-yellow/5
        self.content.pack(side="left", fill="both", expand=True, padx=(2, 0))

        # Pulsing pink dot
        self.dot_canvas = tk.Canvas(self.content, width=6, height=6, bg="#0d0d00", highlightthickness=0)
        self.dot_canvas.pack(side="left", padx=(0, 10))
        self.dot = self.dot_canvas.create_rectangle(0, 0, 6, 6, fill=CYBER_PINK, outline=CYBER_PINK)

        # Log Text
        self.label = tk.Label(
            self.content,
            text=text.upper(),
            bg="#0d0d00",
            fg=CYBER_YELLOW,
            font=("monospace", 9, "bold italic")
        )
        self.label.pack(side="left")

        self._pulse_state = True
        self._pulse()

    def _pulse(self):
        color = CYBER_PINK if self._pulse_state else "#220000"
        self.dot_canvas.itemconfig(self.dot, fill=color, outline=color)
        self._pulse_state = not self._pulse_state
        self.after(600, self._pulse)

    def update_text(self, text):
        self.label.config(text=text.upper())

class MiddlePanels(tk.Frame):
    def __init__(self, parent):
        super().__init__(parent, bg=CYBER_BLACK)

        self.container = tk.Frame(self, bg=CYBER_BLACK, padx=16, pady=20)
        self.container.pack(fill="both", expand=True)

        self.bars = []
        initial_logs = ["FI CORE LOADED", "NEURAL LINK ESTABLISHED", "SYSTEM STATUS: OPTIMAL"]

        for log in initial_logs:
            bar = ActivityBar(self.container, log)
            bar.pack(fill="x", pady=6)
            self.bars.append(bar)

    def add_log(self, text, level="info"):
        for i in range(len(self.bars)-1):
            self.bars[i].update_text(self.bars[i+1].label.cget("text"))
        self.bars[-1].update_text(text)
