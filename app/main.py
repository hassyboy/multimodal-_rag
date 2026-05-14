from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api.routes import ask, health, schemes
from app.api.routes import personalized_ask
from app.core.constants import APP_NAME, APP_VERSION, APP_DESCRIPTION

app = FastAPI(
    title=APP_NAME,
    version=APP_VERSION,
    description=APP_DESCRIPTION
)

# Configure CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], # In production, configure specific origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include API Routers
app.include_router(health.router, tags=["Health"])
app.include_router(ask.router, tags=["QA"])
app.include_router(schemes.router, tags=["Schemes"])
app.include_router(personalized_ask.router, tags=["Personalized"])
