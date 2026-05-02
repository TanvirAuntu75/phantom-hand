with open('backend/core/drawing_engine.py', 'r') as f:
    content = f.read()

import re

additions = """
    def set_brush(self, brush_name: str) -> None:
        if brush_name in self.brush_modes:
            self.active_brush_idx = self.brush_modes.index(brush_name)
            logger.info(f"BRUSH_SELECTED: {self.active_brush}")

    def set_layer(self, layer_idx: int) -> None:
        if 0 <= layer_idx < self.num_layers:
            self.active_layer = layer_idx
            logger.info(f"LAYER_SWITCHED: {self.active_layer}")
"""

# add it after toggle_mirror
content = content.replace('    # ── INTERNAL_UTILITIES', additions + '\n    # ── INTERNAL_UTILITIES')

with open('backend/core/drawing_engine.py', 'w') as f:
    f.write(content)

with open('backend/utils/voice_controller.py', 'r') as f:
    content = f.read()

content = content.replace('self.canvas.set_brush("NEON', 'self.canvas.set_brush("NEON")')
content = content.replace('self.canvas.set_brush("LASER', 'self.canvas.set_brush("LASER")')
content = content.replace('self.canvas.set_brush("CHALK', 'self.canvas.set_brush("CHALK")')
content = content.replace('self.canvas.set_brush("GHOST', 'self.canvas.set_brush("GHOST")')

with open('backend/utils/voice_controller.py', 'w') as f:
    f.write(content)
