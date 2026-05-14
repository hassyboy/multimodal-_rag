"""
Personalized Service — Phase 4
Business logic layer that orchestrates the full personalized recommendation pipeline.
"""
from fastapi import HTTPException
from app.models.personalized_models import PersonalizedAskRequest, PersonalizedAskResponse
from app.models.response_models import SourceItem
from app.intelligence.recommendation_engine import run_personalized_recommendation
from app.intelligence.session_store import get_session_profile, save_session_profile
from app.rag.prompt_builder import get_personalized_prompt
from app.llm.llm_service import generate_response
from app.utils.validators import validate_query
from app.core.logger import get_logger

logger = get_logger(__name__)


def handle_personalized_ask(request: PersonalizedAskRequest) -> PersonalizedAskResponse:
    """
    Full personalized pipeline:
      1. Validate input
      2. Load session memory (if session_id provided)
      3. Extract farmer profile
      4. Calculate eligibility & rank schemes
      5. Retrieve relevant documents
      6. Build personalized LLM prompt
      7. Generate multilingual response
      8. Save updated session profile
    """
    if not validate_query(request.question):
        raise HTTPException(status_code=400, detail="Question must be at least 3 characters.")

    try:
        # Step 1: Load existing session profile if any
        session_profile = None
        if request.session_id:
            session_profile = get_session_profile(request.session_id)
            if session_profile:
                logger.info(f"Restored session profile for session_id={request.session_id}")

        # Step 2: Run recommendation pipeline
        profile, schemes, docs, farmer_context = run_personalized_recommendation(
            question=request.question,
            session_profile=session_profile,
        )

        # Step 3: Save updated profile back to session
        if request.session_id:
            save_session_profile(request.session_id, profile)

        # Step 4: Build context from retrieved docs
        retrieved_context = "\n\n".join([doc.page_content for doc in docs])

        # Step 5: Build personalized prompt
        prompt_template = get_personalized_prompt()
        prompt = prompt_template.format(
            farmer_context=farmer_context,
            context=retrieved_context,
            question=request.question,
            language=profile.language,
        )

        # Step 6: Generate LLM response
        answer = generate_response(prompt)

        # Step 7: Format sources
        sources = [
            SourceItem(content=doc.page_content, metadata=doc.metadata)
            for doc in docs
        ]

        return PersonalizedAskResponse(
            language=profile.language,
            farmer_profile=profile,
            recommended_schemes=schemes,
            answer=answer,
            sources=sources,
        )

    except Exception as e:
        logger.error(f"Error in personalized pipeline: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Internal error: {str(e)}")
