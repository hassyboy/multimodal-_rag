import langdetect
from app.core.logger import get_logger

logger = get_logger(__name__)

def detect_language(text: str) -> str:
    """
    Detect the language of the input text.
    Returns: "kannada" or "english" only.
    Mixed / Kanglish queries containing Kannada script → "kannada"
    Mixed / Kanglish queries in Latin script → "english"
    """
    if not text or not text.strip():
        return "english"

    # First — check for actual Kannada Unicode script characters
    # If any Kannada script is present, treat the whole query as Kannada
    for char in text:
        if '\u0c80' <= char <= '\u0cff':
            return "kannada"

    # No Kannada script found — try langdetect on Latin text
    try:
        lang = langdetect.detect(text)
        if lang == 'kn':
            return "kannada"
        return "english"
    except langdetect.lang_detect_exception.LangDetectException as e:
        logger.warning(f"Language detection failed: {e}. Falling back to english.")
        return "english"
