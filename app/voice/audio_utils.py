"""
Audio Utilities — Refined
Validates, inspects, and manages audio files with duration and size checks.
"""
import os
import time
import uuid
from pathlib import Path
from typing import Tuple
from app.core.logger import get_logger

logger = get_logger(__name__)

SUPPORTED_FORMATS = {".wav", ".mp3", ".mp4", ".m4a", ".ogg", ".flac", ".webm"}
MAX_FILE_SIZE_MB = 25
MAX_DURATION_SECONDS = 120
MIN_FILE_SIZE_BYTES = 512   # reject truly empty/corrupt files (~0.5 KB minimum)
OUTPUT_AUDIO_DIR = "storage/output_audio"


def validate_audio_file(file_path: str) -> Tuple[bool, str]:
    """
    Validate an uploaded audio file for format, size, and emptiness.
    Returns (is_valid, error_message).
    """
    path = Path(file_path)

    if not path.exists():
        return False, f"File not found: {file_path}"

    ext = path.suffix.lower()
    if ext not in SUPPORTED_FORMATS:
        return False, (
            f"Unsupported format '{ext}'. "
            f"Supported: {', '.join(sorted(SUPPORTED_FORMATS))}"
        )

    size_bytes = path.stat().st_size
    if size_bytes < MIN_FILE_SIZE_BYTES:
        return False, f"Audio file is too small ({size_bytes} bytes). May be empty or corrupt."

    size_mb = size_bytes / (1024 * 1024)
    if size_mb > MAX_FILE_SIZE_MB:
        return False, f"File too large ({size_mb:.1f} MB). Max allowed: {MAX_FILE_SIZE_MB} MB."

    return True, ""


def get_audio_info(file_path: str) -> dict:
    """
    Return basic metadata about an audio file.
    Tries soundfile for WAV/FLAC, falls back to size-only info for other formats.
    """
    path = Path(file_path)
    info = {
        "file_path": file_path,
        "format": path.suffix.lower(),
        "size_mb": round(path.stat().st_size / (1024 * 1024), 3),
        "duration_seconds": None,
        "sample_rate": None,
        "channels": None,
    }

    try:
        import soundfile as sf
        data, samplerate = sf.read(file_path)
        samples = data.shape[0] if data.ndim > 1 else len(data)
        duration = samples / samplerate
        info["duration_seconds"] = round(duration, 2)
        info["sample_rate"] = samplerate
        info["channels"] = data.shape[1] if data.ndim > 1 else 1

        if duration > MAX_DURATION_SECONDS:
            logger.warning(f"Audio duration {duration:.1f}s exceeds max {MAX_DURATION_SECONDS}s")
    except Exception:
        pass  # Non-WAV/FLAC — skip duration check (whisper handles it internally)

    return info


def cleanup_file(file_path: str) -> None:
    """Safely delete a temporary audio file."""
    try:
        if file_path and os.path.exists(file_path):
            os.remove(file_path)
            logger.debug(f"Cleaned up temp file: {file_path}")
    except Exception as e:
        logger.warning(f"Could not delete temp file {file_path}: {e}")


def cleanup_old_outputs(max_files: int = 50) -> None:
    """
    Keep the output_audio directory clean by removing oldest files
    when the count exceeds max_files.
    """
    try:
        output_dir = Path(OUTPUT_AUDIO_DIR)
        if not output_dir.exists():
            return
        files = sorted(output_dir.glob("*.mp3"), key=lambda f: f.stat().st_mtime)
        if len(files) > max_files:
            for old_file in files[:len(files) - max_files]:
                old_file.unlink()
                logger.debug(f"Removed old output file: {old_file.name}")
    except Exception as e:
        logger.warning(f"Cleanup of old outputs failed: {e}")


def generate_output_filename(prefix: str = "response") -> str:
    """Generate a unique, timestamped output filename."""
    timestamp = int(time.time())
    uid = str(uuid.uuid4())[:8]
    return f"{prefix}_{timestamp}_{uid}.mp3"


def ensure_output_dir(output_dir: str = OUTPUT_AUDIO_DIR) -> str:
    """Ensure the output directory exists."""
    os.makedirs(output_dir, exist_ok=True)
    return output_dir
