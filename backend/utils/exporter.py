import os
import cv2
import numpy as np
from datetime import datetime
from PIL import Image

class Exporter:
    def __init__(self, export_dir="exports"):
        self.export_dir = export_dir
        os.makedirs(self.export_dir, exist_ok=True)

    def _generate_filepath(self, ext: str) -> str:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"phantom_hand_{timestamp}.{ext}"
        return os.path.join(self.export_dir, filename), filename

    def export_png(self, canvas, filepath=None) -> tuple[str, str]:
        """Flattens visible layers over black background."""
        path, filename = self._generate_filepath("png")
        if filepath: path = filepath

        # We must use canvas.layers[0] since canvas.canvas is undefined in DrawingEngine implementation
        height, width = canvas.height, canvas.width
        output = np.zeros((height, width, 3), dtype=np.uint8)

        # Composite all permanent layers (bottom to top)
        for layer in canvas.layers:
            mask = layer.any(axis=2)
            output[mask] = layer[mask]

        cv2.imwrite(path, output)
        return path, filename

    def export_svg(self, canvas, filepath=None) -> tuple[str, str]:
        """Creates vector SVG from raw strokes."""
        path, filename = self._generate_filepath("svg")
        if filepath: path = filepath

        lines = []
        lines.append(f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {canvas.width} {canvas.height}">')
        lines.append(f'<rect width="{canvas.width}" height="{canvas.height}" fill="#050A14" />')

        for stroke in getattr(canvas, "raw_strokes_2d", []):
            points = stroke["points"]
            if len(points) < 2: continue

            # Convert BGR tuple to HEX
            b, g, r = stroke["color"]
            hex_color = f"#{r:02x}{g:02x}{b:02x}"
            width = stroke["width"]

            pts_str = " ".join([f"{p[0]},{p[1]}" for p in points])
            lines.append(f'<polyline points="{pts_str}" fill="none" stroke="{hex_color}" stroke-width="{width}" stroke-linecap="round" stroke-linejoin="round" />')

        lines.append('</svg>')

        with open(path, "w") as f:
            f.write("\n".join(lines))

        return path, filename

    def export_gif(self, canvas, filepath=None, fps: int = 20) -> tuple[str, str]:
        """Replays drawing frame by frame into an animated GIF."""
        path, filename = self._generate_filepath("gif")
        if filepath: path = filepath

        frames = []
        frame_canvas = np.zeros((canvas.height, canvas.width, 3), dtype=np.uint8)

        for stroke in getattr(canvas, "raw_strokes_2d", []):
            pts = np.array(stroke["points"], np.int32)
            cv2.polylines(frame_canvas, [pts], False, stroke["color"], stroke["width"], cv2.LINE_AA)
            rgb_frame = cv2.cvtColor(frame_canvas, cv2.COLOR_BGR2RGB)
            frames.append(Image.fromarray(rgb_frame))

        if not frames:
            frames.append(Image.fromarray(frame_canvas))

        for _ in range(10):
            frames.append(frames[-1])

        duration = int(1000 / fps)
        frames[0].save(
            path, save_all=True, append_images=frames[1:], duration=duration, loop=0
        )
        return path, filename

    def export_mp4(self, canvas, filepath=None, fps: int = 30) -> tuple[str, str]:
        """Saves a replay as an MP4 video."""
        path, filename = self._generate_filepath("mp4")
        if filepath: path = filepath

        fourcc = cv2.VideoWriter_fourcc(*'mp4v')
        out = cv2.VideoWriter(path, fourcc, fps, (canvas.width, canvas.height))

        frame_canvas = np.zeros((canvas.height, canvas.width, 3), dtype=np.uint8)

        for stroke in getattr(canvas, "raw_strokes_2d", []):
            pts = np.array(stroke["points"], np.int32)
            cv2.polylines(frame_canvas, [pts], False, stroke["color"], stroke["width"], cv2.LINE_AA)
            out.write(frame_canvas)

        for _ in range(30):
            out.write(frame_canvas)

        out.release()
        return path, filename
