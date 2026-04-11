import tkinter as tk
from tkinter import scrolledtext
import datetime

class LogPanel(tk.Frame):
    def __init__(self, parent):
        super().__init__(parent, bg="#0d0d0f")

        # Scrollable Text widget
        self.text_area = scrolledtext.ScrolledText(
            self,
            bg="#0d0d0f",
            fg="#00ccff",
            insertbackground="#00ccff",
            font=("monospace", 11),
            state="disabled",
            relief="flat",
            borderwidth=0
        )
        self.text_area.pack(fill="both", expand=True, padx=5, pady=5)

        # Color tags
        self.text_area.tag_configure("info", foreground="#00ccff")
        self.text_area.tag_configure("success", foreground="#00ff88")
        self.text_area.tag_configure("warn", foreground="#ffcc00")
        self.text_area.tag_configure("error", foreground="#ff4444")

    def append_line(self, text, level="info"):
        timestamp = datetime.datetime.now().strftime("[%H:%M:%S]")
        full_text = f"{timestamp} {text}\n"

        self.text_area.configure(state="normal")
        self.text_area.insert(tk.END, full_text, level)
        self.text_area.configure(state="disabled")

        # Auto-scroll to bottom
        self.text_area.see(tk.END)

    def clear(self):
        self.text_area.configure(state="normal")
        self.text_area.delete(1.0, tk.END)
        self.text_area.configure(state="disabled")
