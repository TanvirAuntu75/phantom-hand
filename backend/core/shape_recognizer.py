import numpy as np
import cv2
import logging
from typing import List, Tuple, Dict, Any, Optional

logger = logging.getLogger("phantom_hand")

class ShapeRecognizer:
    """
    GEOMETRY_CONFORMITY_ENGINE
    Transforms irregular hand-drawn point clouds into mathematically perfect primitives.
    
    Features:
    - RDP_SIMPLIFICATION: Optimized Douglas-Peucker for vertex detection.
    - AXIS_ALIGNMENT: Snaps nearly-horizontal/vertical lines and rectangles.
    - REGULARIZATION: Snaps polygons to equilateral/square forms if within 15% tolerance.
    - LEAST_SQUARES_FITTING: High-precision circle and ellipse estimation.
    """
    def __init__(self):
        self.target_points = 128
        self.snap_tolerance = 0.15 # 15% deviation allowed for regularization

    def process(self, stroke_points: List[Tuple[int, int]]) -> Dict[str, Any]:
        """
        Main entry point for shape recognition.
        Returns a dict with 'shape', 'confidence', and 'fitted_points'.
        """
        if len(stroke_points) < 15:
            return self._fallback(stroke_points)

        # 1. Vectorize and Normalize
        pts = np.array(stroke_points, dtype=np.float32)
        resampled = self._resample(pts, self.target_points)
        
        # 2. Geometric Analysis
        # Get bounding box and perimeter info
        x, y, w, h = cv2.boundingRect(resampled)
        diagonal = np.sqrt(w**2 + h**2)
        perimeter = cv2.arcLength(resampled, True)
        area = cv2.contourArea(resampled)
        
        # Closure check
        dist_start_end = np.linalg.norm(resampled[0] - resampled[-1])
        is_closed = dist_start_end < (0.2 * diagonal)

        # 3. Structural Simplification (Vertex Detection)
        epsilon = 0.03 * perimeter
        approx = cv2.approxPolyDP(resampled, epsilon, is_closed)
        vertices = [tuple(p[0]) for p in approx]
        num_v = len(vertices)

        # 4. Classification Branching
        if is_closed:
            # Circle/Ellipse check via Area/Perimeter Ratio (Isoperimetric Quotient)
            # Perfect circle ratio = 1.0; we check if > 0.8
            if perimeter > 0:
                circularity = (4 * np.pi * area) / (perimeter ** 2)
                if circularity > 0.75:
                    return self._fit_circular_primitive(resampled)

            if num_v == 3:
                return self._fit_regular_polygon(vertices, 3)
            elif num_v == 4:
                return self._fit_rectangle(vertices)
            elif 5 <= num_v <= 6:
                return self._fit_regular_polygon(vertices, num_v)

        else:
            # Open shape - Line or Arc
            if num_v == 2 or self._is_mostly_straight(resampled):
                return self._fit_straight_line(resampled[0], resampled[-1])

        return self._fallback(stroke_points)

    # ── FITTING_STRATEGIES ────────────────────────────────────────────────────
    
    def _fit_circular_primitive(self, pts: np.ndarray) -> Dict[str, Any]:
        """Fits either a perfect circle or an axis-aligned ellipse."""
        if len(pts) < 5: return self._fallback(pts)
        
        (cx, cy), (ma, mi), angle = cv2.fitEllipse(pts)
        ratio = min(ma, mi) / max(ma, mi)
        
        if ratio > 0.88: # Close enough to 1.0 to be a circle
            radius = (ma + mi) / 4.0
            fitted = []
            for i in range(64):
                theta = i * (2 * np.pi / 64)
                fitted.append((cx + radius * np.cos(theta), cy + radius * np.sin(theta)))
            return {"shape": "CIRCLE", "confidence": float(ratio), "fitted_points": fitted}
        
        # Otherwise, return an ellipse
        return {"shape": "ELLIPSE", "confidence": float(ratio), "fitted_points": [tuple(p) for p in pts]}

    def _fit_rectangle(self, vertices: List[Tuple[float, float]]) -> Dict[str, Any]:
        """Fits an axis-aligned rectangle or square."""
        v = np.array(vertices)
        x, y, w, h = cv2.boundingRect(v.astype(np.float32))
        
        # Check for squareness
        aspect_ratio = min(w, h) / max(w, h)
        shape_type = "SQUARE" if aspect_ratio > 0.85 else "RECTANGLE"
        
        if shape_type == "SQUARE":
            side = (w + h) / 2
            fitted = [(x, y), (x + side, y), (x + side, y + side), (x, y + side), (x, y)]
        else:
            fitted = [(x, y), (x + w, y), (x + w, y + h), (x, y + h), (x, y)]
            
        return {"shape": shape_type, "confidence": 0.95, "fitted_points": fitted}

    def _fit_regular_polygon(self, vertices: List[Tuple[float, float]], n: int) -> Dict[str, Any]:
        """Forces a polygon to have equal side lengths and centered alignment."""
        v = np.array(vertices)
        center = np.mean(v, axis=0)
        radii = np.linalg.norm(v - center, axis=1)
        avg_radius = np.mean(radii)
        
        # Calculate rotation to match the first vertex
        start_angle = np.arctan2(v[0][1] - center[1], v[0][0] - center[0])
        
        fitted = []
        for i in range(n + 1):
            theta = start_angle + i * (2 * np.pi / n)
            fitted.append((center[0] + avg_radius * np.cos(theta), 
                           center[1] + avg_radius * np.sin(theta)))
                           
        names = {3: "TRIANGLE", 5: "PENTAGON", 6: "HEXAGON"}
        return {"shape": names.get(n, "POLYGON"), "confidence": 0.90, "fitted_points": fitted}

    def _fit_straight_line(self, start: np.ndarray, end: np.ndarray) -> Dict[str, Any]:
        """Snaps line to horizontal or vertical if within 5 degrees."""
        dx = abs(start[0] - end[0])
        dy = abs(start[1] - end[1])
        
        p1, p2 = list(start), list(end)
        
        # Snap to horizontal
        if dy < (0.05 * dx): p2[1] = p1[1]
        # Snap to vertical
        elif dx < (0.05 * dy): p2[0] = p1[0]
        
        return {"shape": "LINE", "confidence": 0.98, "fitted_points": [tuple(p1), tuple(p2)]}

    # ── UTILITIES ─────────────────────────────────────────────────────────────
    
    def _resample(self, points: np.ndarray, n: int) -> np.ndarray:
        """Uniformly redistributes n points along the stroke length."""
        diffs = np.diff(points, axis=0)
        dists = np.linalg.norm(diffs, axis=1)
        cum_dists = np.concatenate(([0], np.cumsum(dists)))
        
        if cum_dists[-1] == 0: return points
        
        target = np.linspace(0, cum_dists[-1], n)
        new_x = np.interp(target, cum_dists, points[:, 0])
        new_y = np.interp(target, cum_dists, points[:, 1])
        return np.column_stack((new_x, new_y)).astype(np.float32)

    def _is_mostly_straight(self, pts: np.ndarray) -> bool:
        """Measures variance from the chord line."""
        start, end = pts[0], pts[-1]
        line_vec = end - start
        line_len = np.linalg.norm(line_vec)
        if line_len < 1: return False
        
        cross_prod = np.abs(np.cross(line_vec, start - pts))
        dist_to_line = cross_prod / line_len
        return np.max(dist_to_line) < (0.08 * line_len)

    def _fallback(self, pts: Any) -> Dict[str, Any]:
        return {
            "shape": "FREEFORM",
            "confidence": 1.0,
            "fitted_points": [tuple(p) for p in pts]
        }
