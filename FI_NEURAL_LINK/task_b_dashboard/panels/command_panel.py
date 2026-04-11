import tkinter as tk
from ..theme import CYBER_YELLOW, CYBER_BLACK, CYBER_BLUE, CYBER_PINK, CYBER_GRAY, FONT_MONO_MED, FONT_MONO_SMALL

class CommandPanel(tk.Frame):
    def __init__(self, parent, on_submit=None):
        super().__init__(parent, bg=CYBER_BLACK)
        self.on_submit = on_submit

        self.suggestions = ["Launch Chrome", "Search for AI news", "Type 'Hello World'", "Read the screen"]

        # Suggestions frame
        self.suggestions_frame = tk.Frame(self, bg=CYBER_BLACK)
        self.suggestions_frame.pack(fill="x", padx=10)

        self._update_suggestions()

        # Input container
        self.input_container = tk.Frame(self, bg=CYBER_BLACK, highlightthickness=1, highlightbackground=CYBER_YELLOW)
        self.input_container.pack(fill="x", padx=10, pady=5)

        # Leading prompt icon
        self.prompt_label = tk.Label(self.input_container, text=">", bg=CYBER_BLACK, fg=CYBER_YELLOW, font=FONT_MONO_MED)
        self.prompt_label.pack(side="left", padx=(5, 0))

        # Text area (dynamic expanding)
        self.text_input = tk.Text(
            self.input_container,
            height=1,
            bg=CYBER_BLACK,
            fg=CYBER_YELLOW,
            insertbackground=CYBER_YELLOW,
            font=FONT_MONO_MED,
            relief="flat",
            borderwidth=0,
            highlightthickness=0
        )
        self.text_input.pack(side="left", fill="x", expand=True, padx=5, pady=5)
        self.text_input.bind("<KeyRelease>", self._on_key_release)
        self.text_input.bind("<Return>", self._handle_return)

        # Action Buttons
        self.voice_btn = tk.Label(
            self.input_container,
            text="🎙",
            bg=CYBER_BLACK,
            fg=CYBER_PINK,
            font=FONT_MONO_MED,
            cursor="hand2"
        )
        self.voice_btn.pack(side="right", padx=5)

        self.model_btn = tk.Label(
            self.input_container,
            text="⚡",
            bg=CYBER_BLACK,
            fg=CYBER_BLUE,
            font=FONT_MONO_MED,
            cursor="hand2"
        )
        self.model_btn.pack(side="right", padx=5)

        # File icon for collapsed large input
        self.file_icon = tk.Label(
            self.input_container,
            text="📄",
            bg=CYBER_BLACK,
            fg=CYBER_YELLOW,
            font=FONT_MONO_MED,
            cursor="hand2"
        )
        # Not packed initially

        self._full_text = ""

    def _on_key_release(self, event):
        content = self.text_input.get("1.0", "end-1c")

        # Clear suggestions on typing
        if content:
            for child in self.suggestions_frame.winfo_children():
                child.destroy()
        else:
            self._update_suggestions()

        # Dynamic expansion
        num_lines = int(self.text_input.index('end-1c').split('.')[0])
        self.text_input.config(height=min(num_lines, 5))

        # 100 words check
        words = content.split()
        if len(words) > 100:
            self._full_text = content
            self.text_input.pack_forget()
            self.file_icon.pack(side="left", padx=5)
            self.text_input.delete("1.0", tk.END)
            self.text_input.insert("1.0", "[LARGE INPUT STORED]")
            self.text_input.config(state="disabled")

    def _update_suggestions(self):
        for child in self.suggestions_frame.winfo_children():
            child.destroy()

        for s in self.suggestions[:3]:
            btn = tk.Label(
                self.suggestions_frame,
                text=s,
                bg=CYBER_GRAY,
                fg=CYBER_BLUE,
                font=FONT_MONO_SMALL,
                padx=5,
                pady=2,
                cursor="hand2"
            )
            btn.pack(side="left", padx=2, pady=2)
            btn.bind("<Button-1>", lambda e, text=s: self._use_suggestion(text))

    def _use_suggestion(self, text):
        self.text_input.delete("1.0", tk.END)
        self.text_input.insert("1.0", text)
        for child in self.suggestions_frame.winfo_children():
            child.destroy()

    def _handle_return(self, event):
        content = self.text_input.get("1.0", "end-1c")
        if self._full_text:
            command = self._full_text
            self._full_text = ""
            self.file_icon.pack_forget()
            self.text_input.config(state="normal")
            self.text_input.pack(side="left", fill="x", expand=True, padx=5, pady=5)
        else:
            command = content

        if command and self.on_submit:
            self.on_submit(command.strip())

        self.text_input.delete("1.0", tk.END)
        self.text_input.config(height=1)
        self._update_suggestions()
        return "break"
