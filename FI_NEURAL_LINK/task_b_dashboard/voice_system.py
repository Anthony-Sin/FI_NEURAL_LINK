import speech_recognition as sr
import threading

class VoiceSystem:
    def __init__(self, log_callback=None, submit_callback=None):
        self.recognizer = sr.Recognizer()
        self.log_callback = log_callback
        self.submit_callback = submit_callback
        self._is_listening = False

    def start_listening(self):
        if self._is_listening:
            return

        self._is_listening = True
        threading.Thread(target=self._listen_loop, daemon=True).start()

    def _listen_loop(self):
        with sr.Microphone() as source:
            if self.log_callback:
                self.log_callback("VOICE SYSTEM: INITIALIZING CALIBRATION...", "info")
            self.recognizer.adjust_for_ambient_noise(source)

            if self.log_callback:
                self.log_callback("VOICE SYSTEM: LISTENING...", "success")

            try:
                audio = self.recognizer.listen(source, timeout=5, phrase_time_limit=10)
                if self.log_callback:
                    self.log_callback("VOICE SYSTEM: TRANSCRIBING...", "info")

                text = self.recognizer.recognize_google(audio)

                if self.log_callback:
                    self.log_callback(f"VOICE COMMAND: {text}", "success")

                if self.submit_callback:
                    self.submit_callback(text)

            except sr.WaitTimeoutError:
                if self.log_callback:
                    self.log_callback("VOICE SYSTEM: TIMEOUT", "warn")
            except sr.UnknownValueError:
                if self.log_callback:
                    self.log_callback("VOICE SYSTEM: UNABLE TO DECRYPT AUDIO", "error")
            except Exception as e:
                if self.log_callback:
                    self.log_callback(f"VOICE SYSTEM ERROR: {str(e)}", "error")
            finally:
                self._is_listening = False
