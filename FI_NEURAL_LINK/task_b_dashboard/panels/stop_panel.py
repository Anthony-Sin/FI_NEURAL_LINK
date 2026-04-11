import tkinter as tk
import threading

# Module-level singleton STOP_EVENT
STOP_EVENT = threading.Event()

class StopPanel(tk.Frame):
    def __init__(self, parent):
        super().__init__(parent, bg="#0d0d0f")

        # Status Label
        self.status_label = tk.Label(
            self,
            text="RUNNING",
            bg="#0d0d0f",
            fg="#00ff88",
            font=("monospace", 12, "bold")
        )
        self.status_label.pack(pady=(5, 0))

        # EMERGENCY STOP button
        self.stop_btn = tk.Button(
            self,
            text="EMERGENCY STOP",
            bg="#ff2222",
            fg="white",
            activebackground="#ff4444",
            activeforeground="white",
            font=("monospace", 14, "bold"),
            relief="flat",
            command=self._handle_stop
        )
        self.stop_btn.pack(fill="x", padx=10, pady=5)

        # Resume button
        self.resume_btn = tk.Button(
            self,
            text="Resume",
            bg="#111118",
            fg="#00ff88",
            activebackground="#00ff88",
            activeforeground="#111118",
            font=("monospace", 10),
            relief="flat",
            command=self._handle_resume
        )
        self.resume_btn.pack(padx=10, pady=(0, 5))

    def _handle_stop(self):
        STOP_EVENT.set()
        self.status_label.configure(text="STOPPED", fg="#ff4444")

    def _handle_resume(self):
        STOP_EVENT.clear()
        self.status_label.configure(text="RUNNING", fg="#00ff88")
