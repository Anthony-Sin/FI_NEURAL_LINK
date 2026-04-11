import tkinter as tk
import platform

class OverlayWindow(tk.Tk):
    def __init__(self):
        super().__init__()

        # Window attributes
        self.attributes("-topmost", True)
        self.attributes("-alpha", 0.95)
        self.overrideredirect(True)
        self.configure(bg="#000000")

        if platform.system() == "Windows":
            try:
                from ctypes import windll
                windll.shcore.SetProcessDpiAwareness(1)
            except Exception:
                pass

        # Width matching w-72 (approx 288px)
        self.width = 288
        self.height = 750

        self.reposition()

        self._x = 0
        self._y = 0
        self.bind("<Button-1>", self._start_move)
        self.bind("<B1-Motion>", self._do_move)

    def reposition(self):
        self.update_idletasks()
        screen_width = self.winfo_screenwidth()
        screen_height = self.winfo_screenheight()

        # Fixed to right edge, with left yellow border (handled by frame in dashboard)
        x = screen_width - self.width
        y = screen_height - self.height - 60
        self.geometry(f"{self.width}x{self.height}+{int(x)}+{int(y)}")

    def bind_drag_to_all(self, widget):
        widget.bind("<Button-1>", self._start_move, add="+")
        widget.bind("<B1-Motion>", self._do_move, add="+")
        for child in widget.winfo_children():
            self.bind_drag_to_all(child)

    def _start_move(self, event):
        self._x = event.x
        self._y = event.y

    def _do_move(self, event):
        x = self.winfo_x() + (event.x - self._x)
        y = self.winfo_y() + (event.y - self._y)
        self.geometry(f"+{x}+{y}")

    def show(self):
        self.deiconify()

    def hide(self):
        self.withdraw()

    def minimize(self):
        self.update_idletasks()
        self.overrideredirect(False)
        self.state('iconic')
        self.bind("<Map>", self._on_restore)

    def _on_restore(self, event):
        if self.state() == 'normal':
            self.overrideredirect(True)
            self.unbind("<Map>")
            self.reposition()
