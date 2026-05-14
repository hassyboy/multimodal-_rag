from typing import Optional
from pydantic import BaseModel, Field

class FarmerProfile(BaseModel):
    """Structured model representing an extracted farmer profile from their query."""
    farmer_name: Optional[str] = Field(None, description="Farmer's name if mentioned")
    district: Optional[str] = Field(None, description="District the farmer is in")
    state: Optional[str] = Field(None, description="State, defaults to Karnataka")
    land_size: Optional[float] = Field(None, description="Land size in acres")
    crop_type: Optional[str] = Field(None, description="Primary crop being cultivated")
    irrigation_type: Optional[str] = Field(None, description="Type of irrigation (drip, bore, rain-fed)")
    income_category: Optional[str] = Field(None, description="Income category (BPL, small, marginal, large)")
    farmer_category: Optional[str] = Field(None, description="Farmer category (small, marginal, large)")
    gender: Optional[str] = Field(None, description="Farmer gender if mentioned")
    farming_type: Optional[str] = Field(None, description="Organic, conventional, mixed")
    language: str = Field("english", description="Detected language of the query")
    extraction_confidence: float = Field(0.0, description="Confidence of profile extraction (0-1)")

class EligibilityResult(BaseModel):
    """Result of eligibility scoring for a specific scheme."""
    scheme_name: str
    eligibility_score: float = Field(..., description="Eligibility score 0-100")
    confidence: float = Field(..., description="Confidence in this score 0-1")
    matching_reasons: list[str] = Field(default_factory=list)
    disqualifying_reasons: list[str] = Field(default_factory=list)

class RecommendedScheme(BaseModel):
    """A single recommended scheme with context."""
    scheme_name: str
    eligibility_score: float
    reason: str
    benefit_summary: Optional[str] = None
    how_to_apply: Optional[str] = None
