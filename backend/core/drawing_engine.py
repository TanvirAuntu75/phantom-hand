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
        self.thickness = 4

        # 3D Mode Initialization
        self.mode_3d = False
        self._strokes_3d = []  # Permanent 3D strokes
        self.current_strokes_3d = {}  # Active 3D strokes keyed by hand_id

        # ── TELEPORT GUARD ────────────────────────────────────────────────────
        # Increased to 250px to handle very fast handwriting strokes without
        # accidentally 'lifting the pen'.
        self.MAX_JUMP_PX = 250
        # ─────────────────────────────────────────────────────────────────────

    def update(self, state: str, point: tuple = None, hand_id: str = "default", wrist_angle=0.0, z_depth=0.0):
        """
        Updates the drawing logic for a specific hand.
        """
        if state == "DRAW" and point is not None:
            px = int(point[0] * self.width)
            py = int(point[1] * self.height)
            z_scaled = float(z_depth * 800)
            
            # Initialize stroke list for this hand if it doesn't exist
            if hand_id not in self.current_strokes:
                self.current_strokes[hand_id] = []
            if hand_id not in self.current_strokes_3d:
                self.current_strokes_3d[hand_id] = []

            # ── Teleport Guard ──
            if len(self.current_strokes[hand_id]) > 0:
                last_p = self.current_strokes[hand_id][-1]
                dist = np.linalg.norm(np.array([px, py]) - np.array(last_p))
                
                if dist > self.MAX_JUMP_PX:
                    # Treat as a 'pen lift' and start a new segment
                    self.finish_stroke(hand_id)
                    self.current_strokes[hand_id] = [(px, py)]
                    if self.mode_3d:
                        self.current_strokes_3d[hand_id] = [[px, py, z_scaled]]
                    return

            self.current_strokes[hand_id].append((px, py))
            if self.mode_3d:
                # Store relative center based on width/height so 0,0,0 is center of screen for Three.js
                self.current_strokes_3d[hand_id].append([px - self.width/2, -(py - self.height/2), z_scaled])
        else:
            # If we were drawing, finish the stroke
            self.finish_stroke(hand_id)

    def finish_stroke(self, hand_id: str):
        """Commits the active stroke buffer to the permanent canvas."""
        if hand_id in self.current_strokes and len(self.current_strokes[hand_id]) > 1:
            # Draw the final stroke onto the permanent canvas
            pts = np.array(self.current_strokes[hand_id], np.int32)
            cv2.polylines(self.canvas, [pts], False, self.color, self.thickness)
            
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
                cv2.polylines(output, [pts], False, self.color, self.thickness)
        
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

        if len(self._strokes_3d) > 0:
            self._strokes_3d.pop()

    def clear_all(self):
        self.canvas = np.zeros_like(self.canvas)
        self.stroke_history = []
        self.current_strokes = {}
        self._strokes_3d = []
        self.current_strokes_3d = {}

    def clear(self):
        self.clear_all()

    def get_last_stroke_points(self, hand_id: str = None):
        """Returns the points of the last completed stroke for snapping"""
        # The prompt implies returning the last drawn stroke.
        # However, our basic DrawingEngine merges strokes onto canvas.
        # For the sake of the shape recognizer, we need access to raw stroke points.
        if hand_id and hand_id in self.current_strokes and len(self.current_strokes[hand_id]) > 0:
             return self.current_strokes[hand_id]

        # If no active stroke, fallback to returning empty or we'd need to have saved strokes.
        # Let's save the last completed stroke points just for this purpose.
        if hasattr(self, "last_completed_stroke") and self.last_completed_stroke:
             return self.last_completed_stroke

        return []

    def get_current_stroke_points(self, hand_id: str):
        """Returns the points of the currently active stroke for preview"""
        return self.current_strokes.get(hand_id, [])

    def snap_shape(self, hand_id: str, fitted_points: list, shape_name: str):
        """Replaces the last stroke with a perfect geometric shape"""
        # Erase the last stroke from the canvas (we just use undo since finish_stroke pushes to history)
        self.undo()

        # Draw the perfect shape
        pts = np.array(fitted_points, np.int32)

        # Polylines needs closed=True for most shapes except lines
        is_closed = shape_name not in ["LINE", "FREEFORM"]
        cv2.polylines(self.canvas, [pts], is_closed, self.color, self.thickness, self.line_type)

        # Save to history
        self.stroke_history.append(self.canvas.copy())
        if len(self.stroke_history) > 20: self.stroke_history.pop(0)

    def toggle_3d(self):
        self.mode_3d = not self.mode_3d

    def get_3d_strokes(self):
        formatted = []
        for stroke in self._strokes_3d:
            formatted.append({
                "points": stroke["points"],
                "color": stroke["color"],
                "width": stroke["width"]
            })
        for hand_id, pts in self.current_strokes_3d.items():
            if len(pts) > 1:
                # RGB format for Three.js instead of BGR
                formatted.append({
                    "points": pts,
                    "color": [self.color[2], self.color[1], self.color[0]],
                    "width": self.thickness
                })
        return formatted
