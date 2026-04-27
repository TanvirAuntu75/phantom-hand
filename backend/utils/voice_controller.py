import speech_recognition as sr
from threading import Thread
import time
import logging
import asyncio

logger = logging.getLogger(__name__)

class VoiceController:
    def __init__(self, canvas, sio=None, event_loop=None):
        self.canvas = canvas
        self.sio = sio
        self.event_loop = event_loop
        self.active = False
        self.recognizer = sr.Recognizer()
        # Adjust for ambient noise on start
        self.microphone = None
        self._thread = None

    def toggle(self):
        self.active = not self.active
        if self.active:
            if self._thread is None or not self._thread.is_alive():
                self._thread = Thread(target=self._listen_loop, daemon=True)
                self._thread.start()
            logger.info("Voice Controller ACTIVATED")
        else:
            logger.info("Voice Controller DEACTIVATED")

    def _emit(self, event, data):
        if self.sio and self.event_loop:
            asyncio.run_coroutine_threadsafe(
                self.sio.emit(event, data),
                self.event_loop
            )

    def _execute_command(self, text):
        t = text.lower()
        cmd_matched = None

        if "clear" in t:
            if hasattr(self.canvas, "clear_all"): self.canvas.clear_all()
            cmd_matched = "CLEAR"
        elif "undo" in t:
            if hasattr(self.canvas, "undo"): self.canvas.undo()
            cmd_matched = "UNDO"
        elif "redo" in t:
            if hasattr(self.canvas, "redo"): self.canvas.redo()
            cmd_matched = "REDO"
        elif "red" in t:
            if hasattr(self.canvas, "set_color"): self.canvas.set_color((0, 0, 255))
            cmd_matched = "COLOR: RED"
        elif "blue" in t:
            if hasattr(self.canvas, "set_color"): self.canvas.set_color((255, 0, 0))
            cmd_matched = "COLOR: BLUE"
        elif "green" in t:
            if hasattr(self.canvas, "set_color"): self.canvas.set_color((0, 255, 0))
            cmd_matched = "COLOR: GREEN"
        elif "cyan" in t:
            if hasattr(self.canvas, "set_color"): self.canvas.set_color((255, 229, 0))
            cmd_matched = "COLOR: CYAN"
        elif "white" in t:
            if hasattr(self.canvas, "set_color"): self.canvas.set_color((255, 255, 255))
            cmd_matched = "COLOR: WHITE"
        elif "bigger" in t:
            if hasattr(self.canvas, "increase_size"): self.canvas.increase_size()
            cmd_matched = "SIZE UP"
        elif "smaller" in t:
            if hasattr(self.canvas, "decrease_size"): self.canvas.decrease_size()
            cmd_matched = "SIZE DOWN"
        elif "pencil" in t:
            self.canvas.mode = "PNC"
            cmd_matched = "MODE: PENCIL"
        elif "neon" in t:
            self.canvas.mode = "NEO"
            cmd_matched = "MODE: NEON"
        elif "laser" in t:
            self.canvas.mode = "LSR"
            cmd_matched = "MODE: LASER"
        elif "spray" in t:
            self.canvas.mode = "AIR"
            cmd_matched = "MODE: SPRAY"
        elif "mirror" in t:
            if hasattr(self.canvas, "toggle_mirror_h"): self.canvas.toggle_mirror_h()
            cmd_matched = "MIRROR"
        elif "save" in t:
            # To trigger export, we can't easily call the async route from here.
            # Instead, we'll set a flag or let the frontend know to trigger it.
            # Easiest way: emit a special event for frontend to call export API.
            self._emit("trigger_export", {"format": "png"})
            cmd_matched = "SAVE"
        elif "layer" in t:
            if hasattr(self.canvas, "next_layer"): self.canvas.next_layer()
            cmd_matched = "LAYER NEXT"

        if cmd_matched:
            self._emit("voice_command", {
                "command": cmd_matched,
                "raw_text": text,
                "timestamp": time.time()
            })
            logger.debug(f"Voice Command Executed: {cmd_matched} (Raw: {text})")

    def _listen_loop(self):
        try:
            self.microphone = sr.Microphone()
            with self.microphone as source:
                self.recognizer.adjust_for_ambient_noise(source)
        except Exception as e:
            logger.error(f"Could not initialize microphone: {e}")
            self.active = False
            return

        while self.active:
            try:
                with self.microphone as source:
                    audio = self.recognizer.listen(source, timeout=1.0, phrase_time_limit=3.0)

                text = self.recognizer.recognize_google(audio)
                self._execute_command(text)

            except sr.WaitTimeoutError:
                # Normal timeout, just loop again
                pass
            except sr.UnknownValueError:
                # Recognized speech but didn't understand words
                self._emit("voice_error", {"error": "Could not understand audio"})
            except Exception as e:
                logger.error(f"Voice recognition error: {e}")
                self._emit("voice_error", {"error": str(e)})
                time.sleep(1) # Prevent tight spin on hardware errors
