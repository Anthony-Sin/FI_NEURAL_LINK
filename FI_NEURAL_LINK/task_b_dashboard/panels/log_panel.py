import tkinter as tk
from tkinter import scrolledtext
import datetime
import re
from ..theme import CYBER_YELLOW, CYBER_BLACK, CYBER_BLUE, CYBER_PINK, FONT_MONO_SMALL, FONT_MONO_MED

class LogPanel(tk.Frame):
    def __init__(self, parent):
        super().__init__(parent, bg=CYBER_BLACK)

        self.text_area = scrolledtext.ScrolledText(
            self,
            bg=CYBER_BLACK,
            fg=CYBER_YELLOW,
            insertbackground=CYBER_YELLOW,
            font=FONT_MONO_SMALL,
            state="disabled",
            relief="flat",
            borderwidth=0,
            highlightthickness=0
        )
        self.text_area.pack(fill="both", expand=True, padx=10, pady=10)

        # Tags for cyberpunk styling
        self.text_area.tag_configure("bullet", foreground=CYBER_PINK, font=("monospace", 12, "bold"))
        self.text_area.tag_configure("timestamp", foreground=CYBER_BLUE, font=FONT_MONO_SMALL)
        self.text_area.tag_configure("box_text", foreground=CYBER_YELLOW, font=FONT_MONO_SMALL)
        self.text_area.tag_configure("code", foreground="#00ff88", background="#111111", font=FONT_MONO_SMALL)
        self.text_area.tag_configure("error", foreground=CYBER_PINK, font=("monospace", 10, "bold"))

    def append_line(self, text, level="info"):
        timestamp = datetime.datetime.now().strftime("[%H:%M:%S]")

        self.text_area.configure(state="normal")

        # Adding a box-like entry
        self.text_area.insert(tk.END, " ■ ", "bullet")
        self.text_area.insert(tk.END, f"{timestamp} ", "timestamp")

        # Check for code blocks (simple markdown detection)
        if "```" in text:
            parts = re.split(r'```', text)
            for i, part in enumerate(parts):
                if i % 2 == 1:
                    self.text_area.insert(tk.END, part, "code")
                else:
                    self.text_area.insert(tk.END, part, "box_text")
        else:
            tag = "error" if level == "error" else "box_text"
            self.text_area.insert(tk.END, f"{text.upper()}\n", tag)

        self.text_area.insert(tk.END, "─" * 40 + "\n", "timestamp")

        self.text_area.configure(state="disabled")
        self.text_area.see(tk.END)

    def clear(self):
        self.text_area.configure(state="normal")
        self.text_area.delete(1.0, tk.END)
        self.text_area.configure(state="disabled")
