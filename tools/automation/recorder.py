import time
import threading
from pynput import mouse, keyboard
from pywinauto import Desktop
from ui.panels.stop_panel import STOP_EVENT

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

            element_info = None
            try:
                # Attempt to identify element under cursor
                element = Desktop(backend="uia").from_point(x, y)
                if element:
                    element_info = {
                        "name": element.window_text(),
                        "auto_id": element.element_info.automation_id,
                        "control_type": element.element_info.control_type,
                        "window_title": element.top_level_parent().window_text()
                    }
            except:
                pass

            self.events.append({
                "type": "click",
                "time": elapsed,
                "x": x,
                "y": y,
                "button": str(button),
                "element": element_info
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

    def get_recorded_domain(self):
        """Returns the domain or window title of the first recorded web action."""
        for e in self.events:
            if e["type"] == "click" and e.get("element"):
                return e["element"].get("window_title")
        return None

    def get_event_summary(self):
        """Returns a natural language summary of events for the LLM."""
        if not self.events: return "No events recorded."

        summary = []
        for e in self.events:
            if e["type"] == "click":
                el = e.get("element")
                msg = f"Clicked at ({e['x']}, {e['y']})"
                if el:
                    msg += f" (Target: {el['control_type']} '{el['name']}' in {el['window_title']})"
                summary.append(msg)
            elif e["type"] == "keypress":
                summary.append(f"Pressed key: {e['key']}")
        return "\n".join(summary)

    def clear(self):
        self.events = []
        return {"ok": True, "result": "Recording cleared"}

    def get_as_function_calls(self):
        """Converts raw events into a list of ToolRouter-compatible function calls."""
        calls = []
        last_time = 0

        # We group keypresses into 'type_text' for efficiency if they are close in time
        typing_buffer = []

        for event in self.events:
            wait_time = event["time"] - last_time
            if wait_time > 0.1:
                # Flush typing buffer
                if typing_buffer:
                    calls.append({"name": "type_text", "args": {"text": "".join(typing_buffer)}})
                    typing_buffer = []

                # Add wait if significant
                if wait_time > 0.5:
                    calls.append({"name": "wait", "args": {"seconds": round(wait_time, 1)}})

            if event["type"] == "click":
                # Per user instruction: use exact screen coordinates for all clicks
                # This ensures input focus is correctly placed where the human actually clicked.
                calls.append({"name": "click", "args": {"x": event["x"], "y": event["y"]}})
            elif event["type"] == "keypress":
                key = event["key"]
                if len(key) == 1:
                    typing_buffer.append(key)
                else:
                    # Special key like Key.enter
                    if typing_buffer:
                        calls.append({"name": "type_text", "args": {"text": "".join(typing_buffer)}})
                        typing_buffer = []

                    # Convert pynput key name to pyautogui key name
                    clean_key = key.replace("Key.", "")
                    calls.append({"name": "press_key", "args": {"key": clean_key}})

            last_time = event["time"]

        if typing_buffer:
            calls.append({"name": "type_text", "args": {"text": "".join(typing_buffer)}})

        return calls

recorder_instance = ActionRecorder()

def start_recording():
    return recorder_instance.start()

def stop_recording():
    return recorder_instance.stop()

def get_recorded_calls():
    return recorder_instance.get_as_function_calls()

def get_recorded_summary():
    return recorder_instance.get_event_summary()

def get_recorded_domain():
    return recorder_instance.get_recorded_domain()

def clear_recording():
    return recorder_instance.clear()
