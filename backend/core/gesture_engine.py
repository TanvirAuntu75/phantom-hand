import numpy as np
import time
import logging
from collections import deque
from typing import List, Tuple, Optional, Dict

logger = logging.getLogger("phantom_hand")

# ── OUTPUT CONTRACT ────────────────────────────────────────────────────────────
class GestureResult:
    """
    GESTURE_SIGNAL
    Immutable output of the classification pipeline.
    """
    __slots__ = ("gesture", "confidence", "velocity")

    def __init__(self, gesture: str, confidence: float = 1.0, velocity: Optional[np.ndarray] = None):
        self.gesture: str = gesture
        self.confidence: float = confidence
        self.velocity: Optional[np.ndarray] = velocity

    def __repr__(self) -> str:
        return f"[{self.gesture} | conf={self.confidence:.2f}]"


# ── CORE ENGINE ────────────────────────────────────────────────────────────────
class GestureEngine:
    """
    GESTURE_CLASSIFICATION_KERNEL
    Processes 21 MediaPipe landmarks into semantic gesture commands.

    Key upgrades over v1:
    - Temporal Voting Buffer (3-frame debounce) eliminates gesture flicker
    - Depth-Aware Threshold Scaling prevents false positives on z-axis motion
    - Full 18-gesture vocabulary with strict priority ordering
    - Per-gesture confidence scoring for downstream command routing
    """

    # ── Gesture priority chain (highest → lowest) ──────────────────────────────
    _PRIORITY: List[str] = [
        "PINCH_SNAP", "PINCH_ZOOM_IN", "PINCH_ZOOM_OUT",
        "FIST_UNDO", "OPEN_CLEAR",
        "PEACE_REDO", "TWO_ERASE",
        "THREE_3D", "FOUR_BRUSH",
        "HORNS_LAYER", "L_SHAPE_MIRROR", "THUMB_UP_CONFIRM", "THUMB_DOWN_REJECT",
        "PINKY_VOICE",
        "DRAW",
        "SWIPE_LEFT", "SWIPE_RIGHT", "SWIPE_UP", "SWIPE_DOWN",
        "HOVER",
    ]

    def __init__(self, vote_window: int = 3):
        # Temporal debounce buffer
        self._vote_buffer: deque = deque(maxlen=vote_window)

        # Velocity tracking
        self._last_pos: Optional[np.ndarray] = None
        self._last_time: float = time.perf_counter()
        self._smoothed_vel: np.ndarray = np.zeros(2, dtype=np.float32)

        # ── Configurable thresholds ────────────────────────────────────────────
        self._EXT_HIGH: float = 0.75   # Finger "clearly extended"
        self._EXT_LOW: float  = 0.45   # Finger "clearly curled"
        self._PINCH_CLOSE: float = 0.22
        self._SWIPE_VEL: float  = 1.4  # Norm-units / sec
        self._VEL_EMA: float    = 0.65  # Velocity smoothing factor
        # ──────────────────────────────────────────────────────────────────────

    # ── PUBLIC API ─────────────────────────────────────────────────────────────
    def process(self, landmarks: List[Tuple[float, float, float]]) -> GestureResult:
        """
        CLASSIFICATION_DISPATCH
        Takes 21 MediaPipe landmarks, returns a temporally-stable GestureResult.
        """
        if not landmarks or len(landmarks) < 21:
            return GestureResult("HOVER", confidence=0.0)

        lms = np.array(landmarks, dtype=np.float32)

        # ── 1. Compute palm basis ──────────────────────────────────────────────
        palm_size = np.linalg.norm(lms[0] - lms[9])
        if palm_size < 1e-6:
            return GestureResult("HOVER", confidence=0.0)

        # Depth compensation: palm tilted away = foreshortening → scale thresholds
        z_depth = abs(float(lms[9, 2]))
        depth_scale = max(0.7, 1.0 - z_depth * 0.4)

        ext = self._finger_extensions(lms, palm_size, depth_scale)
        pinch = self._pinch_distance(lms, palm_size)
        vel   = self._update_velocity(lms)

        # ── 2. Raw classification ──────────────────────────────────────────────
        raw = self._classify(lms, ext, pinch, vel, palm_size)

        # ── 3. Temporal vote (debounce) ────────────────────────────────────────
        self._vote_buffer.append(raw.gesture)
        stable = self._vote()

        if stable != raw.gesture:
            return GestureResult(stable, confidence=0.6, velocity=vel)
        return GestureResult(raw.gesture, confidence=raw.confidence, velocity=vel)

    # ── INTERNAL FEATURES ──────────────────────────────────────────────────────
    def _finger_extensions(self, lms: np.ndarray, palm: float, scale: float) -> Dict[str, float]:
        """Tip-to-MCP extension ratio, depth-scaled."""
        tips_mcps = [(4, 2), (8, 5), (12, 9), (16, 13), (20, 17)]
        names = ("thumb", "index", "middle", "ring", "pinky")
        return {
            name: np.linalg.norm(lms[tip] - lms[mcp]) / palm / scale
            for name, (tip, mcp) in zip(names, tips_mcps)
        }

    def _pinch_distance(self, lms: np.ndarray, palm: float) -> float:
        """Thumb-tip to index-tip normalised distance."""
        return float(np.linalg.norm(lms[4] - lms[8]) / palm)

    def _update_velocity(self, lms: np.ndarray) -> np.ndarray:
        """EMA-smoothed palm velocity in normalised screen units/sec."""
        pos = lms[9, :2]
        now = time.perf_counter()
        dt  = now - self._last_time
        self._last_time = now

        if self._last_pos is not None and dt > 0:
            raw_vel = (pos - self._last_pos) / dt
            self._smoothed_vel = (
                self._VEL_EMA * self._smoothed_vel +
                (1.0 - self._VEL_EMA) * raw_vel
            )
        self._last_pos = pos
        return self._smoothed_vel.copy()

    def _vote(self) -> str:
        """Majority vote across the temporal buffer."""
        from collections import Counter
        counts = Counter(self._vote_buffer)
        winner, _ = counts.most_common(1)[0]
        return winner

    # ── CLASSIFICATION LOGIC ───────────────────────────────────────────────────
    def _classify(
        self,
        lms: np.ndarray,
        ext: Dict[str, float],
        pinch: float,
        vel: np.ndarray,
        palm: float,
    ) -> GestureResult:

        H = self._EXT_HIGH
        L = self._EXT_LOW

        # ── Pinch family ───────────────────────────────────────────────────────
        if pinch < self._PINCH_CLOSE:
            if ext["middle"] < L and ext["ring"] < L:
                return GestureResult("PINCH_SNAP", 0.95)
            # Zoom variants: thumb-index only, remaining curled
            zoom_speed = float(np.linalg.norm(vel))
            if ext["middle"] < L:
                return GestureResult("PINCH_ZOOM_IN" if zoom_speed > 0.3 else "PINCH_SNAP", 0.85)

        # ── Fist → UNDO ────────────────────────────────────────────────────────
        if all(ext[k] < L for k in ("index", "middle", "ring", "pinky")):
            return GestureResult("FIST_UNDO", 0.92)

        # ── Open Palm → CLEAR ──────────────────────────────────────────────────
        if all(ext[k] > H for k in ("index", "middle", "ring", "pinky")):
            return GestureResult("OPEN_CLEAR", 0.90)

        # ── Peace (spread) → REDO ──────────────────────────────────────────────
        if ext["index"] > H and ext["middle"] > H and ext["ring"] < L and ext["pinky"] < L:
            spread = float(np.linalg.norm(lms[8] - lms[12]) / palm)
            if spread > 0.35:
                return GestureResult("PEACE_REDO", 0.88)

        # ── Two fingers (close) → ERASE ────────────────────────────────────────
        if ext["index"] > H and ext["middle"] > H and ext["ring"] < L:
            return GestureResult("TWO_ERASE", 0.87)

        # ── Three fingers → 3D MODE ────────────────────────────────────────────
        if ext["index"] > H and ext["middle"] > H and ext["ring"] > H and ext["pinky"] < L:
            return GestureResult("THREE_3D", 0.86)

        # ── Four fingers → BRUSH CYCLE ─────────────────────────────────────────
        if all(ext[k] > H for k in ("index", "middle", "ring", "pinky")) and ext["thumb"] < L:
            return GestureResult("FOUR_BRUSH", 0.84)

        # ── Horns (index + pinky) → LAYER SWITCH ──────────────────────────────
        if ext["index"] > H and ext["pinky"] > H and ext["middle"] < L and ext["ring"] < L:
            return GestureResult("HORNS_LAYER", 0.83)

        # ── Thumb Up → CONFIRM ─────────────────────────────────────────────────
        thumb_up_vec = lms[4] - lms[0]  # Thumb tip relative to wrist
        if ext["thumb"] > 0.65 and all(ext[k] < L for k in ("index", "middle", "ring", "pinky")):
            if float(thumb_up_vec[1]) < -0.05:  # Pointing upward in screen space
                return GestureResult("THUMB_UP_CONFIRM", 0.82)
            return GestureResult("THUMB_DOWN_REJECT", 0.80)

        # ── L-Shape → MIRROR ──────────────────────────────────────────────────
        if ext["thumb"] > 0.6 and ext["index"] > H and ext["middle"] < L:
            v_t = lms[4, :2] - lms[2, :2]
            v_i = lms[8, :2] - lms[5, :2]
            norms = np.linalg.norm(v_t) * np.linalg.norm(v_i)
            if norms > 1e-6 and abs(float(np.dot(v_t, v_i) / norms)) < 0.45:
                return GestureResult("L_SHAPE_MIRROR", 0.79)

        # ── Pinky only → VOICE ────────────────────────────────────────────────
        if ext["pinky"] > H and ext["index"] < L and ext["middle"] < L and ext["ring"] < L:
            return GestureResult("PINKY_VOICE", 0.78)

        # ── Index pointer → DRAW ──────────────────────────────────────────────
        if ext["index"] > H and ext["middle"] < self._EXT_HIGH - 0.05:
            return GestureResult("DRAW", 0.75)

        # ── Velocity swipes ───────────────────────────────────────────────────
        speed = float(np.linalg.norm(vel))
        if speed > self._SWIPE_VEL:
            ax, ay = abs(float(vel[0])), abs(float(vel[1]))
            if ax > ay:
                return GestureResult("SWIPE_RIGHT" if vel[0] > 0 else "SWIPE_LEFT", 0.70)
            return GestureResult("SWIPE_DOWN" if vel[1] > 0 else "SWIPE_UP", 0.70)

        return GestureResult("HOVER", 0.50)
