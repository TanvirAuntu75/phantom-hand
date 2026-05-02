import cv2
import numpy as np
import logging
from typing import List, Tuple, Dict, Optional, Any

logger = logging.getLogger("phantom_hand")

class DrawingEngine:
    """
    KINETIC_RENDERING_CORE
    Manages the multi-layer drawing surface, brush physics, and vector state history.
    
    Upgrades:
    - QUAD_LAYER_ARCHITECTURE: True independent layers.
    - BRUSH_PHYSICS: Neon (Glow), Laser (Sharp), and Ghost (Fade) modes.
    - DUAL_STACK_HISTORY: Full Undo and Redo capabilities.
    - PERFORMANCE_PIPELINE: Optimized blend masks using bitwise operations.
    """
    def __init__(self, width: int = 1280, height: int = 720):
        self.width = width
        self.height = height
        
        # ── LAYER_STORAGE ─────────────────────────────────────────────────────
        self.num_layers = 5
        self.active_layer = 0
        # Permanent canvases per layer
        self.layers = [np.zeros((height, width, 3), dtype=np.uint8) for _ in range(self.num_layers)]
        
        # Active stroke buffers (Real-time tracking)
        self.current_strokes: Dict[str, List[Tuple[int, int]]] = {}
        self.current_z_depths: Dict[str, List[float]] = {}
        self.raw_strokes_2d = []
        
        # ── HISTORY_ENGINE ────────────────────────────────────────────────────
        # Stores (layer_index, canvas_snapshot)
        self._undo_stack: List[Tuple[int, np.ndarray]] = []
        self._redo_stack: List[Tuple[int, np.ndarray]] = []
        self._MAX_HISTORY = 15

        # ── BRUSH_CONFIG ──────────────────────────────────────────────────────
        self.brush_modes = ["LASER", "NEON", "GHOST", "CHALK"]
        self.active_brush_idx = 0
        
        self.palette = [
            (255, 229, 0),   # Electric Cyan (BGR)
            (255, 0, 255),   # Magenta
            (0, 255, 128),   # Spring Green
            (0, 165, 255),   # Orange
            (255, 255, 255), # Pure White
        ]
        self.color_idx = 0
        self.thickness = 4
        
        # 3D State
        self.mode_3d = False
        self.completed_strokes_3d = [] # list of {points, color, width}

        # Render Cache
        self._dirty = True
        self._cached_composite: Optional[np.ndarray] = None

    @property
    def current_color(self) -> Tuple[int, int, int]:
        return self.palette[self.color_idx]

    @property
    def active_brush(self) -> str:
        return self.brush_modes[self.active_brush_idx]

    # ── PUBLIC_API ────────────────────────────────────────────────────────────
    def update(self, action: str, point: Tuple[float, float], hand_id: str, 
               angle: float = 0.0, z_depth: float = 0.0) -> None:
        """
        KINETIC_UPDATE_SIGNAL
        Dispatched by CommandRouter to modify canvas state.
        """
        if action == "DRAW":
            px, py = int(point[0] * self.width), int(point[1] * self.height)
            
            # Robust initialization
            if hand_id not in self.current_strokes or hand_id not in self.current_z_depths:
                self.current_strokes[hand_id] = []
                self.current_z_depths[hand_id] = []

            # Teleport guard
            if self.current_strokes[hand_id]:
                last_px, last_py = self.current_strokes[hand_id][-1]
                dist = ((px - last_px)**2 + (py - last_py)**2)**0.5
                if dist > 250: # MAX_JUMP_PX
                    self.finish_stroke(hand_id)
                
            self.current_strokes[hand_id].append((px, py))
            self.current_z_depths[hand_id].append(z_depth)
            self._dirty = True
            
        elif action == "ERASE":
            px, py = int(point[0] * self.width), int(point[1] * self.height)
            self._apply_erase(px, py)
            self._dirty = True
            
        elif action == "HOVER":
            # Hand lifted or hovering
            self.finish_stroke(hand_id)

    def finish_stroke(self, hand_id: str) -> None:
        """COMMITS current stroke buffer to the active layer."""
        if hand_id not in self.current_strokes or len(self.current_strokes[hand_id]) < 2:
            # Clear but ensure consistency
            self.current_strokes[hand_id] = []
            self.current_z_depths[hand_id] = []
            return

        # 1. Save history before modification
        self._push_undo()
        
        # 2. Render the stroke onto the permanent layer
        pts = np.array(self.current_strokes[hand_id], np.int32)
        self._render_stroke_to_surface(self.layers[self.active_layer], pts, self.active_brush)

        # 3. Archive for 3D / Vector Export
        if self.mode_3d:
            self.completed_strokes_3d.append({
                "points": self.current_strokes[hand_id],
                "z_depths": self.current_z_depths[hand_id],
                "color": self.current_color,
                "width": self.thickness
            })
        self.raw_strokes_2d.append({
            "points": self.current_strokes[hand_id],
            "color": self.current_color,
            "width": self.thickness
        })

        # 4. Clear buffers
        self.current_strokes[hand_id] = []
        self.current_z_depths[hand_id] = []
        self._dirty = True

    def render(self, background: np.ndarray) -> np.ndarray:
        """
        COMPOSITE_PIPELINE
        Blends all layers and active strokes onto the camera frame.
        """
        if not self._dirty and self._cached_composite is not None:
            return self._cached_composite

        # Create temporary drawing surface
        drawing_surface = np.zeros_like(background)
        
        # 1. Composite all permanent layers (bottom to top)
        for layer in self.layers:
            # Efficient overlay where layer is non-zero
            mask = layer.any(axis=2)
            drawing_surface[mask] = layer[mask]

        # 2. Overlay current active strokes (previews)
        for hand_id, pts in self.current_strokes.items():
            if len(pts) > 1:
                np_pts = np.array(pts, np.int32)
                self._render_stroke_to_surface(drawing_surface, np_pts, self.active_brush)

        # 3. Final Blend with camera frame
        mask = drawing_surface.any(axis=2)
        final = background.copy()
        final[mask] = drawing_surface[mask]
        
        self._cached_composite = final
        self._dirty = False
        return final

    # ── ENGINE_CONTROLS ───────────────────────────────────────────────────────
    def undo(self) -> None:
        if self._undo_stack:
            layer_idx, snapshot = self._undo_stack.pop()
            # Save current state to redo stack
            self._redo_stack.append((layer_idx, self.layers[layer_idx].copy()))
            self.layers[layer_idx] = snapshot
            self._dirty = True
            logger.info("UNDO_EXECUTED")

    def redo(self) -> None:
        if self._redo_stack:
            layer_idx, snapshot = self._redo_stack.pop()
            self._undo_stack.append((layer_idx, self.layers[layer_idx].copy()))
            self.layers[layer_idx] = snapshot
            self._dirty = True
            logger.info("REDO_EXECUTED")

    def clear(self) -> None:
        self._push_undo()
        self.layers[self.active_layer].fill(0)
        self.current_strokes = {}
        self._dirty = True

    def next_brush(self) -> None:
        self.active_brush_idx = (self.active_brush_idx + 1) % len(self.brush_modes)
        logger.info(f"BRUSH_SELECTED: {self.active_brush}")

    def next_color(self) -> None:
        self.color_idx = (self.color_idx + 1) % len(self.palette)

    def next_layer(self) -> None:
        self.active_layer = (self.active_layer + 1) % self.num_layers
        logger.info(f"LAYER_SWITCHED: {self.active_layer}")

    def prev_color(self) -> None:
        self.color_idx = (self.color_idx - 1) % len(self.palette)
        logger.info(f"COLOR_SELECTED: {self.current_color}")

    def increase_size(self) -> None:
        self.thickness = min(50, self.thickness + 2)
        logger.info(f"THICKNESS_INCREASED: {self.thickness}")

    def decrease_size(self) -> None:
        self.thickness = max(1, self.thickness - 2)
        logger.info(f"THICKNESS_DECREASED: {self.thickness}")

    def toggle_mirror(self) -> None:
        # Placeholder for mirroring logic
        logger.info("MIRROR_MODE_TOGGLED (STUB)")

    # ── INTERNAL_UTILITIES ────────────────────────────────────────────────────
    def _push_undo(self) -> None:
        self._undo_stack.append((self.active_layer, self.layers[self.active_layer].copy()))
        if len(self._undo_stack) > self._MAX_HISTORY:
            self._undo_stack.pop(0)
        self._redo_stack.clear() # Break redo chain on new action

    def _apply_erase(self, x: int, y: int) -> None:
        """Erases a circular region on the active layer."""
        cv2.circle(self.layers[self.active_layer], (x, y), self.thickness * 4, (0, 0, 0), -1)

    def _render_stroke_to_surface(self, surface: np.ndarray, pts: np.ndarray, brush: str) -> None:
        """Applies specialized brush rendering logic."""
        color = self.current_color
        
        if brush == "LASER":
            cv2.polylines(surface, [pts], False, color, self.thickness, cv2.LINE_AA)
        
        elif brush == "NEON":
            # Glow effect: draw thick blurred lines first, then sharp core
            cv2.polylines(surface, [pts], False, color, self.thickness * 3, cv2.LINE_AA)
            # The 'glow' typically requires a post-processing blur or multiple additive passes
            # For direct BGR rendering, we simulate with multiple line widths
            cv2.polylines(surface, [pts], False, color, self.thickness * 2, cv2.LINE_AA)
            cv2.polylines(surface, [pts], False, (255, 255, 255), self.thickness // 2, cv2.LINE_AA)
            
        elif brush == "GHOST":
            # Semi-transparent strokes (simulated)
            # Note: OpenCV doesn't support transparency in polylines directly on a mask
            # We draw at full strength; the HUD handles transparency logic if needed.
            cv2.polylines(surface, [pts], False, color, self.thickness, cv2.LINE_AA)

        elif brush == "CHALK":
            # Rough, textured line using a dotted pattern
            for i in range(len(pts) - 1):
                if i % 2 == 0:
                    cv2.line(surface, tuple(pts[i]), tuple(pts[i+1]), color, self.thickness, cv2.LINE_4)

    def get_last_stroke(self, hand_id: str) -> Optional[List[Tuple[int, int]]]:
        """Provides data for shape recognition."""
        # This would require an additional buffer of the last committed stroke
        return None # Placeholder for recognition logic integration
