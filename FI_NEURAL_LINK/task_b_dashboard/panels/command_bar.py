import tkinter as tk
from ..theme import CYBER_YELLOW, CYBER_BLACK, CYBER_BLUE, CYBER_PINK

class CommandBar(tk.Frame):
    def __init__(self, parent, on_submit=None):
        super().__init__(parent, bg=CYBER_BLACK, padx=20, pady=20)
        self.on_submit = on_submit
        self._suggestion = ""

        # Suggestion Label (Above input)
        self.sugg_label = tk.Label(
            self,
            text="",
            bg=CYBER_BLACK,
            fg=CYBER_BLUE,
            font=("monospace", 8, "bold")
        )
        self.sugg_label.place(x=20, y=-10)

        # Input Container
        self.container = tk.Frame(self, bg=CYBER_BLACK)
        self.container.pack(fill="x")

        # Bottom Border line
        self.line = tk.Frame(self.container, bg="#333300", height=2)
        self.line.pack(fill="x", side="bottom")

        # Row for content
        self.row = tk.Frame(self.container, bg=CYBER_BLACK)
        self.row.pack(fill="x", side="top", pady=(0, 5))

        # Chevron >
        self.chevron = tk.Label(self.row, text=">", bg=CYBER_BLACK, fg=CYBER_YELLOW, font=("monospace", 12, "bold"))
        self.chevron.pack(side="left")

        # Input Frame
        self.input_frame = tk.Frame(self.row, bg=CYBER_BLACK)
        self.input_frame.pack(side="left", fill="x", expand=True, padx=10)

        # Suggestion overlay
        self.ghost = tk.Label(
            self.input_frame,
            text="",
            bg=CYBER_BLACK,
            fg="#222200",
            font=("monospace", 10, "bold italic"),
            anchor="w"
        )
        self.ghost.place(x=0, y=0, relwidth=1)

        # Entry
        self.entry = tk.Entry(
            self.input_frame,
            bg=CYBER_BLACK,
            fg=CYBER_YELLOW,
            insertbackground=CYBER_YELLOW,
            font=("monospace", 10, "bold italic"),
            relief="flat",
            borderwidth=0,
            highlightthickness=0
        )
        self.entry.pack(fill="x")
        self.entry.insert(0, "COMMAND...")
        self.entry.bind("<FocusIn>", self._on_focus)
        self.entry.bind("<KeyRelease>", self._on_key)
        self.entry.bind("<Return>", self._handle_submit)
        self.entry.bind("<Tab>", self._use_sugg)

        # Icons
        self.zap = tk.Label(self.row, text="⚡", bg=CYBER_BLACK, fg=CYBER_BLUE, font=("monospace", 12))
        self.zap.pack(side="right", padx=5)

        self.mic = tk.Label(self.row, text="🎙", bg=CYBER_BLACK, fg=CYBER_PINK, font=("monospace", 12))
        self.mic.pack(side="right", padx=5)

    def _on_focus(self, e):
        if self.entry.get() == "COMMAND...":
            self.entry.delete(0, tk.END)

    def _on_key(self, e):
        text = self.entry.get()
        if text.strip():
            self._suggestion = text.upper() + " SYNC"
            self.ghost.config(text=self._suggestion)
            self.sugg_label.config(text=f"TAB: {self._suggestion}")
        else:
            self.ghost.config(text="")
            self.sugg_label.config(text="")

    def _use_sugg(self, e):
        if self._suggestion:
            self.entry.delete(0, tk.END)
            self.entry.insert(0, self._suggestion)
        return "break"

    def _handle_submit(self, e):
        cmd = self.entry.get()
        if cmd and self.on_submit:
            self.on_submit(cmd)
        self.entry.delete(0, tk.END)
        self.ghost.config(text="")
        self.sugg_label.config(text="")
