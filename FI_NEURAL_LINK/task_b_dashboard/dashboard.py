import tkinter as tk
import threading
from FI_NEURAL_LINK.task_b_dashboard.overlay.overlay_window import OverlayWindow
from FI_NEURAL_LINK.task_b_dashboard.panels.command_panel import CommandPanel
from FI_NEURAL_LINK.task_b_dashboard.panels.log_panel import LogPanel
from FI_NEURAL_LINK.task_b_dashboard.panels.stop_panel import StopPanel

class Dashboard:
    def __init__(self):
        self.root = OverlayWindow()

        # Title bar row
        title_bar = tk.Frame(self.root, bg="#0d0d0f")
        title_bar.pack(fill="x", padx=10, pady=5)

        title_label = tk.Label(
            title_bar,
            text="FI_NEURAL_LINK",
            bg="#0d0d0f",
            fg="#00ff88",
            font=("monospace", 14, "bold")
        )
        title_label.pack(side="left")

        # Close button (X) in the top-right corner of the title bar
        self.close_btn = tk.Label(
            title_bar,
            text="X",
            bg="#0d0d0f",
            fg="#ff4444",
            font=("monospace", 12, "bold"),
            cursor="hand2"
        )
        self.close_btn.pack(side="right")
        self.close_btn.bind("<Button-1>", lambda e: self.root.hide())

        # Panels
        self.log_panel = LogPanel(self.root)
        self.log_panel.pack(fill="both", expand=True) # Flex height

        self.command_panel = CommandPanel(self.root)
        self.command_panel.pack(fill="x")

        self.stop_panel = StopPanel(self.root)
        self.stop_panel.pack(fill="x")

        # Apply recursive drag binding to all components
        # We do this after all widgets are created
        self.root.bind_drag_to_all(self.root)

    def start(self):
        # Launches the tkinter mainloop in a daemon thread
        threading.Thread(target=self.root.mainloop, daemon=True).start()

    def log(self, text, level="info"):
        self.root.after(0, self.log_panel.append_line, text, level)

    def set_on_submit(self, callback):
        self.command_panel.on_submit = callback
