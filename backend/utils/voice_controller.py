import speech_recognition as sr
import threading
import time
import logging
import asyncio
from typing import Optional, Callable
from backend.config import settings

logger = logging.getLogger("phantom_hand")

class VoiceController:
    """
    PHANTOM HAND Voice Kernel.
    Enables hands-free control of the drawing canvas and system state.
    Uses Google Speech Recognition for high-accuracy command parsing.
    """
    def __init__(self, canvas, event_callback: Optional[Callable] = None):
        self.canvas = canvas
        self.event_callback = event_callback
        self.active = False
        self.recognizer = sr.Recognizer()
        self.microphone: Optional[sr.Microphone] = None
        self._thread: Optional[threading.Thread] = None
        self._stop_event = threading.Event()

        # Command Mapping for fuzzy matching
        self.commands = {
            "CLEAR": ["clear", "reset", "wipe", "delete everything"],
            "UNDO": ["undo", "go back", "reverse"],
            "REDO": ["redo", "forward"],
            "NEON": ["neon", "glow", "neon mode"],
            "LASER": ["laser", "beam", "laser mode"],
            "CHALK": ["chalk", "dust", "chalk mode"],
            "GHOST": ["ghost", "phantom", "fade"],
            "AIRBRUSH": ["spray", "airbrush", "mist"],
            "PENCIL": ["pencil", "basic", "standard"],
            "MIRROR": ["mirror", "reflection", "flip"],
            "SAVE": ["save", "export", "download"]
        }

    def toggle(self, state: Optional[bool] = None):
        """Activates or deactivates the voice kernel."""
        self.active = state if state is not None else not self.active
        
        if self.active:
            if self._thread is None or not self._thread.is_alive():
                self._stop_event.clear()
                self._thread = threading.Thread(target=self._listen_loop, daemon=True, name="Voice-Kernel")
                self._thread.start()
            logger.info("VOICE_KERNEL: SYSTEMS_ONLINE")
        else:
            self._stop_event.set()
            logger.info("VOICE_KERNEL: SYSTEMS_OFFLINE")

    def _execute(self, text: str):
        """Parses speech text and maps it to engine actions."""
        t = text.lower()
        matched_cmd = None
        
        # 1. Action Commands
        for cmd, synonyms in self.commands.items():
            if any(syn in t for syn in synonyms):
                matched_cmd = cmd
                break
        
        if matched_cmd:
            self._apply_command(matched_cmd)
        
        # 2. Color Commands (Fuzzy match from config)
        for color_name, hex_val in settings.COLOR_PALETTE.items():
            if color_name.lower() in t:
                self.canvas.set_color(hex_val)
                matched_cmd = f"COLOR_{color_name}"
        
        # 3. Layer Commands ("Layer 1", "Layer 2", etc.)
        if "layer" in t:
            for i in range(1, settings.MAX_LAYERS + 1):
                if str(i) in t:
                    self.canvas.switch_layer(i)
                    matched_cmd = f"LAYER_{i}"

        if matched_cmd and self.event_callback:
            self.event_callback("voice_command", {
                "command": matched_cmd,
                "text": text,
                "timestamp": time.time()
            })

    def _apply_command(self, cmd: str):
        """Directly interacts with the DrawingEngine."""
        if cmd == "CLEAR": self.canvas.clear()
        elif cmd == "UNDO": self.canvas.undo()
        elif cmd == "REDO": self.canvas.redo()
        elif cmd == "NEON": self.canvas.active_brush = "NEON"
        elif cmd == "LASER": self.canvas.active_brush = "LASER"
        elif cmd == "CHALK": self.canvas.active_brush = "CHALK"
        elif cmd == "GHOST": self.canvas.active_brush = "GHOST"
        elif cmd == "AIRBRUSH": self.canvas.active_brush = "AIRBRUSH"
        elif cmd == "PENCIL": self.canvas.active_brush = "BASIC"
        elif cmd == "MIRROR": self.canvas.toggle_mirror()

    def _listen_loop(self):
        """Background listener thread."""
        try:
            self.microphone = sr.Microphone()
            with self.microphone as source:
                self.recognizer.adjust_for_ambient_noise(source, duration=1.0)
        except Exception as e:
            logger.error(f"VOICE_KERNEL: MIC_INIT_FAILED [{e}]")
            return

        while not self._stop_event.is_set():
            try:
                with self.microphone as source:
                    # Short timeout to keep the loop responsive to stop_event
                    audio = self.recognizer.listen(source, timeout=1.0, phrase_time_limit=3.0)
                
                text = self.recognizer.recognize_google(audio)
                logger.info(f"VOICE_KERNEL: RECOGNIZED [{text}]")
                self._execute(text)
                
            except (sr.WaitTimeoutError, sr.UnknownValueError):
                continue
            except Exception as e:
                logger.error(f"VOICE_KERNEL: RECOG_ERROR [{e}]")
                time.sleep(1)
