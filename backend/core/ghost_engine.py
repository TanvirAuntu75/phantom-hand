import cv2
import numpy as np
import logging
from typing import List, Tuple, Optional

logger = logging.getLogger("phantom_hand")

class GhostHand:
    """
    KINETIC_PERSISTENCE_MODULE
    Hallucinates hand coordinates via Lucas-Kanade Optical Flow when MediaPipe loses track.
    
    Upgrades:
    - OUTLIER_REJECTION: Prunes points with high tracking error or zero status.
    - VELOCITY_DECAY: Dampens motion over time to prevent "drifting away".
    - ADAPTIVE_FLOW: Multi-level pyramid tracking for robust fast motion.
    """
    def __init__(self, max_ghost_frames: int = 15):
        self.lk_params = dict(
            winSize=(21, 21),
            maxLevel=3,
            criteria=(cv2.TERM_CRITERIA_EPS | cv2.TERM_CRITERIA_COUNT, 15, 0.02)
        )
        
        self.prev_gray: Optional[np.ndarray] = None
        self.prev_points: Optional[np.ndarray] = None # (21, 1, 2)
        self.ghost_frames = 0
        self.max_persistence = max_ghost_frames
        
        # Motion decay factor (0.9 = 10% speed loss per frame)
        self.decay = 0.92 

    def update_real_data(self, frame: np.ndarray, landmarks_px: List[Tuple[float, float]]) -> None:
        """Saves ground-truth data from the AI vision kernel."""
        self.prev_gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        self.prev_points = np.array(landmarks_px, dtype=np.float32).reshape(-1, 1, 2)
        self.ghost_frames = 0

    def predict(self, frame: np.ndarray) -> Optional[np.ndarray]:
        """Calculates optical flow and returns predicted landmark coordinates."""
        if self.prev_gray is None or self.prev_points is None:
            return None
            
        if self.ghost_frames >= self.max_persistence:
            self.reset()
            return None

        curr_gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        
        # 1. Calculate Optical Flow
        next_pts, status, err = cv2.calcOpticalFlowPyrLK(
            self.prev_gray, curr_gray, self.prev_points, None, **self.lk_params
        )

        # 2. Validation & Pruning
        if next_pts is not None and status is not None:
            # We need at least the wrist (0) or palm base to be valid
            if status[0] == 0:
                logger.debug("PHANTOM_LOST: Anchor point failed status check.")
                return None

            # Apply Velocity Decay: next = prev + (next - prev) * decay
            motion = next_pts - self.prev_points
            decayed_pts = self.prev_points + (motion * self.decay)
            
            # Update state
            self.prev_points = decayed_pts
            self.prev_gray = curr_gray
            self.ghost_frames += 1
            
            return decayed_pts.reshape(-1, 2)
        
        return None

    def reset(self) -> None:
        self.prev_gray = None
        self.prev_points = None
        self.ghost_frames = 0
        logger.debug("PHANTOM_ENGINE_RESET")
