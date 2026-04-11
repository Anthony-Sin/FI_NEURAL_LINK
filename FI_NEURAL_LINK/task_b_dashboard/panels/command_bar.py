import tkinter as tk
from ..theme import CYBER_YELLOW, CYBER_BLACK, CYBER_BLUE, CYBER_PINK

class CommandBar(tk.Frame):
    def __init__(self, parent, on_submit=None):
        super().__init__(parent, bg=CYBER_BLACK)
        self.on_submit = on_submit
        self._suggestion = ""

        # ── Yellow top separator ──────────────────────────────────────────────
        self.top_line = tk.Frame(self, bg=CYBER_YELLOW, height=1)
        self.top_line.pack(fill="x")

        # ── Input row ────────────────────────────────────────────────────────
        self.row = tk.Frame(self, bg=CYBER_BLACK, padx=10, pady=8)
        self.row.pack(fill="x")

        # Chevron
        self.chevron = tk.Label(
            self.row, text=">", bg=CYBER_BLACK, fg=CYBER_YELLOW,
            font=("Consolas", 11, "bold")
        )
        self.chevron.pack(side="left", padx=(0, 6))

        # Entry
        self.entry = tk.Entry(
            self.row,
            bg=CYBER_BLACK,
            fg="#555500",                           # dim placeholder colour
            insertbackground=CYBER_YELLOW,
            font=("Consolas", 9, "bold italic"),
            relief="flat",
            borderwidth=0,
            highlightthickness=0
        )
        self.entry.pack(side="left", fill="x", expand=True)
        self.entry.insert(0, "COMMAND...")
        self.entry.bind("<FocusIn>",   self._on_focus)
        self.entry.bind("<FocusOut>",  self._on_blur)
        self.entry.bind("<KeyRelease>", self._on_key)
        self.entry.bind("<Return>",    self._handle_submit)
        self.entry.bind("<Tab>",       self._use_sugg)

        # Mic button  ──  keep name mic_btn so dashboard can bind to it
        self.mic_btn = tk.Label(
            self.row, text="⏺", bg=CYBER_BLACK, fg=CYBER_PINK,
            font=("Consolas", 13), cursor="hand2"
        )
        self.mic_btn.pack(side="left", padx=(8, 4))

        # Bolt / submit button
        self.bolt_btn = tk.Label(
            self.row, text="⚡", bg=CYBER_BLACK, fg=CYBER_YELLOW,
            font=("Consolas", 12), cursor="hand2"
        )
        self.bolt_btn.pack(side="left", padx=(0, 2))
        self.bolt_btn.bind("<Button-1>", lambda e: self._handle_submit(e))

    # ── Public API ────────────────────────────────────────────────────────────

    def set_mic_active(self, active: bool):
        if active:
            self.mic_btn.config(fg="#ff4466")   # bright pink = listening
        else:
            self.mic_btn.config(fg=CYBER_PINK)

    # ── Private ───────────────────────────────────────────────────────────────

    def _on_focus(self, e):
        if self.entry.get() == "COMMAND...":
            self.entry.delete(0, tk.END)
            self.entry.config(fg=CYBER_YELLOW)

    def _on_blur(self, e):
        if not self.entry.get().strip():
            self.entry.delete(0, tk.END)
            self.entry.insert(0, "COMMAND...")
            self.entry.config(fg="#555500")

    def _on_key(self, e):
        text = self.entry.get()
        if text.strip():
            self._suggestion = text.upper() + " SYNC"
        else:
            self._suggestion = ""

    def _use_sugg(self, e):
        if self._suggestion:
            self.entry.delete(0, tk.END)
            self.entry.insert(0, self._suggestion)
        return "break"

    def _handle_submit(self, e):
        cmd = self.entry.get()
        if cmd and cmd != "COMMAND..." and self.on_submit:
            self.on_submit(cmd)
        self.entry.delete(0, tk.END)
        self._on_blur(None)
        self._suggestion = ""