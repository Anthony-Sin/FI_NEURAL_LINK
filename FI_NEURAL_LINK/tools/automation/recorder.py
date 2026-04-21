import time
import threading
from pynput import mouse, keyboard
from FI_NEURAL_LINK.ui.panels.stop_panel import STOP_EVENT

class ActionRecorder:
    def __init__(self):
        self.events = []
        self.is_recording = False
        self.start_time = None
        self.mouse_listener = None
        self.keyboard_listener = None

    def _on_click(self, x, y, button, pressed):
        if pressed:
            elapsed = time.time() - self.start_time
            self.events.append({
                "type": "click",
                "time": elapsed,
                "x": x,
                "y": y,
                "button": str(button)
            })

    def _on_press(self, key):
        elapsed = time.time() - self.start_time
        try:
            k = key.char  # alphanumeric key
        except AttributeError:
            k = str(key)  # special key

        self.events.append({
            "type": "keypress",
            "time": elapsed,
            "key": k
        })

    def start(self):
        if self.is_recording:
            return {"ok": False, "result": "Already recording"}

        self.events = []
        self.is_recording = True
        self.start_time = time.time()

        self.mouse_listener = mouse.Listener(on_click=self._on_click)
        self.keyboard_listener = keyboard.Listener(on_press=self._on_press)

        self.mouse_listener.start()
        self.keyboard_listener.start()

        return {"ok": True, "result": "Started recording user actions"}

    def stop(self):
        if not self.is_recording:
            return {"ok": False, "result": "Not recording"}

        self.is_recording = False
        if self.mouse_listener:
            self.mouse_listener.stop()
        if self.keyboard_listener:
            self.keyboard_listener.stop()

        return {
            "ok": True,
            "result": f"Stopped recording. Captured {len(self.events)} events.",
            "events": self.events
        }

recorder_instance = ActionRecorder()

def start_recording():
    return recorder_instance.start()

def stop_recording():
    return recorder_instance.stop()
