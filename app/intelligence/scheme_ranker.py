"""
Scheme Ranker — Phase 4
Applies multi-factor ranking to produce the final ordered list of recommended schemes.
Modular — each factor can be individually tuned or replaced with ML in the future.
"""
from typing import List
from app.models.farmer_models import FarmerProfile, EligibilityResult, RecommendedScheme
from app.intelligence.eligibility_engine import SCHEME_RULES
from app.core.logger import get_logger

logger = get_logger(__name__)

SCORE_THRESHOLD = 40.0  # Only recommend schemes with at least this score


def rank_schemes(
    profile: FarmerProfile,
    eligibility_results: List[EligibilityResult],
    top_k: int = 5,
) -> List[RecommendedScheme]:
    """
    Convert raw eligibility results into a ranked, human-readable recommendation list.
    Filters out low-scoring schemes and attaches descriptions.
    """
    logger.info(f"Ranking {len(eligibility_results)} schemes for farmer profile")

    recommended = []
    for result in eligibility_results:
        if result.eligibility_score < SCORE_THRESHOLD:
            continue  # Filter below threshold

        # Build primary reason string from top matching reasons
        if result.matching_reasons:
            reason = "; ".join(result.matching_reasons[:2])
        elif result.disqualifying_reasons:
            reason = f"Partially eligible — {result.disqualifying_reasons[0]}"
        else:
            reason = "Generally applicable scheme"

        # Get benefit summary from rules registry
        rules = SCHEME_RULES.get(result.scheme_name, {})
        benefit_summary = rules.get("description", "")

        recommended.append(
            RecommendedScheme(
                scheme_name=result.scheme_name,
                eligibility_score=result.eligibility_score,
                reason=reason,
                benefit_summary=benefit_summary,
            )
        )

    # Already sorted by eligibility_engine, slice top_k
    top_schemes = recommended[:top_k]
    logger.info(f"Top {len(top_schemes)} schemes selected after ranking")
    return top_schemes
