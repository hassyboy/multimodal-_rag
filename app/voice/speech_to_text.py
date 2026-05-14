"""
Speech-to-Text — Phase 3
Converts uploaded audio to text using faster-whisper.
Optimized for Kannada and English. Returns transcription + detected language + confidence.
"""
import os
import time
from typing import Tuple, Optional
from app.core.logger import get_logger

logger = get_logger(__name__)

# Lazy-load the model once to avoid repeated initialization
_whisper_model = None


def _get_whisper_model():
    """
    Load and cache the faster-whisper model.
    Uses 'base' model — good balance of speed and accuracy for Kannada.
    Upgrade to 'medium' or 'large-v2' for better Kannada accuracy on stronger hardware.
    """
    global _whisper_model
    if _whisper_model is None:
        try:
            from faster_whisper import WhisperModel
            logger.info("Loading faster-whisper model (base)...")
            # device='cpu', compute_type='int8' → runs on any machine without GPU
            _whisper_model = WhisperModel("base", device="cpu", compute_type="int8")
            logger.info("faster-whisper model loaded successfully.")
        except ImportError:
            logger.error("faster-whisper not installed. Run: pip install faster-whisper")
            raise
        except Exception as e:
            logger.error(f"Failed to load whisper model: {e}")
            raise
    return _whisper_model


def transcribe_audio(
    audio_file_path: str,
    language_hint: Optional[str] = None,
) -> dict:
    """
    Transcribe an audio file to text.

    Args:
        audio_file_path: Path to the input audio file (wav, mp3, etc.)
        language_hint: Optional ISO language code hint ('kn' for Kannada, 'en' for English)

    Returns:
        dict with keys:
            - transcribed_text: str
            - detected_language: str  ('kannada' or 'english')
            - language_code: str      (e.g. 'kn', 'en')
            - confidence: float       (0.0 - 1.0)
            - duration_seconds: float
            - success: bool
            - error: str or None
    """
    if not os.path.exists(audio_file_path):
        return _error_result(f"Audio file not found: {audio_file_path}")

    try:
        model = _get_whisper_model()
        start = time.time()

        # Transcribe — pass language hint if provided
        segments, info = model.transcribe(
            audio_file_path,
            language=language_hint,       # None → auto-detect
            beam_size=5,
            vad_filter=True,              # Voice Activity Detection — removes silence/noise
            vad_parameters=dict(min_silence_duration_ms=300),
        )

        # Collect all segments
        full_text = ""
        avg_confidence = 0.0
        seg_count = 0

        for segment in segments:
            full_text += segment.text + " "
            # segment.avg_logprob is log probability; convert to approx confidence
            avg_confidence += min(1.0, max(0.0, 1.0 + segment.avg_logprob))
            seg_count += 1

        full_text = full_text.strip()
        confidence = round(avg_confidence / max(seg_count, 1), 3)
        elapsed = round(time.time() - start, 2)

        lang_code = info.language or "en"
        detected_language = "kannada" if lang_code == "kn" else "english"

        logger.info(
            f"Transcribed in {elapsed}s | lang={lang_code} | "
            f"confidence={confidence} | text='{full_text[:60]}...'"
        )

        return {
            "transcribed_text": full_text,
            "detected_language": detected_language,
            "language_code": lang_code,
            "confidence": confidence,
            "duration_seconds": round(info.duration, 2) if hasattr(info, "duration") else None,
            "processing_time_seconds": elapsed,
            "success": True,
            "error": None,
        }

    except Exception as e:
        logger.error(f"Transcription failed for {audio_file_path}: {e}")
        return _error_result(str(e))


def _error_result(error_msg: str) -> dict:
    return {
        "transcribed_text": "",
        "detected_language": "english",
        "language_code": "en",
        "confidence": 0.0,
        "duration_seconds": None,
        "processing_time_seconds": 0.0,
        "success": False,
        "error": error_msg,
    }
