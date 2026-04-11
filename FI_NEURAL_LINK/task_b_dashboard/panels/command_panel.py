import tkinter as tk

class CommandPanel(tk.Frame):
    def __init__(self, parent, on_submit=None):
        super().__init__(parent, bg="#0d0d0f")
        self.on_submit = on_submit

        # Container for Entry and Button
        input_frame = tk.Frame(self, bg="#0d0d0f")
        input_frame.pack(fill="x", expand=True)

        self.entry = tk.Entry(
            input_frame,
            bg="#111118",
            fg="#00ff88",
            insertbackground="#00ff88",
            highlightthickness=1,
            highlightbackground="#00ff88",
            highlightcolor="#00ff88",
            font=("monospace", 13),
            relief="flat"
        )
        self.entry.pack(side="left", padx=5, pady=5, expand=True, fill="x")
        self.entry.bind("<Return>", lambda e: self._handle_submit())

        self.run_btn = tk.Button(
            input_frame,
            text="Run",
            bg="#111118",
            fg="#00ff88",
            activebackground="#00ff88",
            activeforeground="#111118",
            font=("monospace", 13),
            relief="flat",
            padx=10
        )
        self.run_btn.configure(command=self._handle_submit)
        self.run_btn.pack(side="right", padx=5, pady=5)

        # Status label below
        self.status_label = tk.Label(
            self,
            text="READY",
            bg="#0d0d0f",
            fg="#00ff88",
            font=("monospace", 10),
            anchor="w"
        )
        self.status_label.pack(fill="x", padx=10, pady=(0, 5))

    def _handle_submit(self):
        command = self.entry.get()
        if command and self.on_submit:
            self.on_submit(command)
        self.entry.delete(0, tk.END)

    def set_status(self, text, color):
        self.status_label.configure(text=text, fg=color)
