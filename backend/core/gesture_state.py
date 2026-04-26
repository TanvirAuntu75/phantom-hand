import numpy as np

class GestureState:
    """
    Translates raw 3D landmarks into stable semantic states (DRAW, HOVER).
    Uses 'Pinch-to-Draw' logic (Thumb tip touching Index tip) for extreme reliability.
    """
    def __init__(self):
        # State: "DRAW" or "HOVER"
        self.current_state = "HOVER"
        
        # History for 'Sticky' logic (must be consistent for a few frames to flip state)
        self.history = []
        self.STREAK_REQUIRED = 2
        
        # Thresholds (relative to palm size)
        # Palm Size is the distance between Wrist [0] and Middle Knuckle [9]
        self.PINCH_DRAW_RATIO = 0.25 # If thumb and index tip distance is < 25% of palm size, it's a pinch

    def get_state(self, landmarks):
        """
        landmarks: list of 21 (x, y, z) normalized tuples.
        """
        # 1. Calculate Palm Scale (Reference for depth/size)
        wrist = np.array(landmarks[0])
        m_mcp = np.array(landmarks[9]) # Middle finger knuckle
        palm_size = np.linalg.norm(wrist - m_mcp)
        
        if palm_size == 0: return "HOVER"

        # 2. Check Pinch Distance (Thumb Tip [4] to Index Tip [8])
        thumb_tip = np.array(landmarks[4])
        index_tip = np.array(landmarks[8])
        pinch_dist = np.linalg.norm(thumb_tip - index_tip)
        pinch_ratio = pinch_dist / palm_size
        
        # --- Decision Logic ---
        raw_state = "HOVER"
        
        # Condition: Thumb and index are touching (pinched)
        if pinch_ratio < self.PINCH_DRAW_RATIO:
             raw_state = "DRAW"

        # --- Sticky Debounce ---
        self.history.append(raw_state)
        if len(self.history) > 3:
            self.history.pop(0)
            
        # Only change state if the raw observation is consistent
        draw_count = self.history.count("DRAW")
        if draw_count >= self.STREAK_REQUIRED:
            self.current_state = "DRAW"
        else:
            self.current_state = "HOVER"
            
        return self.current_state
