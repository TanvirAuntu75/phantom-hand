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

        # Start with black background
        output = np.zeros_like(canvas.canvas)

        # Composite canvas onto black
        gray = cv2.cvtColor(canvas.canvas, cv2.COLOR_BGR2GRAY)
        _, mask = cv2.threshold(gray, 1, 255, cv2.THRESH_BINARY)
        mask_inv = cv2.bitwise_not(mask)

        bg = cv2.bitwise_and(output, output, mask=mask_inv)
        fg = cv2.bitwise_and(canvas.canvas, canvas.canvas, mask=mask)
        final = cv2.add(bg, fg)

        cv2.imwrite(path, final)
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
        frame_canvas = np.zeros_like(canvas.canvas)

        # For a true replay, we draw each stroke progressively.
        # To keep processing reasonable, we draw full strokes one by one.
        for stroke in getattr(canvas, "raw_strokes_2d", []):
            pts = np.array(stroke["points"], np.int32)
            cv2.polylines(frame_canvas, [pts], False, stroke["color"], stroke["width"], cv2.LINE_AA)

            # Convert BGR to RGB for PIL
            rgb_frame = cv2.cvtColor(frame_canvas, cv2.COLOR_BGR2RGB)
            frames.append(Image.fromarray(rgb_frame))

        if not frames:
            # If empty, just save one black frame
            frames.append(Image.fromarray(np.zeros((canvas.height, canvas.width, 3), dtype=np.uint8)))

        # Hold final frame
        for _ in range(10):
            frames.append(frames[-1])

        # duration in ms per frame
        duration = int(1000 / fps)

        frames[0].save(
            path,
            save_all=True,
            append_images=frames[1:],
            duration=duration,
            loop=0
        )
        return path, filename

    def export_mp4(self, canvas, filepath=None, fps: int = 30) -> tuple[str, str]:
        """Saves a replay as an MP4 video."""
        path, filename = self._generate_filepath("mp4")
        if filepath: path = filepath

        fourcc = cv2.VideoWriter_fourcc(*'mp4v')
        out = cv2.VideoWriter(path, fourcc, fps, (canvas.width, canvas.height))

        frame_canvas = np.zeros_like(canvas.canvas)

        for stroke in getattr(canvas, "raw_strokes_2d", []):
            pts = np.array(stroke["points"], np.int32)
            cv2.polylines(frame_canvas, [pts], False, stroke["color"], stroke["width"], cv2.LINE_AA)
            out.write(frame_canvas)

        # Hold final frame for 1 second (30 frames)
        for _ in range(30):
            out.write(frame_canvas)

        out.release()
        return path, filename
