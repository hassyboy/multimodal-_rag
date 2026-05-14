"""
POST /personalized-ask
Personalized scheme recommendation API endpoint.
"""
from fastapi import APIRouter
from app.models.personalized_models import PersonalizedAskRequest, PersonalizedAskResponse
from app.services.personalized_service import handle_personalized_ask

router = APIRouter()


@router.post("/personalized-ask", response_model=PersonalizedAskResponse)
async def personalized_ask(request: PersonalizedAskRequest):
    """
    Personalized scheme recommendation endpoint.
    
    Accepts a farmer's natural language question (Kannada / English / mixed),
    automatically extracts farmer profile, ranks eligible schemes, and returns
    a context-aware, multilingual response.
    """
    return handle_personalized_ask(request)
