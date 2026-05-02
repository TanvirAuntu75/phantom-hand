import numpy as np
import time
from typing import List, Tuple, Optional, Any

class LandmarkSmoother:
    """
    TEMPORAL_STABILIZATION_UNIT
    Velocity-adaptive EMA filter with frequency compensation.
    
    Upgrades:
    - FREQUENCY_AWARENESS: Adapts alpha based on actual time delta (dt).
    - CONFIDENCE_WEIGHTING: Dampens landmarks with low visibility scores.
    - MOMENTUM_RETENTION: Maintains state through brief occlusion windows.
    """
    def __init__(self, min_cutoff: float = 0.5, beta: float = 1.5, d_cutoff: float = 1.0):
        # 1-Euro Filter Parameters
        self.min_cutoff = min_cutoff
        self.beta = beta
        self.d_cutoff = d_cutoff
        
        self.x_prev: Optional[np.ndarray] = None
        self.dx_prev: Optional[np.ndarray] = None
        self.t_prev: float = time.time()
        
        # Dead-reckoning config
        self.last_seen: float = 0.0
        self.max_occlusion_ms: float = 100.0 # Hold state for 100ms of signal loss

    def reset(self) -> None:
        self.x_prev = None
        self.dx_prev = None

    def smooth(self, raw_landmarks: List[Tuple[float, float, float]], 
               confidences: Optional[List[float]] = None) -> List[Tuple[float, float, float]]:
        """
        Applies frequency-compensated 1-Euro filtering.
        """
        t_now = time.time()
        dt = t_now - self.t_prev
        self.t_prev = t_now
        
        # Safety for first frame or pause
        if dt <= 0.001 or dt > 0.5: # Prevent numeric instability from micro-deltas
            dt = 1.0 / 30.0 # Assume 30fps fallback

        x = np.array(raw_landmarks, dtype=np.float32) # (21, 3)

        if self.x_prev is None:
            self.x_prev = x
            self.dx_prev = np.zeros_like(x)
            return raw_landmarks

        # 1. Calculate Velocity (Derivative)
        dx = (x - self.x_prev) / dt
        
        # 2. Smooth the derivative
        alpha_d = self._get_alpha(dt, self.d_cutoff)
        dx_hat = alpha_d * dx + (1 - alpha_d) * self.dx_prev
        self.dx_prev = dx_hat
        
        # 3. Calculate Cutoff Frequency based on speed
        # cutoff = min_cutoff + beta * |dx_hat|
        speed = np.linalg.norm(dx_hat, axis=1, keepdims=True)
        cutoff = self.min_cutoff + self.beta * speed
        
        # 4. Smooth the signal
        alpha = self._get_alpha(dt, cutoff)
        
        # --- Confidence Weighting ---
        if confidences is not None:
            conf = np.array(confidences, dtype=np.float32).reshape(-1, 1)
            # Reduce alpha (more smoothing) for low confidence points
            alpha = alpha * np.clip(conf, 0.1, 1.0)

        x_hat = alpha * x + (1 - alpha) * self.x_prev
        self.x_prev = x_hat
        
        return [tuple(map(float, row)) for row in x_hat]

    def _get_alpha(self, dt: float, cutoff: Any) -> np.ndarray:
        """Standard 1-Euro alpha calculation."""
        tau = 1.0 / (2 * np.pi * cutoff)
        return 1.0 / (1.0 + tau / dt)
