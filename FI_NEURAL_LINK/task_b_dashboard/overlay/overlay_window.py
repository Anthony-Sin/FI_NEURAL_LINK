import tkinter as tk

class OverlayWindow(tk.Tk):
    def __init__(self):
        super().__init__()

        # Window attributes
        self.attributes("-topmost", True)
        self.attributes("-alpha", 0.92)
        self.overrideredirect(True)
        self.configure(bg="#0d0d0f")

        # Size and position
        self.width = 420
        self.height = 560

        # Get screen dimensions
        screen_width = self.winfo_screenwidth()
        screen_height = self.winfo_screenheight()

        # Calculate position for bottom-right corner
        x = screen_width - self.width
        y = screen_height - self.height
        self.geometry(f"{self.width}x{self.height}+{x}+{y}")

        # Draggable functionality state
        self._x = 0
        self._y = 0

        # Bind events to the window itself
        self.bind("<Button-1>", self._start_move)
        self.bind("<B1-Motion>", self._do_move)

    def bind_drag_to_all(self, widget):
        """Recursively bind drag events to a widget and all its children."""
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
