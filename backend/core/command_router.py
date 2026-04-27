import math
import time
import logging
from collections import deque
from typing import List, Tuple, Any

logger = logging.getLogger(__name__)

class CommandRouter:
    """
    Bridge between gesture recognition output and drawing engine actions.
    Maps gesture strings to corresponding drawing engine state modifications.
    """
    def __init__(self, canvas: Any, recognizer: Any):
        self.canvas = canvas
        self.recognizer = recognizer

        # Debounce dictionary mapping gesture to (last_time_fired, cooldown_seconds)
        self.debounce_state = {}

        # Configuration for debouncing timeouts
        self.cooldowns = {
            "UNDO": 0.4,
            "REDO": 0.4,
            "CLEAR": 1.5,
            "SNAP_SHAPE": 0.2,
            "SWIPE_RIGHT": 0.3,
            "SWIPE_LEFT": 0.3,
            "SWIPE_UP": 0.25,
            "SWIPE_DOWN": 0.25,
            "THREE_UP": 0.5,
            "HORNS": 0.5,
            "L_SHAPE": 0.6,
            "PINKY_ONLY": 0.6
        }

        # Log of recent actions
        self._gesture_log = deque(maxlen=8)

    @property
    def gesture_log(self) -> List[str]:
        return list(self._gesture_log)

    def _debounce(self, gesture: str, now: float) -> bool:
        """
        Returns True if the action is allowed to fire (cooldown has passed).
        Returns False if the action should be blocked.
        """
        if gesture not in self.cooldowns:
            return True # No cooldown configured = always allow

        last_fired = self.debounce_state.get(gesture, 0.0)
        cooldown = self.cooldowns[gesture]

        if now - last_fired >= cooldown:
            self.debounce_state[gesture] = now
            return True
        return False

    def route(self, label: str, result: Any, lms: List[Tuple[float, float, float]]) -> None:
        """
        Routes the gesture to the canvas action.
        label: Hand ID (e.g. "Left", "Right", "Hand_...")
        result: GestureResult object with a .gesture string attribute
        lms: List of 21 3D landmarks (x, y, z)
        """
        if result is None or not hasattr(result, "gesture"):
            return

        gesture = result.gesture
        now = time.time()
        action_fired = False

        if gesture == "DRAW":
            # lms[0] is wrist, lms[9] is middle knuckle
            wrist = lms[0]
            knuckle = lms[9]
            # Calculate angle in radians (y differences reversed because screen Y is top-down)
            dx = knuckle[0] - wrist[0]
            dy = knuckle[1] - wrist[1]
            wrist_angle = math.atan2(dy, dx)

            z_depth = lms[8][2]
            index_tip_xy = (lms[8][0], lms[8][1])

            if hasattr(self.canvas, "update"):
                self.canvas.update("DRAW", index_tip_xy, label, wrist_angle, z_depth)

        elif gesture == "ERASE":
            middle_tip_xy = (lms[12][0], lms[12][1])
            if hasattr(self.canvas, "update"):
                self.canvas.update("ERASE", middle_tip_xy, label)

        elif gesture in ["STOP", "HOVER"]:
            if hasattr(self.canvas, "update"):
                self.canvas.update("HOVER", None, label)

        elif gesture == "UNDO" and self._debounce("UNDO", now):
            if hasattr(self.canvas, "undo"):
                self.canvas.undo()
            action_fired = True

        elif gesture == "REDO" and self._debounce("REDO", now):
            if hasattr(self.canvas, "redo"):
                self.canvas.redo()
            action_fired = True

        elif gesture == "CLEAR" and self._debounce("CLEAR", now):
            if hasattr(self.canvas, "clear_all"):
                self.canvas.clear_all()
            elif hasattr(self.canvas, "clear"): # Fallback for local stub
                self.canvas.clear()
            action_fired = True

        elif gesture == "SNAP_SHAPE" and self._debounce("SNAP_SHAPE", now):
            if hasattr(self.canvas, "get_last_stroke_points") and hasattr(self.canvas, "snap_shape"):
                # Handle possible hand_id argument
                try:
                    stroke = self.canvas.get_last_stroke_points(label)
                except TypeError:
                    stroke = self.canvas.get_last_stroke_points()

                if stroke and self.recognizer:
                    recognize_func = getattr(self.recognizer, "recognize", getattr(self.recognizer, "recognize_and_snap", None))
                    if recognize_func:
                        result = recognize_func(stroke)
                        if result:
                            # Handle both object and dict returns
                            shape_name = getattr(result, "shape", result.get("shape", "")) if isinstance(result, dict) else result.shape
                            fitted_points = getattr(result, "fitted_points", result.get("fitted_points", [])) if isinstance(result, dict) else result.fitted_points
                            confidence = getattr(result, "confidence", result.get("confidence", 0.0)) if isinstance(result, dict) else result.confidence

                            if shape_name and shape_name != "FREEFORM":
                                # Handle snap_shape arguments
                                try:
                                    self.canvas.snap_shape(label, fitted_points, shape_name)
                                except TypeError:
                                    try:
                                        self.canvas.snap_shape(fitted_points, shape_name)
                                    except TypeError:
                                        self.canvas.snap_shape(result)

                                # Emit socket event if we can
                                import asyncio
                                try:
                                    # Very hacky way to reach sio from here, but avoids circular imports
                                    # The prompt said to emit "shape_snapped", we'll try to get it from sys.modules
                                    import sys
                                    if "backend.app" in sys.modules:
                                        app_mod = sys.modules["backend.app"]
                                        if hasattr(app_mod, "sio") and hasattr(app_mod, "main_loop"):
                                            asyncio.run_coroutine_threadsafe(
                                                app_mod.sio.emit("shape_snapped", {
                                                    "shape": shape_name,
                                                    "confidence": confidence,
                                                    "fitted_points": fitted_points,
                                                    "hand_id": label
                                                }),
                                                app_mod.main_loop
                                            )
                                except Exception as e:
                                    logger.error(f"Failed to emit shape_snapped: {e}")

                                action_fired = True

        elif gesture == "SWIPE_RIGHT" and self._debounce("SWIPE_RIGHT", now):
            if hasattr(self.canvas, "next_color"):
                self.canvas.next_color()
            action_fired = True

        elif gesture == "SWIPE_LEFT" and self._debounce("SWIPE_LEFT", now):
            if hasattr(self.canvas, "prev_color"):
                self.canvas.prev_color()
            action_fired = True

        elif gesture == "SWIPE_UP" and self._debounce("SWIPE_UP", now):
            if hasattr(self.canvas, "increase_size"):
                self.canvas.increase_size()
            action_fired = True

        elif gesture == "SWIPE_DOWN" and self._debounce("SWIPE_DOWN", now):
            if hasattr(self.canvas, "decrease_size"):
                self.canvas.decrease_size()
            action_fired = True

        elif gesture == "THREE_UP" and self._debounce("THREE_UP", now):
            if hasattr(self.canvas, "toggle_3d"):
                self.canvas.toggle_3d()
            action_fired = True

        elif gesture == "HORNS" and self._debounce("HORNS", now):
            if hasattr(self.canvas, "next_layer"):
                self.canvas.next_layer()
            action_fired = True

        elif gesture == "L_SHAPE" and self._debounce("L_SHAPE", now):
            if hasattr(self.canvas, "toggle_mirror_h"):
                self.canvas.toggle_mirror_h()
            action_fired = True

        elif gesture == "PINKY_ONLY" and self._debounce("PINKY_ONLY", now):
            if hasattr(self.canvas, "toggle_mirror_v"):
                self.canvas.toggle_mirror_v()
            action_fired = True

        if action_fired:
            self._gesture_log.append(f"{time.strftime('%H:%M:%S')} - {gesture}")
            logger.debug(f"Action fired: {gesture} for hand {label}")
