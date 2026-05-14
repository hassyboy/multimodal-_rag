import langdetect
from app.core.logger import get_logger

logger = get_logger(__name__)

# Basic Kannada vocabulary check to fallback on mixed/Kanglish
KANNADA_KEYWORDS = ["kannada", "ge", "yen", "ide", "beku", "madbeku", "ritha", "raitige", "raitha", "bele", "subsidy"]

def detect_language(text: str) -> str:
    """
    Detect the language of the input text.
    Returns: "kannada", "english", or "mixed"
    """
    if not text or not text.strip():
        return "english"
        
    try:
        lang = langdetect.detect(text)
        
        # Exact Kannada script detected
        if lang == 'kn':
            return "kannada"
            
        # If English detected, check for transliterated Kannada (Kanglish / Mixed)
        if lang == 'en':
            text_lower = text.lower()
            kannada_word_count = sum(1 for word in KANNADA_KEYWORDS if word in text_lower.split())
            if kannada_word_count > 0:
                return "mixed"
            return "english"
            
    except langdetect.lang_detect_exception.LangDetectException as e:
        logger.warning(f"Language detection failed: {e}. Falling back to english.")
        return "english"
        
    # Default fallback
    return "english"
