import os
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    """
    Application configuration settings, loaded from environment variables.
    All variables must be upper-case in the environment.
    """
    HOST: str = os.getenv("HOST", "0.0.0.0")
    PORT: int = int(os.getenv("PORT", "8000"))

    CAMERA_INDEX: int = int(os.getenv("CAMERA_INDEX", "0"))
    CAMERA_WIDTH: int = int(os.getenv("CAMERA_WIDTH", "1280"))
    CAMERA_HEIGHT: int = int(os.getenv("CAMERA_HEIGHT", "720"))

    TARGET_FPS: int = int(os.getenv("TARGET_FPS", "30"))
    JPEG_QUALITY: int = int(os.getenv("JPEG_QUALITY", "82"))

settings = Settings()
