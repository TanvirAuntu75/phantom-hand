import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

import asyncio
import base64
import cv2
import logging
import time
from datetime import datetime
from threading import Thread, Event
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import socketio

from backend.config import settings
from backend.core.hand_tracker import UltimateHandTracker
from backend.core.drawing_engine import DrawingEngine
from backend.core.command_router import CommandRouter
from backend.core.shape_recognizer import ShapeRecognizer

# The prompt said use "CameraStream (backend/core/hand_tracker.py)".
# CameraStream is nested inside the __main__ block of hand_tracker.py, so it's not importable.
# But we are told NOT to touch core files. So we must recreate it exactly here as a wrapper or utility.
class CameraStream:
    def __init__(self):
        self.stream = cv2.VideoCapture(settings.CAMERA_INDEX)
        self.stream.set(cv2.CAP_PROP_FRAME_WIDTH, settings.CAMERA_WIDTH)
        self.stream.set(cv2.CAP_PROP_FRAME_HEIGHT, settings.CAMERA_HEIGHT)
        self.stream.set(cv2.CAP_PROP_BUFFERSIZE, 1)
        self.frame = None
        self.stopped = False
    def start(self):
        Thread(target=self.update, args=(), daemon=True).start()
        return self
    def update(self):
        while not self.stopped:
            ret, frame = self.stream.read()
            if ret:
                self.frame = cv2.flip(frame, 1)
    def read(self):
        return self.frame
    def stop(self):
        self.stopped = True
        self.stream.release()

