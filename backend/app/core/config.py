from pydantic_settings import BaseSettings
from typing import List
import os


class Settings(BaseSettings):
    """Application configuration settings."""
    
    # App
    APP_NAME: str = "AI Voice Interview System"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = True
    
    # Database - defaults to SQLite for easy local dev
    DATABASE_URL: str = "sqlite+aiosqlite:///./interview.db"
    SATA_DATABASE_URL: str = ""
    
    # CORS
    CORS_ORIGINS: List[str] = ["http://localhost:3000", "http://localhost:5173"]
    
    # File Upload
    UPLOAD_DIR: str = "uploads"
    MAX_FILE_SIZE: int = 10 * 1024 * 1024  # 10MB
    ALLOWED_EXTENSIONS: List[str] = [".pdf", ".docx"]
    
    # AI Models
    HUGGINGFACE_MODEL: str = "google/flan-t5-base"
    WHISPER_MODEL: str = "base"
    TTS_MODEL: str = "tts_models/en/ljspeech/tacotron2-DDC"
    
    # Audio
    AUDIO_SAMPLE_RATE: int = 16000
    AUDIO_CHUNK_DURATION: float = 0.5  # seconds
    
    # Paths
    BASE_DIR: str = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    RECORDINGS_DIR: str = os.path.join(BASE_DIR, "recordings")
    MODELS_DIR: str = os.path.join(BASE_DIR, "models")
    
    class Config:
        env_file = ".env"
        case_sensitive = True


settings = Settings()

# Create directories if they don't exist
os.makedirs(settings.UPLOAD_DIR, exist_ok=True)
os.makedirs(settings.RECORDINGS_DIR, exist_ok=True)
os.makedirs(settings.MODELS_DIR, exist_ok=True)
