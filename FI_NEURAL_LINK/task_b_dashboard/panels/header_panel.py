import tkinter as tk
from ..theme import CYBER_BLUE, CYBER_YELLOW, CYBER_BLACK, CYBER_PINK, FONT_FUTURISTIC_SMALL, FONT_FUTURISTIC_MED

class HeaderPanel(tk.Frame):
    def __init__(self, parent):
        super().__init__(parent, bg=CYBER_BLACK)

        self.container = tk.Frame(self, bg=CYBER_BLACK)
        self.container.pack(fill="x", padx=10, pady=5)

        # Model Indicator
        self.model_frame = tk.Frame(self.container, bg=CYBER_BLACK)
        self.model_frame.pack(side="left")

        self.led = tk.Canvas(self.model_frame, width=12, height=12, bg=CYBER_BLACK, highlightthickness=0)
        self.led.pack(side="left", padx=5)
        self.status_light = self.led.create_oval(2, 2, 10, 10, fill=CYBER_BLUE, outline=CYBER_BLUE)

        self.model_label = tk.Label(
            self.model_frame,
            text="MODEL: GEMINI-1.5-FLASH",
            bg=CYBER_BLACK,
            fg=CYBER_BLUE,
            font=FONT_FUTURISTIC_SMALL
        )
        self.model_label.pack(side="left")

        # Prompt Counter
        self.counter_label = tk.Label(
            self.container,
            text="PROMPTS: 0",
            bg=CYBER_BLACK,
            fg=CYBER_YELLOW,
            font=FONT_FUTURISTIC_SMALL
        )
        self.counter_label.pack(side="right")

        self.prompt_count = 0
        self._pulse_state = False

    def increment_prompt(self):
        self.prompt_count += 1
        self.counter_label.config(text=f"PROMPTS: {self.prompt_count}")

    def set_model_error(self, active=True):
        if active:
            self.model_label.config(fg=CYBER_PINK, text="MODEL: ERROR")
            self._pulse_pink()
        else:
            self.model_label.config(fg=CYBER_BLUE, text="MODEL: GEMINI-1.5-FLASH")
            self.led.itemconfig(self.status_light, fill=CYBER_BLUE, outline=CYBER_BLUE)

    def _pulse_pink(self):
        if "ERROR" in self.model_label.cget("text"):
            color = CYBER_BLACK if self._pulse_state else CYBER_PINK
            self.led.itemconfig(self.status_light, fill=color, outline=color)
            self._pulse_state = not self._pulse_state
            self.after(500, self._pulse_pink)
