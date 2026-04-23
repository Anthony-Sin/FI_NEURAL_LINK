import tkinter as tk
from ..theme import CYBER_YELLOW, CYBER_BLACK, CYBER_BLUE, CYBER_PINK

class CommandBar(tk.Frame):
    def __init__(self, parent, on_submit=None):
        super().__init__(parent, bg=CYBER_BLACK)
        self.on_submit = on_submit
        self._suggestion = ""
        self._history = []
        self._history_idx = -1

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

        # Entry (Using Text for dynamic expansion)
        self.entry_frame = tk.Frame(self.row, bg=CYBER_BLACK)
        self.entry_frame.pack(side="left", fill="x", expand=True)

        self.entry = tk.Text(
            self.entry_frame,
            bg=CYBER_BLACK,
            fg="#555500",                           # dim placeholder colour
            insertbackground=CYBER_YELLOW,
            font=("Consolas", 9, "bold italic"),
            relief="flat",
            borderwidth=0,
            highlightthickness=0,
            height=1,
            undo=True
        )
        self.entry.pack(fill="x", expand=True)
        self.entry.insert("1.0", "COMMAND...")

        self.file_icon = tk.Label(
            self.entry_frame, text="📄", bg=CYBER_BLACK, fg=CYBER_YELLOW,
            font=("Consolas", 12)
        )
        # Hidden initially
        self.file_icon.pack_forget()

        self.entry.bind("<FocusIn>",   self._on_focus)
        self.entry.bind("<FocusOut>",  self._on_blur)
        self.entry.bind("<KeyRelease>", self._on_key)
        self.entry.bind("<Return>",    self._handle_submit)
        self.entry.bind("<Tab>",       self._use_sugg)
        self.entry.bind("<Up>",        self._prev_cmd)
        self.entry.bind("<Down>",      self._next_cmd)

        # Mic button  ──  keep name mic_btn so dashboard can bind to it
        self.mic_btn = tk.Label(
            self.row, text="⏺", bg=CYBER_BLACK, fg=CYBER_PINK,
            font=("Consolas", 13), cursor="hand2"
        )
        self.mic_btn.pack(side="left", padx=(8, 4))

        # Record button
        self.rec_btn = tk.Label(
            self.row, text="REC", bg=CYBER_BLACK, fg=CYBER_PINK,
            font=("Consolas", 9, "bold"), cursor="hand2",
            padx=5, pady=2, relief="flat"
        )
        self.rec_btn.pack(side="left", padx=(0, 5))

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
        if self.entry.get("1.0", "end-1c") == "COMMAND...":
            self.entry.delete("1.0", tk.END)
            self.entry.config(fg=CYBER_YELLOW)

    def _on_blur(self, e):
        content = self.entry.get("1.0", "end-1c").strip()
        if not content:
            self.entry.delete("1.0", tk.END)
            self.entry.insert("1.0", "COMMAND...")
            self.entry.config(fg="#555500", height=1)
            self.file_icon.pack_forget()
            self.entry.pack(fill="x", expand=True)

    def _on_key(self, e):
        content = self.entry.get("1.0", "end-1c")
        words = content.split()

        # 1. Handle dynamic height
        try:
            num_lines = int(self.entry.index('end-1c').split('.')[0])
            new_height = min(max(num_lines, 1), 5)
            self.entry.config(height=new_height)
        except: pass

        # 2. Handle large input (> 100 words)
        if len(words) > 100:
            if not self.file_icon.winfo_ismapped():
                self.entry.pack_forget()
                self.file_icon.pack(side="left", padx=5, fill="both", expand=True)
        else:
            if self.file_icon.winfo_ismapped():
                self.file_icon.pack_forget()
                self.entry.pack(fill="x", expand=True)

        if content.strip():
            self._suggestion = content.upper().split('\n')[0] + " SYNC"
        else:
            self._suggestion = ""

    def _use_sugg(self, e):
        if self._suggestion:
            self.entry.delete("1.0", tk.END)
            self.entry.insert("1.0", self._suggestion)
        return "break"

    def _prev_cmd(self, e):
        if not self._history: return "break"
        self._history_idx = min(self._history_idx + 1, len(self._history) - 1)
        self.entry.delete("1.0", tk.END)
        self.entry.insert("1.0", self._history[self._history_idx])
        self.entry.config(fg=CYBER_YELLOW)
        return "break"

    def _next_cmd(self, e):
        self._history_idx -= 1
        self.entry.delete("1.0", tk.END)
        if self._history_idx >= 0:
            self.entry.insert("1.0", self._history[self._history_idx])
            self.entry.config(fg=CYBER_YELLOW)
        else:
            self._history_idx = -1
            self._on_blur(None)
        return "break"

    def _handle_submit(self, e):
        # Shift+Enter for new line, Enter for submit
        if e.state & 0x0001: # Shift key
            return

        cmd = self.entry.get("1.0", "end-1c").strip()
        if cmd and cmd != "COMMAND..." and self.on_submit:
            # Add to history if not same as last
            if not self._history or cmd != self._history[0]:
                self._history.insert(0, cmd)
                if len(self._history) > 20: self._history.pop()
            self._history_idx = -1
            self.on_submit(cmd)

        self.entry.delete("1.0", tk.END)
        self._on_blur(None)
        self._suggestion = ""
        return "break" # Prevent newline from Enter