# ── LOGGING ───────────────────────────────────────────────────────────────────
logging.basicConfig(
    level=logging.DEBUG,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[
        logging.FileHandler("phantom_hand.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# ── APP INITIALIZATION ────────────────────────────────────────────────────────
app = FastAPI(title="PHANTOM HAND Backend")

# Allow all origins for local development
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize Socket.IO with ASGI wrapper
sio = socketio.AsyncServer(async_mode='asgi', cors_allowed_origins='*')
socket_app = socketio.ASGIApp(sio, other_asgi_app=app)

# ── GLOBAL STATE ──────────────────────────────────────────────────────────────
tracker: UltimateHandTracker = None
canvas: DrawingEngine = None
cam: CameraStream = None
router: CommandRouter = None
recognizer: ShapeRecognizer = None
gesture_states = {}

pipeline_event = Event()
pipeline_thread: Thread = None
last_encoded_frame = None
last_hand_data = None

# A mock class for GestureResult to simulate the gesture_engine output since it is not built yet
class MockGestureResult:
    def __init__(self, gesture):
        self.gesture = gesture

# ── PIPELINE THREAD ───────────────────────────────────────────────────────────
def pipeline_loop():
    """
    Background thread running the computer vision and drawing pipeline at full speed.
    It reads frames, runs AI, updates the canvas, and caches the final JPEG.
    """
    global last_encoded_frame, last_hand_data

    logger.info("Pipeline thread started.")

    while not pipeline_event.is_set():
        start_time = time.time()

        frame = cam.read()
        if frame is None:
            time.sleep(0.01)
            continue

        h, w = frame.shape[:2]

        # 1. Run AI tracking
        try:
            tracker.process_frame(frame, w, h)
        except Exception as e:
            logger.error(f"Error in process_frame: {e}")

        all_hands = tracker.get_all_hands(frame, w, h)
        current_hand_data = []

        # 2. Process gestures and update drawing
        for tracked_id, (landmarks, is_ghost_hand) in all_hands.items():

            # Use gesture_engine logic
            try:
                # Based on context: gesture_engine.py outputs GestureResult with .gesture string
                from backend.core.gesture_engine import GestureEngine

                # In a real impl, we'd initialize the engine globally or per-hand,
                # but following the previous pattern:
                if 'gesture_engine' not in globals():
                    global gesture_engine
                    gesture_engine = GestureEngine()

                # Assuming standard interface process(landmarks)
                gesture_result = gesture_engine.process(landmarks)
                gesture = gesture_result.gesture if hasattr(gesture_result, "gesture") else "HOVER"
            except ImportError:
                # Fallback to gesture_state if gesture_engine doesn't exist
                try:
                    from backend.core.gesture_state import GestureState
                    if tracked_id not in gesture_states:
                        gesture_states[tracked_id] = GestureState()
                    raw_state = gesture_states[tracked_id].get_state(landmarks)
                    gesture = "DRAW" if raw_state == "DRAW" else "HOVER"
                except ImportError:
                    gesture = "HOVER"

                # Create mock result object to satisfy router interface
                class MockResult:
                    def __init__(self, g):
                        self.gesture = g
                gesture_result = MockResult(gesture)

            if router:
                router.route(tracked_id, gesture_result, landmarks)

            current_hand_data.append({
                "id": tracked_id,
                "is_ghost": is_ghost_hand,
                "landmarks": landmarks,
                "gesture": gesture
            })

        # 3. Render frame with composited canvas
        final_frame = canvas.render(frame)

        # 4. JPEG encode at configured quality
        encode_param = [int(cv2.IMWRITE_JPEG_QUALITY), settings.JPEG_QUALITY]
        success, encoded_img = cv2.imencode('.jpg', final_frame, encode_param)

        if success:
            last_encoded_frame = encoded_img.tobytes()
            last_hand_data = current_hand_data

        # 5. Throttle to target FPS
        elapsed = time.time() - start_time
        target_delay = 1.0 / settings.TARGET_FPS
        if elapsed < target_delay:
            time.sleep(target_delay - elapsed)

# ── LIFECYCLE EVENTS ──────────────────────────────────────────────────────────
@app.on_event("startup")
async def startup_event():
    global tracker, canvas, cam, pipeline_thread, router, recognizer
    logger.info("Initializing PHANTOM HAND subsystems...")

    # Initialize Camera
    cam = CameraStream()
    cam.start()

    # Download model asynchronously
    def download_model():
        if not os.path.exists("hand_landmarker.task"):
            import urllib.request
            logger.info("Downloading MediaPipe model...")
            urllib.request.urlretrieve("https://storage.googleapis.com/mediapipe-models/hand_landmarker/hand_landmarker/float16/1/hand_landmarker.task", "hand_landmarker.task")

    await asyncio.to_thread(download_model)

    tracker = UltimateHandTracker(model_path="hand_landmarker.task")
    canvas = DrawingEngine(settings.CAMERA_WIDTH, settings.CAMERA_HEIGHT)
    recognizer = ShapeRecognizer()
    router = CommandRouter(canvas, recognizer)

    # Start Pipeline Thread
    pipeline_event.clear()
    pipeline_thread = Thread(target=pipeline_loop, daemon=True)
    pipeline_thread.start()

    # Start Asyncio Broadcaster
    asyncio.create_task(broadcast_loop())
    logger.info("System Online. Awaiting connections.")

@app.on_event("shutdown")
async def shutdown_event():
    logger.info("Shutting down PHANTOM HAND...")
    pipeline_event.set()
    if pipeline_thread:
        pipeline_thread.join()
    if cam:
        cam.stop()

# ── WEBSOCKET BROADCASTER ─────────────────────────────────────────────────────
async def broadcast_loop():
    """
    Pulls the latest cached frame and hand data, emitting it to all connected clients.
    """
    while True:
        if last_encoded_frame is not None:
            b64_frame = base64.b64encode(last_encoded_frame).decode('utf-8')

            await sio.emit("video_frame", {"image": f"data:image/jpeg;base64,{b64_frame}"})
            # Get current system state from canvas if available
            system_state = {
                "brushMode": "PNC",
                "activeLayer": 1,
                "totalLayers": 5,
                "brushSize": getattr(canvas, "thickness", 12) if canvas else 12,
                "mirrorH": False,
                "mirrorV": False,
                "color": getattr(canvas, "color", "#00E5FF") if canvas else "#00E5FF",
                "colorIndex": 1,
                "totalColors": 7
            }
            if canvas and hasattr(canvas, "get_state"):
                system_state.update(canvas.get_state())

            await sio.emit("hand_data", {
                "fps": tracker.get_fps() if tracker else 0.0,
                "hands": last_hand_data or [],
                "systemState": system_state
            })

        await asyncio.sleep(1.0 / settings.TARGET_FPS)

# ── WEBSOCKET HANDLERS ────────────────────────────────────────────────────────
@sio.on("connect")
async def connect(sid, environ):
    logger.info(f"Client connected: {sid}")
    await sio.emit("system_ready", {"status": "online"}, room=sid)

@sio.on("disconnect")
async def disconnect(sid):
    logger.info(f"Client disconnected: {sid}")

@sio.on("frame_request")
async def frame_request(sid, data):
    # Optionally clients can pull frames rather than wait for the broadcast loop
    if last_encoded_frame is not None:
        b64_frame = base64.b64encode(last_encoded_frame).decode('utf-8')
        await sio.emit("video_frame", {"image": f"data:image/jpeg;base64,{b64_frame}"}, room=sid)

# ── REST ENDPOINTS ────────────────────────────────────────────────────────────
@app.get("/health")
async def health_check():
    return {
        "status": "online",
        "fps": round(tracker.get_fps() if tracker else 0.0, 1),
        "resolution": f"{settings.CAMERA_WIDTH}x{settings.CAMERA_HEIGHT}"
    }

@app.post("/canvas/clear")
async def clear_canvas():
    if canvas:
        if hasattr(canvas, "clear_all"):
            canvas.clear_all()
        elif hasattr(canvas, "clear"):
            canvas.clear()
        logger.info("Canvas cleared.")
        return {"status": "success", "message": "Canvas cleared"}
    raise HTTPException(status_code=500, detail="Canvas not initialized")

@app.post("/canvas/undo")
async def undo_canvas():
    if canvas:
        if hasattr(canvas, "undo"):
            canvas.undo()
        logger.info("Canvas undo triggered.")
        return {"status": "success", "message": "Undo applied"}
    raise HTTPException(status_code=500, detail="Canvas not initialized")

@app.post("/canvas/export")
async def export_canvas():
    if not canvas:
        raise HTTPException(status_code=500, detail="Canvas not initialized")

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filepath = f"exports/phantom_hand_{timestamp}.png"

    def save_image():
        os.makedirs("exports", exist_ok=True)
        cv2.imwrite(filepath, canvas.canvas)

    await asyncio.to_thread(save_image)

    logger.info(f"Canvas exported to {filepath}")

    return {"status": "success", "filepath": filepath}

@app.get("/canvas/snapshot")
async def get_canvas_snapshot():
    if not canvas:
        raise HTTPException(status_code=500, detail="Canvas not initialized")

    def encode_image():
        return cv2.imencode('.png', canvas.canvas)

    success, encoded_img = await asyncio.to_thread(encode_image)
    if not success:
        raise HTTPException(status_code=500, detail="Failed to encode canvas")

    b64_img = base64.b64encode(encoded_img.tobytes()).decode('utf-8')
    return {"status": "success", "image": f"data:image/png;base64,{b64_img}"}

# Expose the ASGI app with Socket.IO wrapped
app = socket_app

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("backend.app:app", host=settings.HOST, port=settings.PORT, reload=False)
