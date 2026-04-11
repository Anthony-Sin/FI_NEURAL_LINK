import tkinter as tk

class OverlayWindow:
    def __init__(self):
        self.root = tk.Tk()

        # Configure window attributes
        self.root.attributes('-topmost', True)
        self.root.attributes('-alpha', 0.92)
        self.root.overrideredirect(True)
        self.root.configure(bg='#0d0d0f')

        # Set dimensions
        self.width = 420
        self.height = 560

        # Calculate position for bottom-right corner
        screen_width = self.root.winfo_screenwidth()
        screen_height = self.root.winfo_screenheight()
        x = screen_width - self.width
        y = screen_height - self.height

        self.root.geometry(f"{self.width}x{self.height}+{x}+{y}")

        # Initialize drag offsets
        self._offsetx = 0
        self._offsety = 0

        # Bind mouse events for dragging
        self.root.bind("<Button-1>", self._start_move)
        self.root.bind("<B1-Motion>", self._do_move)

        # Add close button (X) in the top-right corner
        self.close_button = tk.Button(
            self.root,
            text="✕",
            command=self.hide,
            bg='#0d0d0f',
            fg='#ffffff',
            bd=0,
            highlightthickness=0,
            activebackground='#1a1a1c',
            activeforeground='#ff4444',
            font=("Arial", 12)
        )
        self.close_button.place(x=self.width - 35, y=5, width=30, height=30)

    def _start_move(self, event):
        """Record the initial mouse position for dragging."""
        self._offsetx = event.x
        self._offsety = event.y

    def _do_move(self, event):
        """Update window position based on mouse movement."""
        x = self.root.winfo_x() + event.x - self._offsetx
        y = self.root.winfo_y() + event.y - self._offsety
        self.root.geometry(f"+{x}+{y}")

    def show(self):
        """Display the window."""
        self.root.deiconify()

    def hide(self):
        """Hide the window."""
        self.root.withdraw()

    def run(self):
        """Start the tkinter main loop."""
        self.root.mainloop()

if __name__ == "__main__":
    # Example usage
    app = OverlayWindow()
    app.run()
