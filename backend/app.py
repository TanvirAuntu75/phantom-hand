import sys
import os
import asyncio
import base64
import cv2
import logging
import time
import psutil
from contextlib import asynccontextmanager
from threading import Thread, Event, Lock
from typing import Optional, Dict, Any, List

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
import socketio

# Ensure local imports work correctly
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'core'))

from backend.config import settings
from backend.core.hand_tracker import UltimateHandTracker
from backend.core.drawing_engine import DrawingEngine
from backend.core.command_router import CommandRouter
from backend.core.shape_recognizer import ShapeRecognizer
from backend.core.gesture_engine import GestureEngine
from backend.utils.exporter import Exporter

# ── LOGGING_CONFIGURATION ─────────────────────────────────────────────────────
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] [%(threadName)s] %(message)s",
    handlers=[
        logging.FileHandler("phantom_hand.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger("phantom_hand")

# ── CAMERA_STREAM_KERNEL ──────────────────────────────────────────────────────
class CameraStream:
    """Dedicated capture thread ensuring zero-buffer fresh frames."""
    def __init__(self):
        # Use MSMF (Media Foundation) for modern Windows compatibility
        self.stream = cv2.VideoCapture(settings.CAMERA_INDEX, cv2.CAP_ANY)
        self.stream.set(cv2.CAP_PROP_FRAME_WIDTH,  settings.CAMERA_WIDTH)
        self.stream.set(cv2.CAP_PROP_FRAME_HEIGHT, settings.CAMERA_HEIGHT)
        self.stream.set(cv2.CAP_PROP_BUFFERSIZE, 1)
        self.frame: Optional[np.ndarray] = None
        self.stopped = False
        self._lock = Lock()
        self.error_count = 0

    def start(self) -> "CameraStream":
        Thread(target=self._capture, daemon=True, name="Cam-Capture").start()
        return self

    def _capture(self) -> None:
        while not self.stopped:
            ret, frame = self.stream.read()
            if ret:
                with self._lock:
                    self.frame = cv2.flip(frame, 1)
                self.error_count = 0
            else:
                self.error_count += 1
                if self.error_count > 100:
                    logger.error("CAMERA_FAIL: Restarting stream...")
                    self.stream.release()
                    self.stream = cv2.VideoCapture(settings.CAMERA_INDEX, cv2.CAP_ANY)
                    self.error_count = 0
                time.sleep(0.01)

    def read(self) -> Optional[np.ndarray]:
        with self._lock:
            return self.frame.copy() if self.frame is not None else None

    def stop(self) -> None:
        self.stopped = True
        self.stream.release()

# ── GLOBAL_ENGINE_INSTANCES ───────────────────────────────────────────────────
tracker: Optional[UltimateHandTracker] = None
canvas:  Optional[DrawingEngine]       = None
cam:     Optional[CameraStream]        = None
router:  Optional[CommandRouter]       = None
recognizer: Optional[ShapeRecognizer]  = None
gesture_engine: Optional[GestureEngine] = None
exporter = Exporter()

# Thread-safe pipeline state
pipeline_event = Event()
_state_lock = Lock()
_last_jpeg: Optional[bytes] = None
_last_hand_data: List[Dict] = []
_pipeline_fps: float = 0.0
_frame_ready_event = asyncio.Event()

# ── LIFECYCLE_ORCHESTRATION ───────────────────────────────────────────────────
@asynccontextmanager
async def lifespan(app: FastAPI):
    global tracker, canvas, cam, router, recognizer, gesture_engine, _frame_ready_event
    
    logger.info("PHANTOM_HAND: INITIALIZING_SUBSYSTEMS...")
    _frame_ready_event = asyncio.Event()

    # 1. Hardware Initialization
    cam = CameraStream().start()

    # 2. Engine Initialization
    tracker = UltimateHandTracker(model_path=settings.MODEL_PATH)
    canvas = DrawingEngine(settings.CAMERA_WIDTH, settings.CAMERA_HEIGHT)
    recognizer = ShapeRecognizer()
    gesture_engine = GestureEngine()

    # 3. Router Integration (Injecting Socket.IO callback)
    def emit_event(event: str, data: Any):
        asyncio.run_coroutine_threadsafe(sio.emit(event, data), loop)

    loop = asyncio.get_running_loop()
    router = CommandRouter(canvas, recognizer, event_callback=emit_event)

    # 4. Pipeline Execution
    pipeline_event.clear()
    Thread(target=_vision_pipeline_loop, args=(loop,), daemon=True, name="Vision-Pipeline").start()
    asyncio.create_task(_broadcaster_task())

    logger.info(f"PHANTOM_HAND: SYSTEMS_ONLINE [PORT:{settings.PORT}]")
    yield

    # 5. Shutdown
    pipeline_event.set()
    if cam: cam.stop()
    logger.info("PHANTOM_HAND: SYSTEMS_OFFLINE")

# ── APP_CONFIGURATION ─────────────────────────────────────────────────────────
app = FastAPI(title="PHANTOM HAND Backend", lifespan=lifespan)
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_credentials=False, allow_methods=["*"], allow_headers=["*"])

sio = socketio.AsyncServer(async_mode='asgi', cors_allowed_origins='*', max_http_buffer_size=5*1024*1024)
socket_app = socketio.ASGIApp(sio, other_asgi_app=app)

# ── VISION_PIPELINE ───────────────────────────────────────────────────────────
def _vision_pipeline_loop(loop: asyncio.AbstractEventLoop) -> None:
    """Core CV loop running at camera native refresh rate."""
    global _last_jpeg, _last_hand_data, _pipeline_fps
    
    frame_times = []
    jpeg_params = [int(cv2.IMWRITE_JPEG_QUALITY), 70]
    
    logger.info("PIPELINE: KERNEL_START")
    
    while not pipeline_event.is_set():
        t0 = time.perf_counter()
        
        frame = cam.read()
        if frame is None:
            time.sleep(0.005)
            continue

        # 1. AI Hand Tracking
        all_hands = tracker.process_frame(frame)
        
        current_frame_data = []
        
        # 2. Intelligence & Routing
        for hand_id, (landmarks, is_ghost) in all_hands.items():
            # Classification
            gest_res = gesture_engine.process(landmarks)
            
            # Execution
            router.route(hand_id, gest_res, landmarks)
            
            current_frame_data.append({
                "id": hand_id,
                "is_ghost": is_ghost,
                "gesture": gest_res.gesture,
                "confidence": gest_res.confidence,
                "landmarks": landmarks
            })

        # 3. Compositing
        rendered = canvas.render(frame)
        
        # DOWN-SCALE for transmission (reduces data load by 75%)
        # AI still tracks at full res, but HUD stream is optimized for zero-lag
        stream_view = cv2.resize(rendered, (640, 360), interpolation=cv2.INTER_AREA)
        
        ok, encoded = cv2.imencode('.jpg', stream_view, [int(cv2.IMWRITE_JPEG_QUALITY), 50])
        
        if ok:
            with _state_lock:
                _last_jpeg = encoded.tobytes()
                _last_hand_data = current_frame_data
            
            # Signal the broadcaster
            loop.call_soon_threadsafe(_frame_ready_event.set)

        # 4. Performance Telemetry
        elapsed = time.perf_counter() - t0
        frame_times.append(elapsed)
        if len(frame_times) > 30: frame_times.pop(0)
        _pipeline_fps = 1.0 / (sum(frame_times)/len(frame_times))

# ── DATA_BROADCASTER ──────────────────────────────────────────────────────────
async def _broadcaster_task() -> None:
    """Asynchronous task that pushes frames to all connected clients."""
    while True:
        await _frame_ready_event.wait()
        _frame_ready_event.clear()
        
        with _state_lock:
            if _last_jpeg is None: continue
            jpeg_bytes = _last_jpeg
            hand_data = _last_hand_data
            fps = _pipeline_fps

        b64_frame = base64.b64encode(jpeg_bytes).decode('utf-8')

        # ── SYSTEM_STATE (consumed by HUD toolbar) ────────────────────────
        system_state = {
            "brushMode": canvas.active_brush,
            "activeLayer": canvas.active_layer,
            "color": canvas.current_color,
            "mode_3d": canvas.mode_3d,
            "colorIndex": 1,
            "totalColors": 7,
            "voice_active": False,
        }

        # ── PERFORMANCE_TELEMETRY (consumed by SystemPanel HUD) ────────────
        perf_stats = {
            "fps": round(fps, 1),
            "latency": {
                "tracking": round((time.perf_counter() - _last_t0) * 1000, 1) if '_last_t0' in globals() else 0,
                "total": round(1000.0 / fps, 1) if fps > 0 else 0,
            },
            "system": {
                "cpu": psutil.cpu_percent(interval=None),
                "mem": psutil.virtual_memory().percent,
            }
        }

        # ── UNIFIED_BROADCAST ─────────────────────────────────────────────
        # By sending the image AND data in the same packet, we guarantee
        # frame-perfect synchronization in the React frontend.
        unified_payload = {
            "image": f"data:image/jpeg;base64,{b64_frame}",
            "hands": hand_data,
            "systemState": system_state,
            "stats": perf_stats
        }
        
        await asyncio.gather(
            sio.emit("sync_frame", unified_payload),
            # Keep legacy events for backward compatibility while we transition
            sio.emit("video_frame", {"image": unified_payload["image"]}),
            sio.emit("hand_data", {"hands": hand_data, "systemState": system_state}),
            sio.emit("performance_stats", perf_stats),
            return_exceptions=True
        )

# ── API_ENDPOINTS ─────────────────────────────────────────────────────────────
@app.get("/health")
async def health():
    return {"status": "online", "fps": round(_pipeline_fps, 1)}

@app.post("/canvas/clear")
async def clear_canvas():
    if canvas:
        canvas.clear()
        logger.info("Canvas cleared.")
        return {"status": "success", "message": "Canvas cleared"}
    raise HTTPException(status_code=500, detail="Canvas not initialized")

@app.post("/canvas/undo")
async def undo_canvas():
    if canvas:
        canvas.undo()
        logger.info("Canvas undo triggered.")
        return {"status": "success", "message": "Undo applied"}
    raise HTTPException(status_code=500, detail="Canvas not initialized")

@app.post("/export/png")
async def export_png():
    if not canvas: raise HTTPException(status_code=500, detail="Canvas not initialized")
    path, filename = await asyncio.to_thread(exporter.export_png, canvas)
    return {"status": "success", "path": path, "filename": filename}


@app.post("/export/svg")
async def export_svg():
    if not canvas: raise HTTPException(status_code=500, detail="Canvas not initialized")
    path, filename = await asyncio.to_thread(exporter.export_svg, canvas)
    return {"status": "success", "path": path, "filename": filename}

@app.post("/export/gif")
async def export_gif():
    if not canvas: raise HTTPException(status_code=500, detail="Canvas not initialized")
    path, filename = await asyncio.to_thread(exporter.export_gif, canvas)
    return {"status": "success", "path": path, "filename": filename}

@app.post("/export/mp4")
async def export_mp4():
    if not canvas: raise HTTPException(status_code=500, detail="Canvas not initialized")
    path, filename = await asyncio.to_thread(exporter.export_mp4, canvas)
    return {"status": "success", "path": path, "filename": filename}

@app.get("/export/{filename}")
async def download_export(filename: str):
    filepath = os.path.join(exporter.export_dir, os.path.basename(filename))
    if os.path.exists(filepath):
        return FileResponse(filepath, media_type='application/octet-stream', filename=filename)
    raise HTTPException(status_code=404, detail="File not found")

# ── ASGI_ENTRY_POINT ──────────────────────────────────────────────────────────
app = socket_app

if __name__ == "__main__":
    import uvicorn
    # Use the string "backend.app:app" to allow uvicorn to find the app object correctly
    uvicorn.run("backend.app:app", host=settings.HOST, port=settings.PORT, reload=False)
