"""
Voice Pipeline — Phase 3
Orchestrates the full voice-to-voice flow:
Audio → STT → Language Detection → RAG → LLM → TTS → Audio
"""
import time
from app.voice.audio_utils import validate_audio_file, cleanup_file
from app.voice.speech_to_text import transcribe_audio
from app.voice.text_to_speech import text_to_speech
from app.rag.retriever import retrieve_documents
from app.rag.prompt_builder import get_rag_prompt
from app.llm.llm_service import generate_response
from app.core.logger import get_logger

logger = get_logger(__name__)


def run_voice_pipeline(audio_file_path: str, cleanup_input: bool = True) -> dict:
    """
    Full voice-to-voice RAG pipeline.

    Steps:
        1. Validate audio file
        2. Transcribe audio → text (faster-whisper)
        3. Detect language from transcription
        4. Retrieve relevant documents (ChromaDB RAG)
        5. Build personalized prompt with farmer-friendly instructions
        6. Generate LLM response (Ollama)
        7. Convert response text → speech (gTTS)
        8. Return structured result with timing metrics

    Args:
        audio_file_path: Path to uploaded audio file
        cleanup_input:   Whether to delete the temp input file after processing

    Returns:
        dict with full pipeline result
    """
    pipeline_start = time.time()
    logger.info(f"Starting voice pipeline for: {audio_file_path}")

    # -------------------------------------------------------
    # STEP 1 — Validate audio
    # -------------------------------------------------------
    is_valid, error_msg = validate_audio_file(audio_file_path)
    if not is_valid:
        logger.error(f"Audio validation failed: {error_msg}")
        return _error_result(error_msg, stage="audio_validation")

    # -------------------------------------------------------
    # STEP 2 — Speech to Text
    # -------------------------------------------------------
    stt_start = time.time()
    stt_result = transcribe_audio(audio_file_path)
    stt_elapsed = round(time.time() - stt_start, 2)

    if not stt_result["success"] or not stt_result["transcribed_text"].strip():
        logger.error(f"STT failed: {stt_result.get('error')}")
        _safe_cleanup(audio_file_path, cleanup_input)
        return _error_result(
            stt_result.get("error", "Could not transcribe audio. Please speak clearly."),
            stage="speech_to_text",
        )

    transcribed_text = stt_result["transcribed_text"]
    language = stt_result["detected_language"]
    confidence = stt_result["confidence"]

    logger.info(f"STT done in {stt_elapsed}s | lang={language} | text='{transcribed_text[:60]}'")

    # -------------------------------------------------------
    # STEP 3 — RAG Retrieval
    # -------------------------------------------------------
    rag_start = time.time()
    try:
        docs = retrieve_documents(transcribed_text)
        context = "\n\n".join([doc.page_content for doc in docs])
    except Exception as e:
        logger.error(f"RAG retrieval failed: {e}")
        context = ""
        docs = []
    rag_elapsed = round(time.time() - rag_start, 2)
    logger.info(f"RAG retrieval done in {rag_elapsed}s | {len(docs)} chunks found")

    # -------------------------------------------------------
    # STEP 4 — Build Prompt & Generate LLM Response
    # -------------------------------------------------------
    llm_start = time.time()
    try:
        prompt_template = get_rag_prompt()
        prompt = prompt_template.format(
            context=context if context else "No relevant scheme information found in the database.",
            question=transcribed_text,
            language=language,
        )
        answer = generate_response(prompt)
    except Exception as e:
        logger.error(f"LLM generation failed: {e}")
        answer = (
            "ಮಾಹಿತಿ ಲಭ್ಯವಿಲ್ಲ. ದಯವಿಟ್ಟು ಮತ್ತೆ ಪ್ರಯತ್ನಿಸಿ."
            if language == "kannada"
            else "Information unavailable. Please try again."
        )
    llm_elapsed = round(time.time() - llm_start, 2)
    logger.info(f"LLM generation done in {llm_elapsed}s")

    # -------------------------------------------------------
    # STEP 5 — Text to Speech
    # -------------------------------------------------------
    tts_start = time.time()
    tts_result = text_to_speech(answer, language=language)
    tts_elapsed = round(time.time() - tts_start, 2)

    if not tts_result["success"]:
        logger.warning(f"TTS failed: {tts_result.get('error')} — returning text-only response")

    logger.info(f"TTS done in {tts_elapsed}s | path={tts_result.get('audio_path')}")

    # -------------------------------------------------------
    # STEP 6 — Cleanup & Return
    # -------------------------------------------------------
    _safe_cleanup(audio_file_path, cleanup_input)

    total_elapsed = round(time.time() - pipeline_start, 2)
    logger.info(f"Voice pipeline complete in {total_elapsed}s")

    return {
        "success": True,
        "language": language,
        "confidence": confidence,
        "transcribed_text": transcribed_text,
        "answer": answer,
        "audio_response_path": tts_result.get("audio_path"),
        "tts_success": tts_result["success"],
        "timing": {
            "stt_seconds": stt_elapsed,
            "rag_seconds": rag_elapsed,
            "llm_seconds": llm_elapsed,
            "tts_seconds": tts_elapsed,
            "total_seconds": total_elapsed,
        },
        "sources_count": len(docs),
        "error": None,
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
        "timing": {},
        "sources_count": 0,
        "error": error,
        "failed_stage": stage,
    }
