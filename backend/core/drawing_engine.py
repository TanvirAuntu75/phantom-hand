import cv2
import numpy as np

class DrawingEngine:
    """
    Manages the digital canvas, recording strokes and rendering lines.
    """
    def __init__(self, width=1280, height=720):
        self.width = width
        self.height = height
        
        # The main canvas where drawings live permanently
        self.canvas = np.zeros((height, width, 3), dtype=np.uint8)
        
        # Current active strokes — one buffer PER HAND (keyed by hand_id string)
        self.current_strokes = {}   # e.g. {"Left": [...], "Right": [...]}
        
        # History for Undo feature
        self.stroke_history = []
        
        # Brand Colors
        self.color = (255, 229, 0) # Electric Cyan (BGR)
        self.thickness = 6 # Slightly thicker for better visibility

        # Anti-aliased lines for much smoother rendering
        self.line_type = cv2.LINE_AA

        # ── TELEPORT GUARD ────────────────────────────────────────────────────
        # Increased to 250px to handle very fast handwriting strokes without
        # accidentally 'lifting the pen'.
        self.MAX_JUMP_PX = 250
        # ─────────────────────────────────────────────────────────────────────

    def update(self, state: str, point: tuple = None, hand_id: str = "default"):
        """
        Updates the drawing logic for a specific hand.
        state   : "DRAW" or "HOVER"
        point   : (x, y) normalised [0.0 – 1.0], or None
        hand_id : "Left", "Right", or any unique label
        """
        if state == "DRAW" and point is not None:
            px = int(point[0] * self.width)
            py = int(point[1] * self.height)
            
            # Initialize stroke list for this hand if it doesn't exist
            if hand_id not in self.current_strokes:
                self.current_strokes[hand_id] = []

            # ── Teleport Guard ──
            if len(self.current_strokes[hand_id]) > 0:
                last_p = self.current_strokes[hand_id][-1]
                dist = np.linalg.norm(np.array([px, py]) - np.array(last_p))
                
                if dist > self.MAX_JUMP_PX:
                    # Treat as a 'pen lift' and start a new segment
                    self.finish_stroke(hand_id)
                    self.current_strokes[hand_id] = [(px, py)]
                    return

            self.current_strokes[hand_id].append((px, py))
        else:
            # If we were drawing, finish the stroke
            self.finish_stroke(hand_id)

    def finish_stroke(self, hand_id: str):
        """Commits the active stroke buffer to the permanent canvas."""
        if hand_id in self.current_strokes and len(self.current_strokes[hand_id]) > 1:
            # Draw the final stroke onto the permanent canvas
            pts = np.array(self.current_strokes[hand_id], np.int32)
            cv2.polylines(self.canvas, [pts], False, self.color, self.thickness, self.line_type)
            
            # Save to history for undo
            self.stroke_history.append(self.canvas.copy())
            if len(self.stroke_history) > 20: self.stroke_history.pop(0)
            
            self.current_strokes[hand_id] = []

    def render(self, frame):
        """Composites the drawings on top of the camera frame."""
        # Start with the permanent canvas
        output = self.canvas.copy()
        
        # Add all active (incomplete) strokes from all hands
        for hand_id, stroke_pts in self.current_strokes.items():
            if len(stroke_pts) > 1:
                pts = np.array(stroke_pts, np.int32)
                cv2.polylines(output, [pts], False, self.color, self.thickness, self.line_type)
        
        # Mask where drawing exists
        gray = cv2.cvtColor(output, cv2.COLOR_BGR2GRAY)
        _, mask = cv2.threshold(gray, 1, 255, cv2.THRESH_BINARY)
        mask_inv = cv2.bitwise_not(mask)
        
        # Combine
        img_bg = cv2.bitwise_and(frame, frame, mask=mask_inv)
        img_fg = cv2.bitwise_and(output, output, mask=mask)
        
        return cv2.add(img_bg, img_fg)

    def undo(self):
        if len(self.stroke_history) > 0:
            self.stroke_history.pop()
            if len(self.stroke_history) > 0:
                self.canvas = self.stroke_history[-1].copy()
            else:
                self.canvas = np.zeros_like(self.canvas)

    def clear(self):
        self.canvas = np.zeros_like(self.canvas)
        self.stroke_history = []
        self.current_strokes = {}
