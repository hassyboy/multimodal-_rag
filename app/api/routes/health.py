from fastapi import APIRouter
from app.models.response_models import HealthResponse

router = APIRouter()

@router.get("/health", response_model=HealthResponse)
async def health_check():
    """
    Health check endpoint to verify the service is running.
    """
    return HealthResponse(status="running")
