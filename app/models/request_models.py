from pydantic import BaseModel, Field

class AskRequest(BaseModel):
    """Request model for the /ask endpoint."""
    question: str = Field(..., description="The user's question about agriculture schemes")
