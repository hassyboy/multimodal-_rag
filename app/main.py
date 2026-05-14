import os
from pathlib import Path
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from app.api.routes import ask, health, schemes
from app.api.routes import personalized_ask
from app.api.routes import voice_ask
from app.api.routes import upload
from app.core.constants import APP_NAME, APP_VERSION, APP_DESCRIPTION

app = FastAPI(
    title=APP_NAME,
    version=APP_VERSION,
    description=APP_DESCRIPTION
)

# Configure CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Serve generated audio files at /audio/<filename>
AUDIO_DIR = Path(__file__).resolve().parents[1] / "storage" / "output_audio"
AUDIO_DIR.mkdir(parents=True, exist_ok=True)
app.mount("/audio", StaticFiles(directory=str(AUDIO_DIR)), name="audio")

# Include API Routers
app.include_router(health.router, tags=["Health"])
app.include_router(ask.router, tags=["QA"])
app.include_router(schemes.router, tags=["Schemes"])
app.include_router(personalized_ask.router, tags=["Personalized"])
app.include_router(voice_ask.router, tags=["Voice"])
app.include_router(upload.router, tags=["Upload"])
