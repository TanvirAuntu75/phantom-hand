import numpy as np

class GestureState:
    """
    Translates raw 3D landmarks into stable semantic states (DRAW, HOVER).
    Uses 'Palm-Scale Ratios' and 'Sticky' debounce to ensure smooth handwriting.
    """
    def __init__(self):
        # State: "DRAW" or "HOVER"
        self.current_state = "HOVER"
        
        # History for 'Sticky' logic (must be 2 out of 3 frames to flip state)
        self.history = []
        self.STREAK_REQUIRED = 2
        
        # Thresholds (relative to palm size)
        # Palm Size is the distance between Wrist [0] and Middle Knuckle [9]
        self.DRAW_EXTEND_RATIO = 0.65  # Index must be extended > 65% of palm size
        self.KILL_EXTEND_RATIO = 0.70  # Drawing stops if other fingers extend > 70% of palm size

    def get_state(self, landmarks):
        """
        landmarks: list of 21 (x, y, z) normalized tuples.
        """
        # 1. Calculate Palm Scale (Reference for depth/size)
        wrist = np.array(landmarks[0])
        m_mcp = np.array(landmarks[9]) # Middle finger knuckle
        palm_size = np.linalg.norm(wrist - m_mcp)
        
        if palm_size == 0: return "HOVER"

        # 2. Check Index Extension (Fingertip [8] to Knuckle [5])
        i_tip = np.array(landmarks[8])
        i_mcp = np.array(landmarks[5])
        index_extension = np.linalg.norm(i_tip - i_mcp)
        index_ratio = index_extension / palm_size
        
        # 3. Check Middle & Ring Extension (The 'Kill' switch)
        # In natural handwriting, these fingers are curled.
        # If they straighten out (High-Five), we stop drawing.
        m_tip = np.array(landmarks[12])
        m_knuckle = np.array(landmarks[9])
        middle_ratio = np.linalg.norm(m_tip - m_knuckle) / palm_size
        
        r_tip = np.array(landmarks[16])
        r_knuckle = np.array(landmarks[13])
        ring_ratio = np.linalg.norm(r_tip - r_knuckle) / palm_size

        # --- Decision Logic ---
        raw_state = "HOVER"
        
        # Condition: Index is pointing, and middle/ring are safely curled
        if index_ratio > self.DRAW_EXTEND_RATIO:
            if middle_ratio < self.KILL_EXTEND_RATIO and ring_ratio < self.KILL_EXTEND_RATIO:
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
