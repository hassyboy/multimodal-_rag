"""
Speech-to-Text — Refined
Converts audio to text using faster-whisper.
Automatically converts browser webm/ogg to wav before transcription.
Returns transcription, detected language, and confidence.
"""
import os
import time
import tempfile
from typing import Optional
from app.core.logger import get_logger

logger = get_logger(__name__)

_whisper_model = None
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
                compute_type="int8",
            )
            logger.info("Whisper model ready.")
        except ImportError:
            logger.error("faster-whisper not installed. Run: pip install faster-whisper")
            raise
        except Exception as e:
            logger.error(f"Failed to load whisper model: {e}")
            raise
    return _whisper_model


def _convert_to_wav(input_path: str) -> Optional[str]:
    """
    Convert audio to 16kHz mono WAV using pydub.
    Returns path to converted WAV file, or None if conversion fails.
    WAV is the only format faster-whisper can process without ffmpeg.
    """
    try:
        from pydub import AudioSegment
        ext = os.path.splitext(input_path)[1].lower()

        if ext == ".webm":
            audio = AudioSegment.from_file(input_path, format="webm")
        elif ext == ".ogg":
            audio = AudioSegment.from_ogg(input_path)
        elif ext == ".mp3":
            audio = AudioSegment.from_mp3(input_path)
        elif ext == ".m4a":
            audio = AudioSegment.from_file(input_path, format="m4a")
        elif ext == ".flac":
            audio = AudioSegment.from_file(input_path, format="flac")
        elif ext == ".wav":
            return input_path   # Already WAV, no conversion needed
        else:
            audio = AudioSegment.from_file(input_path)

        # Normalize to 16kHz mono (Whisper's preferred format)
        audio = audio.set_frame_rate(16000).set_channels(1)

        tmp = tempfile.NamedTemporaryFile(delete=False, suffix=".wav")
        tmp.close()
        audio.export(tmp.name, format="wav")
        logger.info(f"Converted {ext} → WAV ({len(audio) / 1000:.1f}s, 16kHz mono) → {tmp.name}")
        return tmp.name

    except Exception as e:
        logger.warning(f"Audio conversion failed ({e}) — will try direct transcription")
        return None


def transcribe_audio(
    audio_file_path: str,
    language_hint: Optional[str] = None,
) -> dict:
    """
    Transcribe an audio file to text.

    Workflow:
        1. If format is not WAV, convert to 16kHz WAV first (pydub)
        2. Run faster-whisper transcription
        3. If VAD strips all speech, retry without VAD filter

    Args:
        audio_file_path: Path to audio file (.wav, .webm, .mp3, .m4a, .ogg, .flac)
        language_hint:   'kn' = force Kannada, 'en' = force English, None = auto-detect

    Returns:
        dict with transcribed_text, detected_language, confidence, success, error
    """
    if not os.path.exists(audio_file_path):
        return _error_result(f"Audio file not found: {audio_file_path}")

    converted_path = None
    try:
        model = _get_whisper_model()
        start = time.time()

        # Step 1: Convert to WAV for maximum compatibility
        ext = os.path.splitext(audio_file_path)[1].lower()
        if ext != ".wav":
            wav_path = _convert_to_wav(audio_file_path)
            if wav_path and wav_path != audio_file_path:
                converted_path = wav_path   # Track for cleanup
                transcription_path = wav_path
            else:
                transcription_path = audio_file_path  # Try original as fallback
        else:
            transcription_path = audio_file_path

        # Step 2: Transcribe with VAD
        segments, info = _run_transcription(
            model, transcription_path, language_hint, use_vad=True
        )
        segments_list = list(segments)

        # Step 3: If VAD killed everything, retry without VAD
        if not segments_list:
            logger.warning("VAD returned no segments — retrying without VAD filter")
            segments, info = _run_transcription(
                model, transcription_path, language_hint, use_vad=False
            )
            segments_list = list(segments)

        # Step 4: Check again
        if not segments_list:
            return _error_result(
                "No speech detected. Please speak louder and closer to the microphone."
            )

        # Aggregate
        texts = [seg.text.strip() for seg in segments_list]
        total_logprob = sum(seg.avg_logprob for seg in segments_list)
        full_text = " ".join(t for t in texts if t)
        avg_logprob = total_logprob / len(segments_list)
        confidence = round(min(1.0, max(0.0, 1.0 + avg_logprob / 4.0)), 3)

        elapsed = round(time.time() - start, 2)
        lang_code = info.language or "en"
        detected_language = _map_language(lang_code)

        logger.info(
            f"STT done in {elapsed}s | lang={lang_code} | conf={confidence} | '{full_text[:80]}'"
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

    finally:
        # Clean up temporary converted WAV
        if converted_path and os.path.exists(converted_path):
            try:
                os.remove(converted_path)
            except Exception:
                pass


def _run_transcription(model, path: str, language_hint: Optional[str], use_vad: bool):
    """Run whisper transcription with or without VAD."""
    kwargs = dict(
        language=language_hint,
        beam_size=5,
        best_of=5,
        temperature=0.0,
        condition_on_previous_text=True,
        word_timestamps=False,
    )
    if use_vad:
        kwargs["vad_filter"] = True
        kwargs["vad_parameters"] = dict(
            min_silence_duration_ms=500,
            speech_pad_ms=300,
            threshold=0.3,      # Lower threshold = less aggressive — catches quiet speech
        )
    else:
        kwargs["vad_filter"] = False

    return model.transcribe(path, **kwargs)


def _map_language(lang_code: str) -> str:
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
