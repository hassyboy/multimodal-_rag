"""
Farmer Profile Extractor — Phase 4
Extracts structured farmer profile from natural language queries.
Supports Kannada, English, and mixed (Kanglish) input.
Uses regex patterns and heuristics — no cloud API dependency.
"""
import re
from typing import Optional
from app.models.farmer_models import FarmerProfile
from app.utils.language_detector import detect_language
from app.core.logger import get_logger

logger = get_logger(__name__)

# -------------------------------------------------------------------
# DISTRICT MAPPINGS
# Covers Karnataka districts in English and Kannada transliteration
# -------------------------------------------------------------------
DISTRICT_KEYWORDS = {
    "mandya": "Mandya", "ಮಂಡ್ಯ": "Mandya",
    "mysore": "Mysore", "mysuru": "Mysore", "ಮೈಸೂರು": "Mysore",
    "bangalore": "Bangalore", "bengaluru": "Bangalore", "ಬೆಂಗಳೂರು": "Bangalore",
    "hassan": "Hassan", "ಹಾಸನ": "Hassan",
    "tumkur": "Tumkur", "tumakuru": "Tumkur", "ತುಮಕೂರು": "Tumkur",
    "davangere": "Davangere", "ದಾವಣಗೆರೆ": "Davangere",
    "bellary": "Bellary", "ballari": "Bellary", "ಬಳ್ಳಾರಿ": "Bellary",
    "bidar": "Bidar", "ಬೀದರ್": "Bidar",
    "bagalkot": "Bagalkot", "ಬಾಗಲಕೋಟೆ": "Bagalkot",
    "belgaum": "Belgaum", "belagavi": "Belgaum", "ಬೆಳಗಾವಿ": "Belgaum",
    "dharwad": "Dharwad", "ಧಾರವಾಡ": "Dharwad",
    "gadag": "Gadag", "ಗದಗ": "Gadag",
    "gulbarga": "Gulbarga", "kalaburagi": "Gulbarga", "ಕಲಬುರಗಿ": "Gulbarga",
    "raichur": "Raichur", "ರಾಯಚೂರು": "Raichur",
    "koppal": "Koppal", "ಕೊಪ್ಪಳ": "Koppal",
    "shimoga": "Shimoga", "shivamogga": "Shimoga", "ಶಿವಮೊಗ್ಗ": "Shimoga",
    "chikmagalur": "Chikmagalur", "ಚಿಕ್ಕಮಗಳೂರು": "Chikmagalur",
    "kodagu": "Kodagu", "coorg": "Kodagu", "ಕೊಡಗು": "Kodagu",
    "udupi": "Udupi", "ಉಡುಪಿ": "Udupi",
    "dakshina kannada": "Dakshina Kannada", "mangalore": "Dakshina Kannada",
    "uttara kannada": "Uttara Kannada",
    "chitradurga": "Chitradurga", "ಚಿತ್ರದುರ್ಗ": "Chitradurga",
    "kolar": "Kolar", "ಕೋಲಾರ": "Kolar",
    "chikkaballapura": "Chikkaballapura",
    "ramanagara": "Ramanagara", "ರಾಮನಗರ": "Ramanagara",
    "chamarajanagar": "Chamarajanagar", "ಚಾಮರಾಜನಗರ": "Chamarajanagar",
    "yadgir": "Yadgir", "ಯಾದಗಿರಿ": "Yadgir",
    "vijayanagara": "Vijayanagara",
}

# -------------------------------------------------------------------
# CROP MAPPINGS (English + Kannada)
# -------------------------------------------------------------------
CROP_KEYWORDS = {
    "rice": "rice", "paddy": "rice", "akki": "rice", "ಅಕ್ಕಿ": "rice", "ಭತ್ತ": "rice",
    "wheat": "wheat", "godhi": "wheat", "ಗೋಧಿ": "wheat",
    "sugarcane": "sugarcane", "kabbu": "sugarcane", "ಕಬ್ಬು": "sugarcane",
    "maize": "maize", "corn": "maize", "makka": "maize", "ಮೆಕ್ಕೆ": "maize",
    "cotton": "cotton", "ಹತ್ತಿ": "cotton",
    "tomato": "tomato", "ಟೊಮ್ಯಾಟೊ": "tomato",
    "ragi": "ragi", "finger millet": "ragi", "ರಾಗಿ": "ragi",
    "jowar": "jowar", "sorghum": "jowar", "ಜೋಳ": "jowar",
    "groundnut": "groundnut", "peanut": "groundnut", "ಕಡಲೆ": "groundnut",
    "areca": "arecanut", "arecanut": "arecanut", "supari": "arecanut", "ಅಡಿಕೆ": "arecanut",
    "coconut": "coconut", "ತೆಂಗಿನ": "coconut",
    "onion": "onion", "eerulli": "onion", "ಈರುಳ್ಳಿ": "onion",
    "chilli": "chilli", "mensu": "chilli", "ಮೆಣಸು": "chilli",
    "banana": "banana", "bale": "banana", "ಬಾಳೆ": "banana",
    "mango": "mango", "mavina": "mango", "ಮಾವಿನ": "mango",
    "soybean": "soybean", "soya": "soybean",
    "sunflower": "sunflower", "ಸೂರ್ಯಕಾಂತಿ": "sunflower",
}

