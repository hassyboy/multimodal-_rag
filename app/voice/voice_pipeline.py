"""
Voice Pipeline — Refined
Orchestrates the complete voice-to-voice agricultural assistant flow.
Audio → Validate → STT → RAG → LLM → TTS → Audio
"""
import time
from app.voice.audio_utils import validate_audio_file, get_audio_info, cleanup_file
from app.voice.speech_to_text import transcribe_audio
from app.voice.text_to_speech import text_to_speech
from app.rag.retriever import retrieve_documents
from app.rag.prompt_builder import get_rag_prompt
from app.llm.llm_service import generate_response
from app.core.logger import get_logger

logger = get_logger(__name__)

# Fallback messages when LLM fails — shown as voice response
FALLBACK_MESSAGES = {
    "kannada": "ಕ್ಷಮಿಸಿ, ಮಾಹಿತಿ ತರಲು ತೊಂದರೆ ಆಯಿತು. ದಯವಿಟ್ಟು ಮತ್ತೆ ಪ್ರಯತ್ನಿಸಿ.",
    "english": "Sorry, I encountered an issue fetching the information. Please try again.",
}


def run_voice_pipeline(audio_file_path: str, cleanup_input: bool = True) -> dict:
    """
    Full voice-to-voice RAG pipeline.

    Flow:
        1. Audio validation (format, size, empty)
        2. Speech-to-text via faster-whisper
        3. RAG retrieval from ChromaDB
        4. LLM answer generation via Ollama
        5. Text-to-speech via gTTS
        6. Return structured result + timing metrics

    Args:
        audio_file_path: Path to the uploaded audio file
        cleanup_input:   Delete input file after processing

    Returns:
        Full pipeline result dict
    """
    pipeline_start = time.time()
    logger.info(f"=== Voice Pipeline START: {audio_file_path} ===")

    # ─── STEP 1: Validate audio ────────────────────────────────────
    is_valid, error_msg = validate_audio_file(audio_file_path)
    if not is_valid:
        logger.error(f"[STEP 1] Audio validation failed: {error_msg}")
        return _error_result(error_msg, stage="audio_validation")

    audio_info = get_audio_info(audio_file_path)
    logger.info(f"[STEP 1] Audio OK | {audio_info['format']} | {audio_info['size_mb']} MB")

    # ─── STEP 2: Speech-to-Text ────────────────────────────────────
    t0 = time.time()
    stt_result = transcribe_audio(audio_file_path)
    stt_elapsed = round(time.time() - t0, 2)

    if not stt_result["success"] or not stt_result["transcribed_text"].strip():
        _safe_cleanup(audio_file_path, cleanup_input)
        msg = stt_result.get("error") or "No speech detected. Please speak clearly."
        logger.error(f"[STEP 2] STT failed: {msg}")
        return _error_result(msg, stage="speech_to_text")

    transcribed_text = stt_result["transcribed_text"]
    language = stt_result["detected_language"]
    confidence = stt_result["confidence"]
    logger.info(
        f"[STEP 2] STT done in {stt_elapsed}s | lang={language} | "
        f"conf={confidence} | '{transcribed_text[:60]}'"
    )

    # ─── STEP 3: RAG Retrieval ─────────────────────────────────────
    t0 = time.time()
    docs = []
    context = ""
    try:
        docs = retrieve_documents(transcribed_text)
        context = "\n\n---\n\n".join(
            [f"[Source {i+1}]\n{doc.page_content}" for i, doc in enumerate(docs)]
        )
    except Exception as e:
        logger.warning(f"[STEP 3] RAG retrieval failed: {e} — proceeding with empty context")
    rag_elapsed = round(time.time() - t0, 2)
    logger.info(f"[STEP 3] RAG done in {rag_elapsed}s | {len(docs)} chunks retrieved")

    # ─── STEP 4: LLM Response Generation ──────────────────────────
    t0 = time.time()
    answer = FALLBACK_MESSAGES.get(language, FALLBACK_MESSAGES["english"])
    try:
        prompt_template = get_rag_prompt()
        prompt = prompt_template.format(
            context=context if context else "No relevant information found in the knowledge base.",
            question=transcribed_text,
            language=language,
        )
        answer = generate_response(prompt)
    except Exception as e:
        logger.error(f"[STEP 4] LLM generation failed: {e} — using fallback message")
    llm_elapsed = round(time.time() - t0, 2)
    logger.info(f"[STEP 4] LLM done in {llm_elapsed}s | answer length={len(answer)} chars")

    # ─── STEP 5: Text-to-Speech ────────────────────────────────────
    t0 = time.time()
    tts_result = text_to_speech(answer, language=language)
    tts_elapsed = round(time.time() - t0, 2)

    if not tts_result["success"]:
        logger.warning(f"[STEP 5] TTS failed: {tts_result.get('error')} — text-only response")
    else:
        logger.info(
            f"[STEP 5] TTS done in {tts_elapsed}s | "
            f"{tts_result.get('file_size_kb', 0)} KB | {tts_result.get('audio_path')}"
        )

    # ─── Cleanup & Return ──────────────────────────────────────────
    _safe_cleanup(audio_file_path, cleanup_input)
    total_elapsed = round(time.time() - pipeline_start, 2)
    logger.info(f"=== Voice Pipeline DONE in {total_elapsed}s ===")

    return {
        "success": True,
        "language": language,
        "confidence": confidence,
        "transcribed_text": transcribed_text,
        "answer": answer,
        "audio_response_path": tts_result.get("audio_path"),
        "tts_success": tts_result["success"],
        "sources_count": len(docs),
        "timing": {
            "stt_seconds": stt_elapsed,
            "rag_seconds": rag_elapsed,
            "llm_seconds": llm_elapsed,
            "tts_seconds": tts_elapsed,
            "total_seconds": total_elapsed,
        },
        "error": None,
        "failed_stage": None,
    }


def _safe_cleanup(path: str, should_cleanup: bool) -> None:
    if should_cleanup:
        cleanup_file(path)


def _error_result(error: str, stage: str = "unknown") -> dict:
    return {
        "success": False,
        "language": "english",
        "confidence": 0.0,
        "transcribed_text": "",
        "answer": "",
        "audio_response_path": None,
        "tts_success": False,
        "sources_count": 0,
        "timing": {},
        "error": error,
        "failed_stage": stage,
    }
