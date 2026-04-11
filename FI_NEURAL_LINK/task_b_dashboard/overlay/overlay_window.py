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

        # DPI awareness for Windows
        if platform.system() == "Windows":
            try:
                from ctypes import windll
                windll.shcore.SetProcessDpiAwareness(1)
            except Exception:
                pass

        # Initial size
        self.width = 420
        self.height = 750

        # Position dynamically
        self.reposition()

        # Draggable functionality state
        self._x = 0
        self._y = 0

        # Bind events to the window itself
        self.bind("<Button-1>", self._start_move)
        self.bind("<B1-Motion>", self._do_move)

    def reposition(self):
        """Position the window in the bottom-right, above the taskbar."""
        self.update_idletasks()

        # Get screen dimensions
        screen_width = self.winfo_screenwidth()
        screen_height = self.winfo_screenheight()

        # Attempt to get work area (excluding taskbar)
        # This is platform specific, but we'll use a safe offset as fallback
        offset_x = 20
        offset_y = 60 # Safe bet for most taskbars

        # For Windows, we can use _wm_get_workarea if available or just stick to safe offsets
        x = screen_width - self.width - offset_x
        y = screen_height - self.height - offset_y

        self.geometry(f"{self.width}x{self.height}+{int(x)}+{int(y)}")

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

    def minimize(self):
        """True OS minimize to taskbar."""
        # For overrideredirect windows, we need to temporarily disable it
        # to allow the OS to manage the minimize state, then re-enable on restore.
        # Alternatively, we can use state('iconic') which works on some WMs even with overrideredirect.
        self.update_idletasks()
        self.overrideredirect(False)
        self.state('iconic')

        # We need a way to detect restore to set overrideredirect(True) again
        self.bind("<Map>", self._on_restore)

    def _on_restore(self, event):
        if self.state() == 'normal':
            self.overrideredirect(True)
            self.unbind("<Map>")
            # Position might need reset after OS management
            self.reposition()
