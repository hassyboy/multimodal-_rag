from langchain_community.embeddings import HuggingFaceEmbeddings
from app.core.constants import EMBEDDING_MODEL_NAME
from app.core.logger import get_logger

logger = get_logger(__name__)

def get_embeddings_model() -> HuggingFaceEmbeddings:
    """
    Initialize and return the HuggingFace embeddings model.
    Uses 'intfloat/multilingual-e5-small' by default.
    """
    logger.info(f"Initializing embedding model: {EMBEDDING_MODEL_NAME}")
    try:
        model_kwargs = {'device': 'cpu'} # Use CPU by default, can be extended for GPU
        encode_kwargs = {'normalize_embeddings': True} # Required for e5 models usually
        embeddings = HuggingFaceEmbeddings(
            model_name=EMBEDDING_MODEL_NAME,
            model_kwargs=model_kwargs,
            encode_kwargs=encode_kwargs
        )
        return embeddings
    except Exception as e:
        logger.error(f"Failed to initialize embedding model: {e}")
        raise
