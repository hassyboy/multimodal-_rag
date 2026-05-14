"""
Recommendation Engine — Phase 4
Orchestrates: profile extraction → eligibility scoring → scheme ranking → context-aware retrieval.
"""
from typing import List, Tuple
from app.models.farmer_models import FarmerProfile, RecommendedScheme
from app.intelligence.farmer_profile_extractor import extract_farmer_profile
from app.intelligence.eligibility_engine import calculate_all_eligibilities
from app.intelligence.scheme_ranker import rank_schemes
from app.intelligence.context_builder import build_farmer_context_string
from app.rag.retriever import retrieve_documents
from app.core.logger import get_logger
from langchain_core.documents import Document

logger = get_logger(__name__)


def run_personalized_recommendation(
    question: str,
    session_profile: FarmerProfile = None,
) -> Tuple[FarmerProfile, List[RecommendedScheme], List[Document], str]:
    """
    Full personalized recommendation pipeline.

    Returns:
        - farmer_profile: extracted (or merged with session)
        - recommended_schemes: top-ranked eligible schemes
        - retrieved_docs: relevant documents from ChromaDB
        - farmer_context: formatted context string for LLM injection
    """
    # Step 1: Extract farmer profile from the question
    profile = extract_farmer_profile(question)

    # Step 2: Merge with existing session profile if available
    if session_profile:
        profile = merge_profiles(session_profile, profile)

    # Step 3: Run eligibility engine
    eligibility_results = calculate_all_eligibilities(profile)

    # Step 4: Rank and filter top schemes
    recommended_schemes = rank_schemes(profile, eligibility_results, top_k=5)

    # Step 5: Build a richer retrieval query including farmer context
    enriched_query = build_retrieval_query(question, profile)
    retrieved_docs = retrieve_documents(enriched_query)

    # Step 6: Build farmer context string for LLM
    farmer_context = build_farmer_context_string(profile, recommended_schemes)

    return profile, recommended_schemes, retrieved_docs, farmer_context


def merge_profiles(existing: FarmerProfile, new: FarmerProfile) -> FarmerProfile:
    """
    Merge a new extracted profile into the existing session profile.
    New values override existing only if they are non-None.
    This implements lightweight session memory.
    """
    return FarmerProfile(
        farmer_name=new.farmer_name or existing.farmer_name,
        district=new.district or existing.district,
        state=new.state or existing.state,
        land_size=new.land_size if new.land_size is not None else existing.land_size,
        crop_type=new.crop_type or existing.crop_type,
        irrigation_type=new.irrigation_type or existing.irrigation_type,
        income_category=new.income_category or existing.income_category,
        farmer_category=new.farmer_category or existing.farmer_category,
        gender=new.gender or existing.gender,
        farming_type=new.farming_type or existing.farming_type,
        language=new.language,
        extraction_confidence=max(new.extraction_confidence, existing.extraction_confidence),
    )


def build_retrieval_query(original_question: str, profile: FarmerProfile) -> str:
    """
    Build an enriched retrieval query by appending farmer context keywords.
    This improves ChromaDB semantic retrieval accuracy.
    """
    parts = [original_question]
    if profile.crop_type:
        parts.append(f"{profile.crop_type} scheme subsidy")
    if profile.district:
        parts.append(f"{profile.district} Karnataka scheme")
    if profile.land_size:
        parts.append(f"farmer {profile.land_size} acres eligibility")
    return " ".join(parts)
