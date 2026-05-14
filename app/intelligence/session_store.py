"""
In-memory session store for farmer context.
Stores FarmerProfile per session_id so follow-up questions retain context.
No database required — Phase 4 lightweight implementation.
"""
from typing import Dict, Optional
from app.models.farmer_models import FarmerProfile

# Simple in-memory store: {session_id: FarmerProfile}
_session_store: Dict[str, FarmerProfile] = {}


def get_session_profile(session_id: str) -> Optional[FarmerProfile]:
    """Retrieve stored farmer profile for a session."""
    return _session_store.get(session_id)


def save_session_profile(session_id: str, profile: FarmerProfile) -> None:
    """Save or update the farmer profile for a session."""
    _session_store[session_id] = profile


def clear_session(session_id: str) -> None:
    """Clear the session context for a given session."""
    _session_store.pop(session_id, None)
