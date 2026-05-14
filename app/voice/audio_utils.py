"""
Audio Utilities — Phase 3
Validates, inspects, and cleans up uploaded audio files.
"""
import os
import time
from pathlib import Path
from typing import Tuple
from app.core.logger import get_logger

logger = get_logger(__name__)

# Supported formats that faster-whisper can handle
SUPPORTED_FORMATS = {".wav", ".mp3", ".mp4", ".m4a", ".ogg", ".flac", ".webm"}

MAX_FILE_SIZE_MB = 25       # Max audio upload size
MAX_DURATION_SECONDS = 120  # Max audio duration (2 minutes)
MIN_DURATION_SECONDS = 0.5  # Minimum audio duration


def validate_audio_file(file_path: str) -> Tuple[bool, str]:
    """
    Validate an uploaded audio file.
    Returns (is_valid, error_message).
    """
    path = Path(file_path)

    # Check file exists
    if not path.exists():
        return False, f"File not found: {file_path}"

    # Check file extension
    if path.suffix.lower() not in SUPPORTED_FORMATS:
        return False, (
            f"Unsupported format '{path.suffix}'. "
            f"Supported formats: {', '.join(SUPPORTED_FORMATS)}"
        )

    # Check file size
    size_mb = path.stat().st_size / (1024 * 1024)
    if size_mb > MAX_FILE_SIZE_MB:
        return False, f"File too large ({size_mb:.1f} MB). Max allowed: {MAX_FILE_SIZE_MB} MB"

    # Check file is not empty
    if path.stat().st_size == 0:
        return False, "Audio file is empty"

    return True, ""


def get_audio_info(file_path: str) -> dict:
    """
    Return basic metadata about an audio file.
    Uses soundfile for WAV/FLAC, falls back to basic info for other formats.
    """
    info = {
        "file_path": file_path,
        "format": Path(file_path).suffix.lower(),
        "size_mb": round(Path(file_path).stat().st_size / (1024 * 1024), 3),
    }

    try:
        import soundfile as sf
        data, samplerate = sf.read(file_path)
        duration = len(data) / samplerate
        info["duration_seconds"] = round(duration, 2)
        info["sample_rate"] = samplerate
        info["channels"] = data.ndim
    except Exception:
        # Non-WAV format — skip detailed info
        info["duration_seconds"] = None

    return info


def cleanup_file(file_path: str) -> None:
    """Safely delete a temporary audio file."""
    try:
        if os.path.exists(file_path):
            os.remove(file_path)
            logger.debug(f"Cleaned up temp file: {file_path}")
    except Exception as e:
        logger.warning(f"Could not clean up file {file_path}: {e}")


def generate_output_filename(prefix: str = "response") -> str:
    """Generate a unique output audio filename."""
    timestamp = int(time.time())
    return f"{prefix}_{timestamp}.mp3"


def ensure_output_dir(output_dir: str = "storage/output_audio") -> str:
    """Ensure the output directory exists and return its path."""
    os.makedirs(output_dir, exist_ok=True)
    return output_dir
