import os
from typing import Dict
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    """
    PHANTOM HAND Configuration Kernel.
    Centralized authority for vision physics, gesture logic, and aesthetic tokens.
    """
    
    # ── NETWORK_&_SERVER ──────────────────────────────────────────────────────
    HOST: str = "0.0.0.0"
    PORT: int = 8080
    DEBUG: bool = False

    # ── CAMERA_PIPELINE ───────────────────────────────────────────────────────
    CAMERA_INDEX: int = 0
    CAMERA_WIDTH: int = 1280
    CAMERA_HEIGHT: int = 720
    TARGET_FPS: int = 60
    JPEG_QUALITY: int = 70  # Balanced for low-latency localhost streaming

    # ── VISION_ENGINE_PHYSICS ─────────────────────────────────────────────────
    # 1-Euro Filter Parameters (Temporal Stabilization)
    SMOOTHING_MIN_CUTOFF: float = 0.5  # Lower = smoother slow movements
    SMOOTHING_BETA: float = 0.1       # Higher = less lag during fast movements
    SMOOTHING_D_CUTOFF: float = 1.0    # Derivative cutoff
    
    # Ghost Hand (PhantomEngine) Persistence
    GHOST_MAX_FRAMES: int = 15         # How long to track after occlusion
    GHOST_VELOCITY_DAMPING: float = 0.92 # How fast the ghost slows down
    
    # ── GESTURE_INTELLIGENCE ──────────────────────────────────────────────────
    GESTURE_CONFIDENCE_THRESHOLD: float = 0.85
    GESTURE_VOTING_BUFFER_SIZE: int = 3  # Frames needed for a stable command
    PINCH_DISTANCE_THRESHOLD: float = 0.04 # Normalized distance for pinch-draw
    
    # ── DRAWING_AESTHETICS ────────────────────────────────────────────────────
    # Cold, Clinical Color Palette (HEX)
    COLOR_PALETTE: Dict[str, str] = {
        "CYAN": "#00E5FF",    # Main Accent
        "MAGENTA": "#FF00FF", # System Alert
        "GREEN": "#00FF41",   # Terminal Green
        "WHITE": "#F0F0F0",   # Data readout
        "RED": "#FF3D00"      # Error/Erase
    }
    
    DEFAULT_COLOR: str = "#00E5FF"
    DEFAULT_THICKNESS: int = 8
    NEON_GLOW_INTENSITY: float = 0.4
    MAX_LAYERS: int = 5

    # ── FILE_SYSTEM_PATHS ─────────────────────────────────────────────────────
    BASE_DIR: str = os.path.dirname(os.path.abspath(__file__))
    MODEL_PATH: str = os.path.join(BASE_DIR, "hand_landmarker.task")
    EXPORT_DIR: str = os.path.join(BASE_DIR, "exports")
    LOG_FILE: str = "phantom_hand.log"

    class Config:
        case_sensitive = True
        env_file = ".env"
        extra = "ignore"

settings = Settings()

# Ensure directories exist
os.makedirs(settings.EXPORT_DIR, exist_ok=True)
