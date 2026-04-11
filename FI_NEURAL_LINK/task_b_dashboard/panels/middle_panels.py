import tkinter as tk
from ..theme import CYBER_YELLOW, CYBER_BLACK, CYBER_PINK

# ── Activity Log Bar ──────────────────────────────────────────────────────────

class ActivityBar(tk.Frame):
    def __init__(self, parent, text=""):
        super().__init__(parent, bg=CYBER_BLACK)

        self.border = tk.Frame(self, bg=CYBER_YELLOW, width=2)
        self.border.pack(side="left", fill="y")

        self.content = tk.Frame(self, bg="#0d0d00", padx=10, pady=7)
        self.content.pack(side="left", fill="both", expand=True)

        self.dot_canvas = tk.Canvas(
            self.content, width=8, height=8, bg="#0d0d00", highlightthickness=0
        )
        self.dot_canvas.pack(side="left", padx=(0, 9))
        self.dot = self.dot_canvas.create_rectangle(1, 1, 7, 7, fill=CYBER_PINK, outline=CYBER_PINK)

        self.label = tk.Label(
            self.content,
            text=text.upper(),
            bg="#0d0d00",
            fg=CYBER_YELLOW,
            font=("Consolas", 9, "bold italic"),
            anchor="w"
        )
        self.label.pack(side="left", fill="x", expand=True)

        self._pulse_state = True
        self._pulse()

    def _pulse(self):
        color = CYBER_PINK if self._pulse_state else "#1a0000"
        self.dot_canvas.itemconfig(self.dot, fill=color, outline=color)
        self._pulse_state = not self._pulse_state
        self.after(600, self._pulse)

    def update_text(self, text):
        self.label.config(text=text.upper())


# ── Middle Panel ──────────────────────────────────────────────────────────────

class MiddlePanels(tk.Frame):
    def __init__(self, parent):
        super().__init__(parent, bg=CYBER_BLACK)

        self.container = tk.Frame(self, bg=CYBER_BLACK, padx=14, pady=16)
        self.container.pack(fill="both", expand=True)

        self.prompt_label = tk.Label(
            self.container,
            text="",
            bg=CYBER_BLACK,
            fg="#444400",
            font=("Consolas", 8, "italic"),
            anchor="w",
            justify="left"
        )
        self.prompt_label.pack(fill="x", pady=(0, 14))

        # 3 bars, all hidden until logs arrive
        self.bars: list[ActivityBar] = []
        for _ in range(3):
            bar = ActivityBar(self.container, "")
            bar.pack(fill="x", pady=5)
            bar.pack_forget()
            self.bars.append(bar)

    def set_last_prompt(self, text: str):
        if text:
            self.prompt_label.config(text=f"PREVIOUS PROMPT: {text}")
        else:
            self.prompt_label.config(text="")

    def add_log(self, text: str, level: str = "info"):
        for i in range(len(self.bars) - 1):
            self.bars[i].update_text(self.bars[i + 1].label.cget("text"))
            if self.bars[i + 1].winfo_ismapped():
                self.bars[i].pack(fill="x", pady=5)
        self.bars[-1].update_text(text)
        self.bars[-1].pack(fill="x", pady=5)