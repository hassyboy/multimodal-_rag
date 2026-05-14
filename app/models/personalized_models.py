from typing import Optional, List
from pydantic import BaseModel, Field
from app.models.response_models import AskResponse, SourceItem
from app.models.farmer_models import FarmerProfile, RecommendedScheme


class PersonalizedAskRequest(BaseModel):
    """Request model for /personalized-ask endpoint."""
    question: str = Field(..., description="Farmer's question (Kannada, English, or mixed)")
    session_id: Optional[str] = Field(None, description="Optional session ID for context memory")


class PersonalizedAskResponse(BaseModel):
    """Full personalized response including farmer profile and scheme recommendations."""
    language: str
    farmer_profile: FarmerProfile
    recommended_schemes: List[RecommendedScheme]
    answer: str
    sources: List[SourceItem] = Field(default_factory=list)
