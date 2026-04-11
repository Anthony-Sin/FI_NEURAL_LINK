import tkinter as tk

class CommandPanel(tk.Frame):
    def __init__(self, parent, on_submit, **kwargs):
        bg_color = kwargs.get('bg', '#0d0d0f')
        super().__init__(parent, bg=bg_color, **kwargs)

        self.on_submit = on_submit

        entry_bg = "#111118"
        neon_green = "#00ff88"
        mono_font = ("Courier", 13)

        self.input_container = tk.Frame(self, bg=bg_color)
        self.input_container.pack(fill=tk.X, padx=10, pady=(10, 0))

        self.entry = tk.Entry(
            self.input_container,
            bg=entry_bg,
            fg=neon_green,
            insertbackground=neon_green,
            font=mono_font,
            bd=1,
            highlightthickness=1,
            highlightbackground=neon_green,
            highlightcolor=neon_green,
            relief=tk.FLAT
        )
        self.entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 5))

        self.run_button = tk.Button(
            self.input_container,
            text="Run",
            command=self._handle_submit,
            bg=entry_bg,
            fg=neon_green,
            activebackground=neon_green,
            activeforeground=entry_bg,
            font=mono_font,
            bd=1,
            highlightthickness=1,
            highlightbackground=neon_green,
            highlightcolor=neon_green,
            relief=tk.FLAT,
            padx=10
        )
        self.run_button.pack(side=tk.LEFT)

        self.status_label = tk.Label(
            self,
            text="",
            bg=bg_color,
            fg="#ffffff",
            font=("Arial", 10),
            anchor=tk.W
        )
        self.status_label.pack(fill=tk.X, padx=10, pady=(5, 10))

        self.entry.bind("<Return>", lambda e: self._handle_submit())

    def _handle_submit(self):
        command = self.entry.get()
        if self.on_submit:
            self.on_submit(command)
        self.entry.delete(0, tk.END)

    def set_status(self, text, color):
        self.status_label.config(text=text, fg=color)
