"""
Speech-to-Text — Refined
Converts audio to text using faster-whisper.
Optimized for Kannada (kn) and English. Handles noisy audio via VAD.
Returns transcription, detected language, and per-segment confidence.
"""
import os
import time
from typing import Optional
from app.core.logger import get_logger

logger = get_logger(__name__)

_whisper_model = None

# Whisper model size — 'base' for low-RAM machines, 'small'/'medium' for better Kannada accuracy
WHISPER_MODEL_SIZE = "base"


def _get_whisper_model():
    """Load and cache the faster-whisper model (singleton per process)."""
    global _whisper_model
    if _whisper_model is None:
        try:
            from faster_whisper import WhisperModel
            logger.info(f"Loading faster-whisper '{WHISPER_MODEL_SIZE}' model (CPU, int8)...")
            _whisper_model = WhisperModel(
                WHISPER_MODEL_SIZE,
                device="cpu",
                compute_type="int8",   # Quantized — fast on CPU, low RAM
            )
            logger.info("Whisper model ready.")
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
    Transcribe an audio file to text with language detection and confidence scoring.

    Args:
        audio_file_path: Path to audio file (.wav, .mp3, .m4a, .ogg, .flac, .webm)
        language_hint:   ISO-639-1 code to force language ('kn', 'en'). None = auto-detect.

    Returns:
        {
            transcribed_text, detected_language, language_code,
            confidence, duration_seconds, processing_time_seconds,
            success, error
        }
    """
    if not os.path.exists(audio_file_path):
        return _error_result(f"Audio file not found: {audio_file_path}")

    try:
        model = _get_whisper_model()
        start = time.time()

        segments, info = model.transcribe(
            audio_file_path,
            language=language_hint,     # None → auto-detect
            beam_size=5,                # Higher beam = more accurate (slightly slower)
            best_of=5,                  # Sample diversity for better accuracy
            temperature=0.0,            # Greedy decode — most stable for agriculture domain
            condition_on_previous_text=True,  # Better coherence for multi-sentence speech
            vad_filter=True,            # Remove silence / background noise
            vad_parameters=dict(
                min_silence_duration_ms=400,
                speech_pad_ms=200,
            ),
            word_timestamps=False,      # Not needed — saves memory
        )

        segments_list = list(segments)  # Materialize generator

        if not segments_list:
            logger.warning("Whisper returned no segments — audio may be silent or too noisy.")
            return _error_result("No speech detected. Please speak clearly into the microphone.")

        # Aggregate transcription and confidence
        texts = []
        total_logprob = 0.0
        for seg in segments_list:
            texts.append(seg.text.strip())
            total_logprob += seg.avg_logprob

        full_text = " ".join(t for t in texts if t)
        # Convert log-probability to 0-1 confidence score
        avg_logprob = total_logprob / len(segments_list)
        confidence = round(min(1.0, max(0.0, 1.0 + avg_logprob / 4.0)), 3)

        elapsed = round(time.time() - start, 2)
        lang_code = info.language or "en"

        # Map whisper language codes to our system language strings
        detected_language = _map_language(lang_code)

        logger.info(
            f"STT complete in {elapsed}s | lang={lang_code} ({detected_language}) | "
            f"confidence={confidence} | '{full_text[:70]}'"
        )

        return {
            "transcribed_text": full_text,
            "detected_language": detected_language,
            "language_code": lang_code,
            "confidence": confidence,
            "duration_seconds": round(info.duration, 2) if hasattr(info, "duration") else None,
            "processing_time_seconds": elapsed,
            "segment_count": len(segments_list),
            "success": True,
            "error": None,
        }

    except Exception as e:
        logger.error(f"Transcription error for '{audio_file_path}': {e}")
        return _error_result(f"Transcription failed: {str(e)}")


def _map_language(lang_code: str) -> str:
    """Map whisper ISO language codes to our system's language strings."""
    return "kannada" if lang_code == "kn" else "english"


def _error_result(error_msg: str) -> dict:
    return {
        "transcribed_text": "",
        "detected_language": "english",
        "language_code": "en",
        "confidence": 0.0,
        "duration_seconds": None,
        "processing_time_seconds": 0.0,
        "segment_count": 0,
        "success": False,
        "error": error_msg,
    }
