import tkinter as tk
from ..theme import CYBER_YELLOW, CYBER_BLACK, CYBER_BLUE, CYBER_PINK, FONT_MONO_SMALL, FONT_MONO_MED

class StatusBar(tk.Frame):
    def __init__(self, parent):
        super().__init__(parent, bg=CYBER_BLACK)

        # Model Indicator Container
        self.model_frame = tk.Frame(self, bg=CYBER_BLACK)
        self.model_frame.pack(side="left", padx=10, pady=5)

        self.model_led = tk.Canvas(self.model_frame, width=12, height=12, bg=CYBER_BLACK, highlightthickness=0)
        self.model_led.pack(side="left", padx=(0, 5))
        self.led_circle = self.model_led.create_oval(2, 2, 10, 10, fill=CYBER_BLUE, outline=CYBER_BLUE)

        self.model_label = tk.Label(
            self.model_frame,
            text="MODEL: GEMINI-1.5-FLASH",
            bg=CYBER_BLACK,
            fg=CYBER_BLUE,
            font=FONT_MONO_SMALL
        )
        self.model_label.pack(side="left")

        # Prompt Counter
        self.counter_label = tk.Label(
            self,
            text="PROMPTS: 0",
            bg=CYBER_BLACK,
            fg=CYBER_YELLOW,
            font=FONT_MONO_SMALL
        )
        self.counter_label.pack(side="right", padx=10)

        self.prompt_count = 0
        self._pulse_state = False

    def increment_counter(self):
        self.prompt_count += 1
        self.counter_label.config(text=f"PROMPTS: {self.prompt_count}")

    def set_model_state(self, status="active"):
        if status == "active":
            self.model_led.itemconfig(self.led_circle, fill=CYBER_BLUE, outline=CYBER_BLUE)
            self.model_label.config(fg=CYBER_BLUE)
        elif status == "error":
            self.model_led.itemconfig(self.led_circle, fill=CYBER_PINK, outline=CYBER_PINK)
            self.model_label.config(fg=CYBER_PINK)
            self._pulse_error()
        elif status == "switching":
            self.model_led.itemconfig(self.led_circle, fill=CYBER_YELLOW, outline=CYBER_YELLOW)
            self.model_label.config(fg=CYBER_YELLOW)

    def _pulse_error(self):
        if self.model_label.cget("fg") == CYBER_PINK:
            new_color = CYBER_BLACK if self._pulse_state else CYBER_PINK
            self.model_led.itemconfig(self.led_circle, fill=new_color)
            self._pulse_state = not self._pulse_state
            self.after(500, self._pulse_error)
