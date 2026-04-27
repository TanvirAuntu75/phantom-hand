# PHANTOM HAND
The Phantom Hand: Zero-Latency 3D Hand Tracking & Drawing Engine

A zero-keyboard, real-time hand gesture drawing and control system with a clinical JARVIS-style cypherpunk HUD. No mouse. No keyboard. Hands only.

## 🚀 One-Command Quickstart

**For Windows (PowerShell):**
```powershell
./scripts/start.ps1
```

**For Mac / Linux (Bash):**
```bash
./scripts/start.sh
```
*Note: This script will verify dependencies, download the AI models, install Python/Node packages silently, launch both the backend and frontend in the background, and open your browser to the HUD automatically.*

**Docker Deployment:**
```bash
docker-compose -f docker/docker-compose.yml up --build
```
*Note: Docker passthrough of the webcam (`/dev/video0`) is strictly supported on Linux local environments.*

---

## 🖐️ Gesture Reference

The system interprets 20 distinct hand gestures using a spatial tracking algorithm and `Pinch-to-Draw` mechanics.

| Gesture Name | Hand Pose | Action |
| --- | --- | --- |
| **PINCH / DRAW** | Thumb & Index fingertips touching | Draw on canvas. Emits ghost shape preview. |
| **ERASE** | Middle fingertip extended | Erases along the path. |
| **HOVER / STOP** | Open palm / resting | Lifts pen off canvas. |
| **SNAP_SHAPE** | Pinch & Release after drawing | Converts messy stroke into perfect geometry. |
| **UNDO** | Thumbs Up | Undoes the last stroke (Debounced). |
| **REDO** | Thumbs Down | Redoes the last undone stroke (Debounced). |
| **CLEAR** | Open Palm | Clears the entire canvas (Debounced 1.5s). |
| **SWIPE_RIGHT** | Hand moving right | Cycle to next color. |
| **SWIPE_LEFT** | Hand moving left | Cycle to previous color. |
| **SWIPE_UP** | Hand moving up | Increase brush size. |
| **SWIPE_DOWN** | Hand moving down | Decrease brush size. |
| **THREE_UP** | Three fingers extended | Toggle immersive 3D Mode. |
| **HORNS** | Index & Pinky extended | Cycle to next layer. |
| **L_SHAPE** | Thumb & Index forming 'L' | Toggle Horizontal Mirror. |
| **PINKY_ONLY** | Only Pinky extended | Toggle Voice Command Microphone. |
| **FOUR_CLOSE** | Four fingers touching thumb | Open Export Menu (or export OBJ if in 3D). |
| **ZOOM_IN** | Two hands pulling apart | Dolly camera forward (3D Mode only). |
| **ZOOM_OUT** | Two hands pushing together | Dolly camera backward (3D Mode only). |

---

## 🛠️ Adding a New Gesture (Step-by-Step)

1. **Define the Pose:** Open `backend/core/gesture_state.py`. Add the geometric logic (e.g., finger extension ratios) inside `get_state()`.
2. **Return the String:** Have your new logic return a specific string identifier (e.g., `"MY_NEW_GESTURE"`).
3. **Route the Command:** Open `backend/core/command_router.py`. Inside `route()`, add an `elif gesture == "MY_NEW_GESTURE":` block.
4. **Debounce (Optional):** Add your gesture string to the `self.cooldowns` dictionary in the `CommandRouter` constructor to prevent rapid-firing.
5. **Add HUD Icon:** Open `frontend/src/components/GestureIndicator.jsx` and add an entry mapping your string to a Unicode icon in `ICON_MAP`.

## 🖌️ Adding a New Brush Mode

1. **Add to Canvas:** Open `backend/core/drawing_engine.py`. Update the `update()` or `finish_stroke()` methods to utilize a new `cv2` rendering function based on `self.mode`.
2. **Add to HUD:** Open `frontend/src/components/BrushModeBar.jsx`. Add the 3-letter abbreviation to the `modes` array.
3. **Link to Voice (Optional):** Update `backend/utils/voice_controller.py` to map a spoken word to set your new `canvas.mode`.

---

## ⚠️ Troubleshooting

- **Camera Not Found:** Ensure your webcam isn't being used by another application (like Zoom/Teams). Change `CAMERA_INDEX=0` in `.env` to `1` or `2` if using external cameras.
- **Missing MediaPipe Model:** If the system crashes stating `hand_landmarker.task` is missing, the auto-downloader failed. You can download it manually from Google's servers and place it directly inside the `backend/` directory.
- **Port Conflicts:** If `http://localhost:3000` or `8000` is already in use, edit the `PORT` values inside `.env` and `frontend/vite.config.js`.
- **Low FPS:**
  1. Ensure you are running Python 3.11+.
  2. Check the HUD for "PERFORMANCE ALERT" socket events indicating high CPU/RAM.
  3. Lower the `CAMERA_WIDTH` and `CAMERA_HEIGHT` inside your `.env` file to `640x480` to relieve the OpenCV compositing bottleneck.
