import numpy as np
import cv2

class ShapeRecognizer:
    """
    Takes a messy hand-drawn stroke and snaps it into perfect geometric shapes.
    """
    def __init__(self):
        # We sample every stroke to exactly 128 points for consistent math
        self.target_points = 128

    def recognize_and_snap(self, stroke_points: list) -> dict:
        """
        Input: list of (x, y) tuples from the drawing engine.
        Output: dict with shape name, confidence, and 'perfect' fitted points.
        """
        if len(stroke_points) < 10:
            return self._fallback_freeform(stroke_points)

        # 1. Convert to numpy array
        pts = np.array(stroke_points, dtype=np.float32)

        # 2. Resample to uniform spacing
        pts = self._resample_points(pts, self.target_points)

        # 3. Calculate basic geometry
        x, y, w, h = cv2.boundingRect(pts)
        bbox_diagonal = np.sqrt(w**2 + h**2)
        
        # Check if shape is closed (start and end points are close)
        start_pt = pts[0]
        end_pt = pts[-1]
        dist_start_end = np.linalg.norm(start_pt - end_pt)
        is_closed = dist_start_end < (0.15 * bbox_diagonal)

        # 4. Simplify stroke to find hard corners (vertices)
        epsilon = 0.04 * cv2.arcLength(pts, is_closed)
        approx_vertices = cv2.approxPolyDP(pts, epsilon, is_closed)
        num_vertices = len(approx_vertices)

        # 5. Run Classifiers
        if is_closed:
            # Check for Circle/Ellipse
            if num_vertices > 6:
                # If area ratio is close to Pi/4, it's very circle/ellipse like
                area = cv2.contourArea(pts)
                bbox_area = w * h
                if bbox_area > 0 and 0.65 < (area / bbox_area) < 0.90:
                    return self._fit_ellipse_or_circle(pts)

            # Check for Square/Rectangle
            if num_vertices == 4:
                return self._fit_rectangle(approx_vertices)

            # Check for Triangle
            if num_vertices == 3:
                return self._fit_triangle(approx_vertices)

        else:
            # Check for straight line
            if num_vertices == 2 or (num_vertices > 2 and self._is_line(pts)):
                return self._fit_line(pts[0], pts[-1])

        # If nothing matches confidently, return the smoothed freeform stroke
        return self._fallback_freeform(stroke_points)

    # --- GEOMETRY FITTING METHODS ---

    def _resample_points(self, points, num_points):
        """Resamples an array of points to have exactly `num_points` evenly spaced along the arc."""
        # Calculate cumulative distance along the stroke
        diffs = np.diff(points, axis=0)
        dists = np.linalg.norm(diffs, axis=1)
        cum_dists = np.concatenate(([0], np.cumsum(dists)))
        
        total_len = cum_dists[-1]
        if total_len == 0:
            return points

        # Interpolate new points
        target_dists = np.linspace(0, total_len, num_points)
        new_x = np.interp(target_dists, cum_dists, points[:, 0])
        new_y = np.interp(target_dists, cum_dists, points[:, 1])
        
        return np.column_stack((new_x, new_y)).astype(np.float32)

    def _fit_ellipse_or_circle(self, pts):
        # Fit an ellipse
        if len(pts) < 5:
            return self._fallback_freeform(pts)
            
        (center_x, center_y), (axis_a, axis_b), angle = cv2.fitEllipse(pts)
        
        # If axes are very similar, it's a circle
        ratio = min(axis_a, axis_b) / max(axis_a, axis_b)
        
        if ratio > 0.85:
            # It's a Circle - average the radius
            radius = (axis_a + axis_b) / 4.0
            perfect_circle = []
            for i in range(64):
                theta = i * (2 * np.pi / 64)
                px = center_x + radius * np.cos(theta)
                py = center_y + radius * np.sin(theta)
                perfect_circle.append((px, py))
                
            return {
                "shape": "CIRCLE",
                "confidence": ratio,
                "fitted_points": perfect_circle
            }
        else:
            # It's an Ellipse (implement generation if needed)
            return {
                "shape": "ELLIPSE",
                "confidence": ratio,
                "fitted_points": pts.tolist() # Placeholder
            }

    def _fit_rectangle(self, approx_vertices):
        # We have 4 corners. Just return those 4 to draw a perfect polygon!
        # Close the loop by appending the first point at the end
        perfect_rect = [tuple(pt[0]) for pt in approx_vertices]
        perfect_rect.append(perfect_rect[0]) 
        
        return {
            "shape": "RECTANGLE",
            "confidence": 0.90,
            "fitted_points": perfect_rect
        }

    def _fit_triangle(self, approx_vertices):
        perfect_tri = [tuple(pt[0]) for pt in approx_vertices]
        perfect_tri.append(perfect_tri[0])
        return {
            "shape": "TRIANGLE",
            "confidence": 0.90,
            "fitted_points": perfect_tri
        }

    def _is_line(self, pts):
        # Check if all points fall roughly on the line between start and end
        start = pts[0]
        end = pts[-1]
        line_len = np.linalg.norm(start - end)
        if line_len == 0: return False
        
        # Calculate distance of all points to the line
        cross_prod = np.abs(np.cross(end - start, start - pts))
        distances = cross_prod / line_len
        
        # If max deviation is small, it's a straight line
        return np.max(distances) < (0.10 * line_len)

    def _fit_line(self, start, end):
        return {
            "shape": "LINE",
            "confidence": 0.95,
            "fitted_points": [tuple(start), tuple(end)]
        }

    def _fallback_freeform(self, pts):
        return {
            "shape": "FREEFORM",
            "confidence": 1.0,
            "fitted_points": [tuple(p) for p in pts]
        }
