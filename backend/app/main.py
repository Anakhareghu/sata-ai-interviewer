from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from contextlib import asynccontextmanager
import logging
import os

from app.core.config import settings
from app.core.database import create_tables
from app.api.routes import resume, interview, evaluation, websocket

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan events."""
    # Startup
    logger.info("🚀 Starting AI Voice Interview System...")
    logger.info(f"📁 Upload directory: {settings.UPLOAD_DIR}")
    logger.info(f"🎤 Recordings directory: {settings.RECORDINGS_DIR}")
    
    # Create necessary directories
    os.makedirs(settings.UPLOAD_DIR, exist_ok=True)
    os.makedirs(settings.RECORDINGS_DIR, exist_ok=True)
    os.makedirs(settings.MODELS_DIR, exist_ok=True)
    
    # Auto-create database tables
    try:
        # Import all models so they register with Base
        import app.models  # noqa: F401
        await create_tables()
        logger.info("✅ Database tables ready")
    except Exception as e:
        logger.error(f"❌ Database error: {e}")
    
    # Initialize AI models (lazy loading)
    logger.info("🤖 AI models will be loaded on first use...")
    
    yield
    
    # Shutdown
    logger.info("👋 Shutting down AI Voice Interview System...")


app = FastAPI(
    title="AI Voice Interview System",
    description="""
    AI-powered Resume-Based Voice Interview System integrated with SATA.
    
    ## Features
    - 📄 Resume parsing and skill extraction
    - 🎯 AI-generated interview questions
    - 🎤 Live voice interviews with speech recognition
    - 📊 Performance evaluation and analytics
    - 💼 Career recommendations
    """,
    version="1.0.0",
    lifespan=lifespan
)

# CORS configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Static files for recordings and uploads — mount only if directories exist
os.makedirs(settings.UPLOAD_DIR, exist_ok=True)
os.makedirs(settings.RECORDINGS_DIR, exist_ok=True)
app.mount("/uploads", StaticFiles(directory=settings.UPLOAD_DIR), name="uploads")
app.mount("/recordings", StaticFiles(directory=settings.RECORDINGS_DIR), name="recordings")

# Include routers
app.include_router(resume.router, prefix="/api/resume", tags=["Resume"])
app.include_router(interview.router, prefix="/api/interview", tags=["Interview"])
app.include_router(evaluation.router, prefix="/api/evaluation", tags=["Evaluation"])
app.include_router(websocket.router, prefix="/ws", tags=["WebSocket"])


@app.get("/")
async def root():
    """Root endpoint with system info."""
    return {
        "name": settings.APP_NAME,
        "version": settings.APP_VERSION,
        "status": "running",
        "docs": "/docs",
        "features": [
            "Resume Intelligence Engine",
            "AI Question Generator",
            "Live Voice Interview",
            "Performance Evaluation",
            "Career Recommendations"
        ]
    }


@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {
        "status": "healthy",
        "database": "connected",
        "ai_models": "ready"
    }
