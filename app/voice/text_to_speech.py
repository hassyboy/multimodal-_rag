"""
Text-to-Speech — Phase 3
Converts LLM response text to audio using gTTS.
Supports Kannada (kn) and English (en).
Saves output as MP3 in storage/output_audio/.
"""
import os
from app.voice.audio_utils import generate_output_filename, ensure_output_dir
from app.core.logger import get_logger

logger = get_logger(__name__)

# Map our language strings to gTTS language codes
LANG_CODE_MAP = {
    "kannada": "kn",
    "english": "en",
}


def text_to_speech(
    text: str,
    language: str = "kannada",
    output_dir: str = "storage/output_audio",
) -> dict:
    """
    Convert text to speech and save as an MP3 file.

    Args:
        text:       Text to convert (supports Kannada Unicode)
        language:   'kannada' or 'english'
        output_dir: Directory to save the generated audio file

    Returns:
        dict with keys:
            - audio_path: str   — absolute path to the generated MP3
            - language: str
            - success: bool
            - error: str or None
    """
    if not text or not text.strip():
        return _error_result("No text provided for speech synthesis")

    try:
        from gtts import gTTS
    except ImportError:
        return _error_result("gTTS not installed. Run: pip install gTTS")

    # Resolve language code
    lang_code = LANG_CODE_MAP.get(language, "en")

    try:
        ensure_output_dir(output_dir)
        filename = generate_output_filename(prefix=f"response_{language}")
        output_path = os.path.join(output_dir, filename)

        logger.info(f"Generating TTS audio | lang={lang_code} | chars={len(text)}")

        tts = gTTS(text=text, lang=lang_code, slow=False)
        tts.save(output_path)

        abs_path = os.path.abspath(output_path)
        logger.info(f"TTS audio saved: {abs_path}")

        return {
            "audio_path": abs_path,
            "language": language,
            "lang_code": lang_code,
            "success": True,
            "error": None,
        }

    except Exception as e:
        logger.error(f"TTS generation failed: {e}")
        return _error_result(str(e))


def _error_result(error_msg: str) -> dict:
    return {
        "audio_path": None,
        "language": "english",
        "lang_code": "en",
        "success": False,
        "error": error_msg,
    }