# -------------------------------------------------------------------
# IRRIGATION TYPE KEYWORDS
# -------------------------------------------------------------------
IRRIGATION_KEYWORDS = {
    "drip": "drip", "drip irrigation": "drip", "ತೊಟ್ಟು": "drip",
    "bore well": "borewell", "borewell": "borewell", "bore": "borewell",
    "canal": "canal", "ಕಾಲುವೆ": "canal",
    "rain": "rainfed", "rain fed": "rainfed", "rainfed": "rainfed", "ಮಳೆ": "rainfed",
    "sprinkler": "sprinkler",
    "well": "well", "bavi": "well", "ಬಾವಿ": "well",
    "tank": "tank", "kere": "tank", "ಕೆರೆ": "tank",
}

# -------------------------------------------------------------------
# CATEGORY / INCOME KEYWORDS
# -------------------------------------------------------------------
INCOME_KEYWORDS = {
    "bpl": "BPL", "below poverty": "BPL",
    "small farmer": "small", "small": "small",
    "marginal": "marginal", "marginal farmer": "marginal",
    "large": "large", "big farmer": "large",
}

FARMING_TYPE_KEYWORDS = {
    "organic": "organic", "ಸಾವಯವ": "organic",
    "conventional": "conventional",
    "natural farming": "natural",
}

GENDER_KEYWORDS = {
    "female": "female", "woman": "female", "lady": "female", "ಮಹಿಳಾ": "female",
    "male": "male", "man": "male",
}


def extract_land_size(text: str) -> Optional[float]:
    """Extract land size in acres from the text."""
    # Matches patterns like: "3 acres", "2.5 acre", "3 ಎಕರೆ", "5 ಎಕರ"
    patterns = [
        r"(\d+\.?\d*)\s*(?:acres?|ಎಕರೆ|ಎಕರ|ekare)",
        r"(\d+\.?\d*)\s*(?:guntas?|ಗುಂಟ)",  # guntas – 40 guntas = 1 acre
    ]
    for pattern in patterns:
        match = re.search(pattern, text, re.IGNORECASE)
        if match:
            val = float(match.group(1))
            if "gunta" in pattern:
                val = round(val / 40, 2)  # convert to acres
            return val
    return None


def extract_district(text: str) -> Optional[str]:
    """Extract district name from text using keyword lookup."""
    text_lower = text.lower()
    for keyword, district in DISTRICT_KEYWORDS.items():
        if keyword.lower() in text_lower:
            return district
    return None


def extract_crop(text: str) -> Optional[str]:
    """Extract primary crop type from text."""
    text_lower = text.lower()
    for keyword, crop in CROP_KEYWORDS.items():
        if keyword.lower() in text_lower:
            return crop
    return None


def extract_irrigation(text: str) -> Optional[str]:
    """Extract irrigation type from text."""
    text_lower = text.lower()
    for keyword, irrigation in IRRIGATION_KEYWORDS.items():
        if keyword.lower() in text_lower:
            return irrigation
    return None


def extract_income_category(text: str) -> Optional[str]:
    """Extract income / farmer category."""
    text_lower = text.lower()
    for keyword, category in INCOME_KEYWORDS.items():
        if keyword.lower() in text_lower:
            return category
    return None


def extract_farming_type(text: str) -> Optional[str]:
    """Extract farming type (organic, conventional)."""
    text_lower = text.lower()
    for keyword, ftype in FARMING_TYPE_KEYWORDS.items():
        if keyword.lower() in text_lower:
            return ftype
    return None


def extract_gender(text: str) -> Optional[str]:
    """Extract gender if mentioned."""
    text_lower = text.lower()
    for keyword, gender in GENDER_KEYWORDS.items():
        if keyword.lower() in text_lower:
            return gender
    return None


def calculate_confidence(profile: FarmerProfile) -> float:
    """Calculate overall extraction confidence based on how many fields were found."""
    fields = [
        profile.district, profile.land_size, profile.crop_type,
        profile.irrigation_type, profile.income_category,
        profile.farming_type, profile.gender,
    ]
    filled = sum(1 for f in fields if f is not None)
    return round(filled / len(fields), 2)


def extract_farmer_profile(text: str) -> FarmerProfile:
    """
    Main entry point — extract a FarmerProfile from any natural language query.
    Supports Kannada, English, and mixed language.
    """
    logger.info(f"Extracting farmer profile from: {text[:80]}...")

    language = detect_language(text)
    district = extract_district(text)
    land_size = extract_land_size(text)
    crop_type = extract_crop(text)
    irrigation_type = extract_irrigation(text)
    income_category = extract_income_category(text)
    farming_type = extract_farming_type(text)
    gender = extract_gender(text)

    profile = FarmerProfile(
        district=district,
        state="Karnataka",  # Default to Karnataka for this system
        land_size=land_size,
        crop_type=crop_type,
        irrigation_type=irrigation_type,
        income_category=income_category,
        farming_type=farming_type,
        gender=gender,
        language=language,
        extraction_confidence=0.0,
    )

    # Calculate and attach confidence
    profile.extraction_confidence = calculate_confidence(profile)

    logger.info(
        f"Extracted profile — district={district}, crop={crop_type}, "
        f"land={land_size} acres, confidence={profile.extraction_confidence}"
    )
    return profile
