import tkinter as tk
from FI_NEURAL_LINK.ui.main_window import Dashboard
import time
from PIL import ImageGrab
import os

def capture_ui():
    d = Dashboard()
    d.log("SYSTEM REBOOT COMPLETE")
    d.middle.set_last_prompt("OPEN GOOGLE CHROME")

    # Give it a moment to render
    d.root.update()
    time.sleep(1)

    # Save screenshot
    os.makedirs("verification", exist_ok=True)
    # Using a larger box to capture the sidebar
    ImageGrab.grab(bbox=(0, 0, 1024, 768)).save("verification/sidebar_redesign_v2.png")
    print("Screenshot saved to verification/sidebar_redesign_v2.png")
    d.root.destroy()

if __name__ == "__main__":
    capture_ui()
