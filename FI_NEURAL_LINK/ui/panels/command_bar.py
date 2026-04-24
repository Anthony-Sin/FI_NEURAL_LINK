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
        self.entry.bind("<Control-v>", self._handle_paste)
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

        # Attachment card for long text/recording (Cyberpunk style)
        self.attachment_card = tk.Frame(self, bg="#1a1a00", padx=10, pady=10, cursor="hand2")
        self.attachment_card.pack(fill="x", padx=10, pady=5)
        self.attachment_card.pack_forget()
        self.attachment_card.bind("<Button-1>", self._preview_attachment)

        self.card_label = tk.Label(
            self.attachment_card, text="", bg="#1a1a00", fg=CYBER_WHITE,
            font=("Consolas", 8), justify="left", anchor="w", wraplength=200,
            cursor="hand2"
        )
        self.card_label.pack(side="left", fill="x", expand=True)
        self.card_label.bind("<Button-1>", self._preview_attachment)

        self.remove_btn = tk.Label(
            self.attachment_card, text="REMOVE", bg="#1a1a00", fg=CYBER_PINK,
            font=("Consolas", 8, "bold"), cursor="hand2", padx=5
        )
        self.remove_btn.pack(side="right")
        self.remove_btn.bind("<Button-1>", self._remove_attachment)

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
        # Trigger height update on every keypress
        self._update_height()

        content = self.entry.get("1.0", "end-1c")
        words = content.split()

        # Handle large input (> 100 words) -> show card
        if len(words) > 100:
            full_text = self.entry.get("1.0", tk.END).strip()
            self.entry.delete("1.0", tk.END)
            self.show_attachment(f"LONG TEXT: {words[0]}... {words[-1]}", full_content=full_text)
        elif not getattr(self, '_recording_active', False) and not getattr(self, '_long_text_active', False):
            self.attachment_card.pack_forget()

        if content.strip():
            self._suggestion = content.upper().split('\n')[0] + " SYNC"
        else:
            self._suggestion = ""

    def _update_height(self):
        """Measures text lines and updates widget height."""
        try:
            # Force update of internal geometry
            self.entry.update_idletasks()
            # Calculate height based on line count in the widget
            # We look at the actual wrapped lines if possible, or just newlines
            content = self.entry.get("1.0", "end-1c")
            line_count = content.count('\n') + 1

            # Simple check for wrapping: if width is small, we might have more lines
            # For now, 1 line per 40 chars is a safe fallback
            char_count = len(content)
            est_lines = max(line_count, (char_count // 35) + 1)

            new_height = min(max(est_lines, 1), 5)
            self.entry.config(height=new_height)
        except: pass

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

    def show_attachment(self, text, full_content=None):
        self.card_label.config(text=text)
        self.attachment_card.pack(fill="x", padx=10, pady=5, before=self.top_line)
        self._recording_active = "RECORDING" in text
        self._long_text_active = "LONG TEXT" in text
        self._full_content = full_content

    def _preview_attachment(self, e):
        content = self._full_content
        if not content and self._recording_active:
            from FI_NEURAL_LINK.tools.automation.recorder import get_recorded_summary
            content = get_recorded_summary()

        if content:
            top = tk.Toplevel(self)
            top.title("DATA PREVIEW")
            top.geometry("300x400")
            top.configure(bg="#0a0a0a")

            txt = tk.Text(top, bg="#0a0a0a", fg=CYBER_YELLOW, font=("Consolas", 9), padx=10, pady=10)
            txt.pack(fill="both", expand=True)
            txt.insert("1.0", content)
            txt.config(state="disabled")

    def _handle_paste(self, e):
        # Check clipboard content
        try:
            pasted_text = self.clipboard_get()
            words = pasted_text.split()
            if len(words) > 50: # If long, don't paste in box, put in card
                self.show_attachment(f"LONG TEXT (PASTED): {words[0]}... {words[-1]}", full_content=pasted_text)
                return "break"
        except: pass

        # Default paste behavior
        self.after(10, self._update_height)
        return None

    def _remove_attachment(self, e):
        self.attachment_card.pack_forget()
        self._recording_active = False
        if hasattr(self, 'on_remove_attachment'):
            self.on_remove_attachment()

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