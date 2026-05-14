"""
Text-to-Speech — Refined
Converts LLM response text to MP3 audio using gTTS.
Fully supports Kannada Unicode. Saves to storage/output_audio/.
"""
import os
from app.voice.audio_utils import generate_output_filename, ensure_output_dir, OUTPUT_AUDIO_DIR, cleanup_old_outputs
from app.core.logger import get_logger

logger = get_logger(__name__)

LANG_CODE_MAP = {
    "kannada": "kn",
    "english": "en",
}

# Max characters gTTS can reliably handle in one call
MAX_TTS_CHARS = 4000


def text_to_speech(
    text: str,
    language: str = "kannada",
    output_dir: str = OUTPUT_AUDIO_DIR,
) -> dict:
    """
    Convert text to speech and save as MP3.

    Args:
        text:       Text to synthesize (supports full Kannada Unicode)
        language:   'kannada' or 'english'
        output_dir: Directory to store output audio

    Returns:
        {audio_path, language, lang_code, success, error}
    """
    if not text or not text.strip():
        return _error_result("Empty text — nothing to synthesize.")

    try:
        from gtts import gTTS, gTTSError
    except ImportError:
        return _error_result("gTTS not installed. Run: pip install gTTS")

    lang_code = LANG_CODE_MAP.get(language, "en")

    # Trim to safe length to avoid gTTS timeout on very long answers
    synthesis_text = text.strip()
    if len(synthesis_text) > MAX_TTS_CHARS:
        logger.warning(f"Text truncated from {len(synthesis_text)} to {MAX_TTS_CHARS} chars for TTS.")
        synthesis_text = synthesis_text[:MAX_TTS_CHARS] + "..."

    try:
        ensure_output_dir(output_dir)
        filename = generate_output_filename(prefix=f"agri_{language}")
        output_path = os.path.join(output_dir, filename)

        logger.info(f"Synthesizing speech | lang={lang_code} | chars={len(synthesis_text)}")

        tts = gTTS(
            text=synthesis_text,
            lang=lang_code,
            slow=False,     # Normal speed — more natural for farmers
        )
        tts.save(output_path)

        abs_path = os.path.abspath(output_path)
        file_size_kb = round(os.path.getsize(abs_path) / 1024, 1)
        logger.info(f"TTS audio saved: {abs_path} ({file_size_kb} KB)")

        # Periodically clean up old output files
        cleanup_old_outputs(max_files=50)

        return {
            "audio_path": abs_path,
            "language": language,
            "lang_code": lang_code,
            "file_size_kb": file_size_kb,
            "success": True,
            "error": None,
        }

    except Exception as e:
        logger.error(f"TTS generation failed: {e}")
        return _error_result(f"Speech synthesis failed: {str(e)}")


def _error_result(error_msg: str) -> dict:
    return {
        "audio_path": None,
        "language": "english",
        "lang_code": "en",
        "file_size_kb": 0,
        "success": False,
        "error": error_msg,
    }
