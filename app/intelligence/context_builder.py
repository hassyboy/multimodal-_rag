"""
Context Builder — Phase 4
Builds a human-readable farmer context string to inject into the LLM prompt.
Supports multilingual context formatting.
"""
from app.models.farmer_models import FarmerProfile, RecommendedScheme
from typing import List


def build_farmer_context_string(profile: FarmerProfile, schemes: List[RecommendedScheme]) -> str:
    """
    Build a context paragraph summarizing farmer profile and top matching schemes.
    This is injected into the LLM prompt alongside the retrieved document chunks.
    """
    lines = ["=== FARMER PROFILE (AUTO-EXTRACTED) ==="]

    if profile.district:
        lines.append(f"District: {profile.district}, {profile.state}")
    if profile.land_size:
        lines.append(f"Land Size: {profile.land_size} acres")
    if profile.crop_type:
        lines.append(f"Primary Crop: {profile.crop_type.capitalize()}")
    if profile.irrigation_type:
        lines.append(f"Irrigation: {profile.irrigation_type}")
    if profile.income_category:
        lines.append(f"Farmer Category: {profile.income_category}")
    if profile.farming_type:
        lines.append(f"Farming Type: {profile.farming_type}")
    if profile.gender:
        lines.append(f"Gender: {profile.gender}")

    if schemes:
        lines.append("\n=== TOP MATCHING SCHEMES (RANKED BY ELIGIBILITY) ===")
        for scheme in schemes:
            lines.append(
                f"• {scheme.scheme_name} — Score: {scheme.eligibility_score}/100\n"
                f"  Reason: {scheme.reason}\n"
                f"  Benefit: {scheme.benefit_summary}"
            )

    return "\n".join(lines)
