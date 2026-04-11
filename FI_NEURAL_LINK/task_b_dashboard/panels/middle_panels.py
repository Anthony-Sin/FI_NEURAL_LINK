import tkinter as tk
from ..theme import CYBER_YELLOW, CYBER_BLUE, CYBER_BLACK, CYBER_PINK, FONT_FUTURISTIC_MED, BULLET_COLOR

class CyberPanel(tk.Frame):
    def __init__(self, parent, text, color, bullet=True):
        super().__init__(parent, bg=CYBER_BLACK)
        self.canvas = tk.Canvas(self, height=45, bg=CYBER_BLACK, highlightthickness=0)
        self.canvas.pack(fill="x", padx=15, pady=2)

        # Bracket aesthetic
        self.canvas.create_line(5, 5, 395, 5, fill=color)
        self.canvas.create_line(5, 40, 395, 40, fill=color)
        self.canvas.create_line(5, 5, 5, 40, fill=color, width=2)
        self.canvas.create_line(395, 10, 395, 35, fill=color)

        self.text_id = self.canvas.create_text(
            50 if bullet else 20, 22, text=text, fill=color, font=FONT_FUTURISTIC_MED, anchor="w"
        )
        if bullet:
            self.canvas.create_rectangle(25, 17, 35, 27, fill=BULLET_COLOR, outline=BULLET_COLOR)

    def update_text(self, text):
        self.canvas.itemconfig(self.text_id, text=text.upper())

class MiddlePanels(tk.Frame):
    def __init__(self, parent):
        super().__init__(parent, bg=CYBER_BLACK)

        self.container = tk.Frame(self, bg=CYBER_BLACK)
        self.container.pack(fill="both", expand=True)

        self.panels = []
        # Initial image state
        initial_data = [
            ("SYSTEM STATUS: OPTIMAL", CYBER_YELLOW),
            ("ENCRYPTING NEURAL DATA...", CYBER_BLUE),
            ("FI: 'I'M READY WHEN YOU ARE.'", CYBER_BLUE)
        ]

        for text, color in initial_data:
            p = CyberPanel(self.container, text, color)
            p.pack(fill="x")
            self.panels.append(p)

    def add_log(self, text, level="info"):
        # Cycle logic to keep 3 panels visible like the image
        color = CYBER_BLUE
        if level == "error": color = CYBER_PINK
        elif level == "warn": color = CYBER_YELLOW

        # Shift texts up
        for i in range(len(self.panels)-1):
            next_text = self.panels[i+1].canvas.itemcget(self.panels[i+1].text_id, "text")
            self.panels[i].update_text(next_text)

        self.panels[-1].update_text(text)
        # In a real log view we'd update colors too, but for reproduction
        # we'll just update the last panel's text content.
