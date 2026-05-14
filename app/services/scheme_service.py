from fastapi import HTTPException
from app.models.request_models import AskRequest
from app.models.response_models import AskResponse
from app.rag.rag_pipeline import run_rag_pipeline
from app.llm.response_formatter import format_ask_response
from app.utils.validators import validate_query
from app.utils.language_detector import detect_language
from app.core.logger import get_logger

logger = get_logger(__name__)

def handle_ask_query(request: AskRequest) -> AskResponse:
    """
    Handle the incoming question, validate it, detect language, 
    run it through the multilingual RAG pipeline, and format the response.
    """
    if not validate_query(request.question):
        raise HTTPException(status_code=400, detail="Invalid question format. Must be at least 3 characters long.")
    
    try:
        # Detect language
        detected_language = detect_language(request.question)
        logger.info(f"Processing query '{request.question}' detected as '{detected_language}'")
        
        # Run pipeline with language awareness
        answer, docs = run_rag_pipeline(request.question, language=detected_language)
        
        # Format response including language metadata
        response = format_ask_response(answer, docs, language=detected_language)
        return response
    except Exception as e:
        logger.error(f"Error handling query: {e}")
        raise HTTPException(status_code=500, detail="Internal server error while processing the question.")
