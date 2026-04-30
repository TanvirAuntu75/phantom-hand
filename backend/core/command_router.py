import time
import logging
import numpy as np
from collections import deque
from typing import List, Tuple, Any, Dict, Callable, Optional

logger = logging.getLogger("phantom_hand")

class CommandRouter:
    """
    COMMAND_ROUTING_UNIT
    Bridges the GESTURE_CLASSIFICATION_KERNEL with the DRAWING_ENGINE.
    Handles temporal debouncing, multi-hand collision logic, and system event dispatch.
    """
    def __init__(self, 
                 canvas: Any, 
                 shape_recognizer: Any = None, 
                 event_callback: Optional[Callable[[str, Dict], None]] = None):
        self.canvas = canvas
        self.shape_recognizer = shape_recognizer
        self._dispatch = event_callback  # Unified callback for Socket.IO / UI updates

        # ── COOLDOWN_REGISTRY (Seconds) ────────────────────────────────────────
        self._cooldown_config: Dict[str, float] = {
            "PINCH_SNAP": 0.45,
            "FIST_UNDO": 0.5,
            "PEACE_REDO": 0.5,
            "OPEN_CLEAR": 1.5,
            "FOUR_BRUSH": 0.4,
            "HORNS_LAYER": 0.5,
            "L_SHAPE_MIRROR": 0.6,
            "PINKY_VOICE": 0.8,
            "THUMB_UP_CONFIRM": 1.0,
            "THUMB_DOWN_REJECT": 1.0,
            "SWIPE_LEFT": 0.4,
            "SWIPE_RIGHT": 0.4,
            "SWIPE_UP": 0.3,
            "SWIPE_DOWN": 0.3,
        }

        # Per-hand, per-gesture debounce state: (hand_id, gesture) -> last_fire_time
        self._debounce_registry: Dict[Tuple[str, str], float] = {}
        
        # Telemetry
        self._execution_history = deque(maxlen=10)

    def _should_fire(self, hand_id: str, gesture: str) -> bool:
        """
        TEMPORAL_GATEKEEPER
        Verifies if the gesture has exceeded its cooldown period for the specific hand.
        """
        cooldown = self._cooldown_config.get(gesture, 0.0)
        if cooldown <= 0:
            return True

        key = (hand_id, gesture)
        now = time.perf_counter()
        last_fired = self._debounce_registry.get(key, 0.0)

        if now - last_fired >= cooldown:
            self._debounce_registry[key] = now
            return True
        return False

    def route(self, hand_id: str, result: Any, landmarks: List[Tuple[float, float, float]]) -> None:
        """
        COMMAND_DISPATCH_PIPELINE
        Routes processed gesture signals to engine actions.
        """
        if not result or result.gesture == "HOVER":
            # Signal HOVER state to canvas for cursor updates
            if hasattr(self.canvas, "update"):
                tip = landmarks[8][:2] if len(landmarks) > 8 else (0.5, 0.5)
                self.canvas.update("HOVER", tip, hand_id)
            return

        gesture = result.gesture
        now = time.perf_counter()
        lms = landmarks

        # 1. CONTINUOUS ACTIONS (No Debounce)
        if gesture == "DRAW":
            tip = lms[8][:2]
            z_depth = lms[8][2]
            # Simple wrist-to-index-mcp angle for brush orientation
            angle = 0.0
            if len(lms) > 5:
                angle = float(np.arctan2(lms[5][1] - lms[0][1], lms[5][0] - lms[0][0]))
            
            self.canvas.update("DRAW", tip, hand_id, angle, z_depth)
            return

        if gesture == "TWO_ERASE":
            tip = lms[12][:2] # Use middle finger for eraser
            self.canvas.update("ERASE", tip, hand_id)
            return

        # 2. DISCRETE ACTIONS (Debounced)
        if not self._should_fire(hand_id, gesture):
            return

        logger.info(f"COMMAND_EXECUTED: {gesture} from {hand_id}")
        self._execution_history.append(f"{hand_id}:{gesture}")

        # --- Action Mapping ---
        if gesture == "FIST_UNDO":
            self.canvas.undo()
            self._emit("action_triggered", {"type": "UNDO", "hand": hand_id})

        elif gesture == "PEACE_REDO":
            self.canvas.redo()
            self._emit("action_triggered", {"type": "REDO", "hand": hand_id})

        elif gesture == "OPEN_CLEAR":
            self.canvas.clear()
            self._emit("action_triggered", {"type": "CLEAR", "hand": hand_id})

        elif gesture == "PINCH_SNAP":
            self._execute_shape_snap(hand_id)

        elif gesture == "FOUR_BRUSH":
            if hasattr(self.canvas, "next_brush"):
                self.canvas.next_brush()
            self._emit("config_changed", {"target": "BRUSH", "hand": hand_id})

        elif gesture == "HORNS_LAYER":
            if hasattr(self.canvas, "next_layer"):
                self.canvas.next_layer()
            self._emit("config_changed", {"target": "LAYER", "hand": hand_id})

        elif gesture == "L_SHAPE_MIRROR":
            if hasattr(self.canvas, "toggle_mirror"):
                self.canvas.toggle_mirror()
            self._emit("config_changed", {"target": "MIRROR", "hand": hand_id})

        elif gesture.startswith("SWIPE_"):
            self._handle_swipe(gesture, hand_id)

    def _handle_swipe(self, gesture: str, hand_id: str) -> None:
        """Routes motion-based swiping commands."""
        if gesture == "SWIPE_RIGHT":
            self.canvas.next_color()
        elif gesture == "SWIPE_LEFT":
            self.canvas.prev_color()
        elif gesture == "SWIPE_UP":
            self.canvas.increase_size()
        elif gesture == "SWIPE_DOWN":
            self.canvas.decrease_size()
        
        self._emit("navigation_event", {"direction": gesture, "hand": hand_id})

    def _execute_shape_snap(self, hand_id: str) -> None:
        """Logic for triggering the SHAPE_RECOGNITION engine."""
        if not self.shape_recognizer:
            return

        stroke = self.canvas.get_last_stroke(hand_id)
        if not stroke:
            return

        result = self.shape_recognizer.recognize(stroke)
        if result and result.confidence > 0.6:
            self.canvas.apply_shape(hand_id, result.fitted_points, result.shape_type)
            self._emit("shape_snapped", {
                "shape": result.shape_type,
                "confidence": result.confidence,
                "hand": hand_id
            })

    def _emit(self, event_name: str, payload: Dict) -> None:
        """Safely dispatches events to the external world."""
        if self._dispatch:
            try:
                self._dispatch(event_name, payload)
            except Exception as e:
                logger.error(f"EVENT_DISPATCH_ERROR: {e}")

    def get_history(self) -> List[str]:
        return list(self._execution_history)
