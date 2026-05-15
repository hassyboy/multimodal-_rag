"""
POST /voice-ask
Voice-enabled RAG endpoint.
Accepts audio upload, returns transcription + LLM answer + audio response path.
"""
import os
import tempfile
from fastapi import APIRouter, UploadFile, File, Form, HTTPException
from fastapi.responses import JSONResponse
from app.voice.voice_pipeline import run_voice_pipeline
from app.voice.audio_utils import SUPPORTED_FORMATS
from app.core.logger import get_logger
from typing import Optional

router = APIRouter()
logger = get_logger(__name__)


@router.post("/voice-ask")
async def voice_ask(
    audio: UploadFile = File(..., description="Audio file (wav, mp3, m4a, ogg, flac, webm)"),
    language_hint: Optional[str] = Form(None, description="Language hint: 'kn' for Kannada, 'en' for English"),
):
    """
    Voice-based agricultural scheme assistant.

    Upload an audio file of a farmer speaking in Kannada or English.
    The system will:
    1. Transcribe the speech to text
    2. Detect the language automatically
    3. Retrieve relevant government scheme information
    4. Generate a farmer-friendly answer
    5. Convert the answer back to speech

    Returns JSON with transcription, answer text, and path to audio response.
    """
    # Validate file extension
    ext = os.path.splitext(audio.filename or "")[1].lower()
    if ext not in SUPPORTED_FORMATS:
        raise HTTPException(
            status_code=400,
            detail=f"Unsupported audio format '{ext}'. Supported: {', '.join(SUPPORTED_FORMATS)}"
        )

    # Save uploaded file to a temp location
    temp_path = None
    try:
        with tempfile.NamedTemporaryFile(delete=False, suffix=ext) as tmp:
            content = await audio.read()
            tmp.write(content)
            temp_path = tmp.name

        logger.info(f"Voice ask | file={audio.filename} | lang_hint={language_hint} | {len(content)/1024:.1f} KB")

        # Map hint string to whisper language code
        whisper_lang = None
        if language_hint == 'kn':
            whisper_lang = 'kn'
        elif language_hint == 'en':
            whisper_lang = 'en'

        result = run_voice_pipeline(
            audio_file_path=temp_path,
            cleanup_input=True,
            language_hint=whisper_lang,
        )

        if not result["success"]:
            raise HTTPException(
                status_code=422,
                detail=result.get("error", "Voice processing failed")
            )

        return JSONResponse(content={
            "language": result["language"],
            "confidence": result["confidence"],
            "transcribed_text": result["transcribed_text"],
            "answer": result["answer"],
            "audio_response_path": result["audio_response_path"],
            "timing": result["timing"],
            "sources_count": result["sources_count"],
        })

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Unexpected error in /voice-ask: {e}")
        # Clean up temp file if pipeline didn't
        if temp_path and os.path.exists(temp_path):
            os.remove(temp_path)
        raise HTTPException(status_code=500, detail=f"Internal error: {str(e)}")
