"""
Eligibility Engine — Phase 4
Rule-based scoring system for calculating how eligible a farmer is for each scheme.
Fully modular — designed for future ML upgrade.
"""
from typing import List
from app.models.farmer_models import FarmerProfile, EligibilityResult
from app.core.logger import get_logger

logger = get_logger(__name__)

# -------------------------------------------------------------------
# SCHEME RULES REGISTRY
# Each entry defines matching criteria and max points per field.
# -------------------------------------------------------------------
SCHEME_RULES: dict = {
    "PM-KISAN": {
        "description": "Rs. 6000/year income support for all farmer families",
        "crop_bonus": [],                  # applies to all crops
        "land_max_acres": 10.0,            # all small/marginal (no strict upper limit here)
        "land_points": 30,
        "crop_points": 10,
        "irrigation_bonus": [],
        "irrigation_points": 10,
        "state_bonus": [],                 # central scheme
        "state_points": 0,
        "base_score": 50,                  # applicable to everyone
    },
    "Akki Bele Yojane": {
        "description": "Free seeds and pesticide discount for rice farmers in Mandya/Mysore",
        "crop_bonus": ["rice"],
        "land_max_acres": 10.0,
        "land_points": 20,
        "crop_points": 40,
        "district_bonus": ["Mandya", "Mysore"],
        "district_points": 30,
        "base_score": 10,
    },
    "Drip Irrigation Subsidy": {
        "description": "90% subsidy for installing drip irrigation system",
        "crop_bonus": ["sugarcane", "cotton", "banana", "tomato", "onion"],
        "land_max_acres": 15.0,
        "land_points": 20,
        "crop_points": 20,
        "irrigation_bonus": ["drip"],
        "irrigation_points": 40,
        "base_score": 20,
    },
    "Krishi Vikas Yojana": {
        "description": "50% subsidy on fertilizers + Rs 5000/acre for rice farmers in Karnataka",
        "crop_bonus": ["rice", "wheat", "maize"],
        "land_max_acres": 20.0,
        "land_points": 20,
        "crop_points": 35,
        "state_bonus": ["Karnataka"],
        "state_points": 25,
        "base_score": 20,
    },
    "Solar Pump Subsidy": {
        "description": "Subsidy for solar-powered irrigation pumps",
        "crop_bonus": [],
        "land_max_acres": 10.0,
        "land_points": 25,
        "crop_points": 0,
        "irrigation_bonus": ["borewell", "well"],
        "irrigation_points": 35,
        "base_score": 30,
    },
    "Organic Farming Scheme": {
        "description": "Financial support and certification for organic farmers",
        "crop_bonus": ["ragi", "jowar", "groundnut"],
        "land_max_acres": 5.0,
        "land_points": 20,
        "crop_points": 20,
        "farming_type_bonus": ["organic"],
        "farming_type_points": 50,
        "base_score": 10,
    },
    "PM Fasal Bima Yojana": {
        "description": "Crop insurance for all farmers against natural disasters",
        "crop_bonus": [],
        "land_max_acres": 50.0,
        "land_points": 10,
        "crop_points": 30,
        "base_score": 50,
    },
    "Kisan Credit Card": {
        "description": "Low-interest credit line for agricultural inputs",
        "crop_bonus": [],
        "land_max_acres": 50.0,
        "land_points": 20,
        "crop_points": 10,
        "base_score": 60,
    },
    "Tractor Loan Scheme": {
        "description": "4% interest rate loan for purchasing tractor",
        "crop_bonus": [],
        "land_min_acres": 5.0,            # minimum land requirement
        "land_max_acres": 100.0,
        "land_points": 40,
        "crop_points": 0,
        "base_score": 30,
    },
}


def score_scheme(profile: FarmerProfile, scheme_name: str, rules: dict) -> EligibilityResult:
    """Calculate eligibility score for a single scheme given the farmer profile."""
    score = rules.get("base_score", 0)
    reasons = []
    disqualifications = []

    # --- Land size scoring ---
    land_max = rules.get("land_max_acres")
    land_min = rules.get("land_min_acres", 0.0)
    land_pts = rules.get("land_points", 0)

    if profile.land_size is not None:
        if profile.land_size < land_min:
            penalty = land_pts
            score -= penalty
            disqualifications.append(
                f"Minimum land required is {land_min} acres (you have {profile.land_size} acres)"
            )
        elif profile.land_size <= (land_max or 999):
            score += land_pts
            reasons.append(f"Land size ({profile.land_size} acres) qualifies")
        else:
            score -= land_pts
            disqualifications.append(f"Land size exceeds limit ({land_max} acres)")

    # --- Crop type scoring ---
    crop_bonus = rules.get("crop_bonus", [])
    crop_pts = rules.get("crop_points", 0)
    if profile.crop_type:
        if not crop_bonus or profile.crop_type.lower() in [c.lower() for c in crop_bonus]:
            score += crop_pts
            if crop_bonus:
                reasons.append(f"{profile.crop_type.capitalize()} is a priority crop for this scheme")
            else:
                reasons.append("Applicable to all crops")
        else:
            score -= crop_pts // 2  # partial deduction

    # --- Irrigation type scoring ---
    irrigation_bonus = rules.get("irrigation_bonus", [])
    irrigation_pts = rules.get("irrigation_points", 0)
    if profile.irrigation_type and irrigation_bonus:
        if profile.irrigation_type.lower() in [i.lower() for i in irrigation_bonus]:
            score += irrigation_pts
            reasons.append(f"Irrigation type ({profile.irrigation_type}) matches scheme requirements")

    # --- District scoring ---
    district_bonus = rules.get("district_bonus", [])
    district_pts = rules.get("district_points", 0)
    if profile.district and district_bonus:
        if profile.district in district_bonus:
            score += district_pts
            reasons.append(f"District ({profile.district}) is a priority area for this scheme")

    # --- State scoring ---
    state_bonus = rules.get("state_bonus", [])
    state_pts = rules.get("state_points", 0)
    if profile.state and state_bonus:
        if profile.state in state_bonus:
            score += state_pts
            reasons.append(f"State ({profile.state}) qualifies for this scheme")

    # --- Farming type scoring ---
    farming_type_bonus = rules.get("farming_type_bonus", [])
    farming_type_pts = rules.get("farming_type_points", 0)
    if profile.farming_type and farming_type_bonus:
        if profile.farming_type.lower() in [f.lower() for f in farming_type_bonus]:
            score += farming_type_pts
            reasons.append(f"Organic farming qualification adds priority")

    # Clamp score to 0-100
    score = max(0, min(100, score))

    confidence = min(1.0, profile.extraction_confidence + 0.3)  # boost if profile is rich

    return EligibilityResult(
        scheme_name=scheme_name,
        eligibility_score=round(score, 1),
        confidence=round(confidence, 2),
        matching_reasons=reasons,
        disqualifying_reasons=disqualifications,
    )


def calculate_all_eligibilities(profile: FarmerProfile) -> List[EligibilityResult]:
    """
    Run the eligibility engine for all known schemes and return sorted results.
    """
    logger.info(f"Running eligibility engine for profile: district={profile.district}, crop={profile.crop_type}")
    results = []
    for scheme_name, rules in SCHEME_RULES.items():
        result = score_scheme(profile, scheme_name, rules)
        results.append(result)

    # Sort by score descending
    results.sort(key=lambda r: r.eligibility_score, reverse=True)
    return results
