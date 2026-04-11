import tkinter as tk
from ..theme import CYBER_YELLOW, CYBER_BLACK, CYBER_BLUE, CYBER_PINK, CYBER_GRAY, FONT_FUTURISTIC_MED, FONT_FUTURISTIC_SMALL

class CommandBar(tk.Frame):
    def __init__(self, parent, on_submit=None):
        super().__init__(parent, bg=CYBER_BLACK)
        self.on_submit = on_submit
        self._full_text_cache = ""
        self.suggestions = ["Launch Chrome", "Search for AI news", "Check system status"]

        # Suggestions area
        self.sugg_frame = tk.Frame(self, bg=CYBER_BLACK)
        self.sugg_frame.pack(fill="x", padx=10)
        self._update_suggestions()

        # Input Row
        self.input_row = tk.Frame(self, bg=CYBER_BLACK)
        self.input_row.pack(fill="x", padx=10, pady=5)

        # > Prompt
        self.prompt = tk.Label(self.input_row, text=">", bg=CYBER_BLACK, fg=CYBER_YELLOW, font=FONT_FUTURISTIC_MED)
        self.prompt.pack(side="left")

        # Icons Container (packed first on the right so they stay there)
        self.icon_frame = tk.Frame(self.input_row, bg=CYBER_BLACK)
        self.icon_frame.pack(side="right")

        # Bolt Icon (Canvas)
        self.bolt_canvas = tk.Canvas(self.icon_frame, width=30, height=30, bg=CYBER_BLACK, highlightthickness=0, cursor="hand2")
        self.bolt_canvas.pack(side="right", padx=2)
        self._draw_bolt(CYBER_BLUE)

        # Mic Icon (Canvas)
        self.mic_canvas = tk.Canvas(self.icon_frame, width=30, height=30, bg=CYBER_BLACK, highlightthickness=0, cursor="hand2")
        self.mic_canvas.pack(side="right", padx=2)
        self._draw_mic(CYBER_PINK)

        # Text input (dynamic expanding)
        self.entry = tk.Text(
            self.input_row,
            height=1,
            bg=CYBER_BLACK,
            fg=CYBER_YELLOW,
            insertbackground=CYBER_YELLOW,
            font=FONT_FUTURISTIC_MED,
            relief="flat",
            borderwidth=0,
            highlightthickness=1,
            highlightbackground=CYBER_GRAY,
            undo=True
        )
        self.entry.pack(side="left", fill="x", expand=True, padx=10)
        self.entry.insert("1.0", "COMMAND...")
        self.entry.bind("<FocusIn>", self._clear_placeholder)
        self.entry.bind("<FocusOut>", self._add_placeholder)
        self.entry.bind("<KeyRelease>", self._on_key)
        self.entry.bind("<Return>", self._handle_submit)

        # File icon
        self.file_icon = tk.Label(self.input_row, text="[FILE]", bg=CYBER_BLACK, fg=CYBER_YELLOW, font=FONT_FUTURISTIC_SMALL)

    def _draw_bolt(self, color):
        self.bolt_canvas.delete("all")
        # Lightning bolt shape
        points = [15, 5, 25, 5, 10, 15, 20, 15, 5, 25, 15, 12, 10, 12]
        self.bolt_canvas.create_polygon(points, fill=color, outline=color)

    def _draw_mic(self, color):
        self.mic_canvas.delete("all")
        # Mic shape
        self.mic_canvas.create_oval(10, 5, 20, 18, fill=color, outline=color)
        self.mic_canvas.create_arc(5, 10, 25, 22, start=180, extent=180, outline=color, style="arc", width=2)
        self.mic_canvas.create_line(15, 22, 15, 26, fill=color, width=2)

    def _clear_placeholder(self, event):
        if self.entry.get("1.0", "end-1c") == "COMMAND...":
            self.entry.delete("1.0", tk.END)
        for child in self.sugg_frame.winfo_children(): child.destroy()

    def _add_placeholder(self, event):
        if not self.entry.get("1.0", "end-1c").strip():
            self.entry.delete("1.0", tk.END)
            self.entry.insert("1.0", "COMMAND...")
            self.entry.config(height=1)
            self._update_suggestions()

    def _on_key(self, event):
        content = self.entry.get("1.0", "end-1c")
        words = content.split()
        if len(words) > 100 and not self._full_text_cache:
            self._full_text_cache = content
            self.entry.delete("1.0", tk.END)
            self.entry.insert("1.0", "[INPUT OVERFLOW]")
            self.entry.config(state="disabled", height=1)
            self.file_icon.pack(side="left", before=self.entry)
        if not self._full_text_cache:
            num_lines = int(self.entry.index('end-1c').split('.')[0])
            self.entry.config(height=min(num_lines, 5))

    def _update_suggestions(self):
        for child in self.sugg_frame.winfo_children(): child.destroy()
        for s in self.suggestions:
            b = tk.Label(self.sugg_frame, text=s, bg=CYBER_GRAY, fg=CYBER_BLUE, font=FONT_FUTURISTIC_SMALL, padx=5, cursor="hand2")
            b.pack(side="left", padx=2, pady=2)
            b.bind("<Button-1>", lambda e, text=s: self._use_suggestion(text))

    def _use_suggestion(self, text):
        self.entry.delete("1.0", tk.END)
        self.entry.insert("1.0", text)
        for child in self.sugg_frame.winfo_children(): child.destroy()

    def _handle_submit(self, event=None):
        if self._full_text_cache:
            cmd = self._full_text_cache
            self._full_text_cache = ""
            self.entry.config(state="normal")
            self.file_icon.pack_forget()
        else:
            cmd = self.entry.get("1.0", "end-1c")
        if cmd and cmd != "COMMAND...":
            if self.on_submit:
                self.on_submit(cmd.strip())
            self.entry.delete("1.0", tk.END)
            self.entry.config(height=1)
            self._update_suggestions()
        return "break"
