import cv2
import numpy as np

class GhostHand:
    """
    Uses Lucas-Kanade Optical Flow to 'hallucinate' hand positions
    when the AI is blinking or confused.
    """
    def __init__(self, max_ghost_frames=15):
        self.lk_params = dict(winSize=(31, 31),
                             maxLevel=3,
                             criteria=(cv2.TERM_CRITERIA_EPS | cv2.TERM_CRITERIA_COUNT, 10, 0.03))
        
        self.last_frame_gray = None
        self.last_points = None
        self.ghost_count = 0
        self.max_ghost_frames = max_ghost_frames

    def update_real_data(self, frame, landmarks_px):
        """ Feed the engine fresh ground-truth from the AI. """
        self.last_frame_gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        self.last_points = np.array(landmarks_px, dtype=np.float32).reshape(-1, 1, 2)
        self.ghost_count = 0

    def predict(self, frame):
        """ Track the last known points using pure pixel motion. """
        if self.last_frame_gray is None or self.last_points is None:
            return None
            
        if self.ghost_count >= self.max_ghost_frames:
            return None

        current_gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        
        # Calculate optical flow
        new_points, status, error = cv2.calcOpticalFlowPyrLK(
            self.last_frame_gray, current_gray, self.last_points, None, **self.lk_params
        )

        if new_points is not None:
            self.last_points = new_points
            self.last_frame_gray = current_gray
            self.ghost_count += 1
            return new_points.reshape(-1, 2)
        
        return None
