from fastapi import APIRouter
from app.models.request_models import AskRequest
from app.models.response_models import AskResponse
from app.services.scheme_service import handle_ask_query

router = APIRouter()

@router.post("/ask", response_model=AskResponse)
async def ask_question(request: AskRequest):
    """
    Accepts a user question regarding agriculture schemes and returns a generated answer
    based on retrieved context from the government scheme documents.
    """
    # Processing is handled synchronously in this phase since RAG pipeline is synchronous
    return handle_ask_query(request)
