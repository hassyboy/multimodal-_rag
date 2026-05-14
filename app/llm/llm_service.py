from langchain_community.llms import Ollama
from app.core.config import settings
from app.core.logger import get_logger

logger = get_logger(__name__)

def get_llm() -> Ollama:
    """
    Initialize and return the Ollama LLM client.
    Always reads MODEL_NAME fresh from settings.
    """
    logger.info(f"Initializing Ollama LLM with model: {settings.MODEL_NAME} at {settings.OLLAMA_BASE_URL}")
    try:
        llm = Ollama(
            base_url=settings.OLLAMA_BASE_URL,
            model=settings.MODEL_NAME,
            temperature=0.1,
            timeout=120
        )
        return llm
    except Exception as e:
        logger.error(f"Error initializing Ollama: {e}")
        raise

def generate_response(prompt: str) -> str:
    """
    Generate a response using the LLM given a prompt.
    """
    try:
        model = get_llm()
        response = model.invoke(prompt)
        return response
    except Exception as e:
        logger.error(f"Error generating response from LLM: {str(e)}")
        return f"I apologize, but I encountered an error while trying to generate a response. Error: {str(e)}"
