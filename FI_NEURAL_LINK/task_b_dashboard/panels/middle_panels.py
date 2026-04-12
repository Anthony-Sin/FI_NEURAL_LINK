import tkinter as tk
from ..theme import CYBER_YELLOW, CYBER_BLACK, CYBER_PINK

# ── Activity Log Bar ──────────────────────────────────────────────────────────

class ActivityBar(tk.Frame):
    def __init__(self, parent, text=""):
        super().__init__(parent, bg=CYBER_BLACK)

        self.border = tk.Frame(self, bg=CYBER_YELLOW, width=2)
        self.border.pack(side="left", fill="y")

        self.content = tk.Frame(self, bg="#0d0d00", padx=10, pady=7)
        self.content.pack(side="left", fill="both", expand=True)

        self.dot_canvas = tk.Canvas(
            self.content, width=8, height=8, bg="#0d0d00", highlightthickness=0
        )
        self.dot_canvas.pack(side="left", padx=(0, 9))
        self.dot = self.dot_canvas.create_rectangle(1, 1, 7, 7, fill=CYBER_PINK, outline=CYBER_PINK)

        self.label = tk.Label(
            self.content,
            text=text.upper(),
            bg="#0d0d00",
            fg=CYBER_YELLOW,
            font=("Consolas", 9, "bold italic"),
            anchor="w"
        )
        self.label.pack(side="left", fill="x", expand=True)

        self._pulse_state = True
        self._pulse()

    def _pulse(self):
        color = CYBER_PINK if self._pulse_state else "#1a0000"
        self.dot_canvas.itemconfig(self.dot, fill=color, outline=color)
        self._pulse_state = not self._pulse_state
        self.after(600, self._pulse)

    def update_text(self, text, level="info"):
        # Truncate and uppercase for consistency
        clean_text = text.strip().upper()
        if len(clean_text) > 40:
            clean_text = clean_text[:37] + "..."
        self.label.config(text=clean_text)

        # Color code based on level
        color_map = {
            "info": CYBER_YELLOW,
            "success": "#00ff88", # Cyber Green
            "warning": "#ffaa00", # Cyber Orange
            "error": CYBER_PINK,
            "debug": "#00f0ff"    # Cyber Blue
        }
        self.label.config(fg=color_map.get(level.lower(), CYBER_YELLOW))


# ── Middle Panel ──────────────────────────────────────────────────────────────

class MiddlePanels(tk.Frame):
    def __init__(self, parent):
        super().__init__(parent, bg=CYBER_BLACK)

        self.container = tk.Frame(self, bg=CYBER_BLACK, padx=14, pady=16)
        self.container.pack(fill="both", expand=True)

        self.prompt_label = tk.Label(
            self.container,
            text="",
            bg=CYBER_BLACK,
            fg="#444400",
            font=("Consolas", 8, "italic"),
            anchor="w",
            justify="left"
        )
        self.prompt_label.pack(fill="x", pady=(0, 14))

        # 5 bars for more history, all hidden until logs arrive
        self.bars: list[ActivityBar] = []
        for _ in range(5):
            bar = ActivityBar(self.container, "")
            bar.pack(fill="x", pady=5)
            bar.pack_forget()
            self.bars.append(bar)

    def set_last_prompt(self, text: str):
        if text:
            # Handle long prompts with ellipsis
            display_text = (text[:45] + '...') if len(text) > 48 else text
            self.prompt_label.config(text=f"PREVIOUS PROMPT: {display_text}")
        else:
            self.prompt_label.config(text="")

    def add_log(self, text: str, level: str = "info"):
        # Shift logs up (keeping colors/levels)
        for i in range(len(self.bars) - 1):
            next_bar = self.bars[i + 1]
            next_text = next_bar.label.cget("text")
            next_color = next_bar.label.cget("fg")

            self.bars[i].label.config(text=next_text, fg=next_color)
            if next_text:
                self.bars[i].pack(fill="x", pady=5)

        # Add new log at the bottom
        self.bars[-1].update_text(text, level)
        self.bars[-1].pack(fill="x", pady=5)