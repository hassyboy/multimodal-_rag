from typing import List, Dict, Any, Optional
from pydantic import BaseModel, Field

class SourceItem(BaseModel):
    """Model representing a source document reference."""
    content: str
    metadata: Dict[str, Any]

class AskResponse(BaseModel):
    """Response model for the /ask endpoint."""
    language: str = Field(..., description="The detected language of the response")
    answer: str = Field(..., description="The generated answer from the LLM")
    sources: List[SourceItem] = Field(default_factory=list, description="List of source documents used to generate the answer")

class HealthResponse(BaseModel):
    """Response model for the /health endpoint."""
    status: str = Field(..., description="The health status of the service")
