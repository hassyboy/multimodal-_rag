"""
Improved RAG Retriever
Supports MMR-based diverse retrieval and configurable k for voice vs text queries.
"""
from langchain_community.vectorstores import Chroma
from langchain_core.documents import Document
from typing import List
from app.rag.vector_store import get_vector_store
from app.core.logger import get_logger

logger = get_logger(__name__)

DEFAULT_K = 5          # Retrieve top-5 chunks for better context coverage
VOICE_K = 4            # Slightly fewer for voice — keeps LLM prompt concise


def get_retriever(vector_store: Chroma = None, k: int = DEFAULT_K):
    """
    Get a retriever using MMR (Maximum Marginal Relevance) search.
    MMR balances relevance AND diversity — avoids returning duplicate/near-duplicate chunks.
    """
    if vector_store is None:
        vector_store = get_vector_store()

    return vector_store.as_retriever(
        search_type="mmr",              # More diverse results than plain similarity
        search_kwargs={
            "k": k,
            "fetch_k": k * 3,           # Candidate pool for MMR selection
            "lambda_mult": 0.7,         # 0=max diversity, 1=max relevance; 0.7 is balanced
        }
    )


def retrieve_documents(query: str, k: int = DEFAULT_K) -> List[Document]:
    """
    Retrieve top-k relevant documents for a query using MMR search.

    Args:
        query: Natural language query (Kannada or English)
        k: Number of documents to retrieve

    Returns:
        List of LangChain Document objects
    """
    try:
        retriever = get_retriever(k=k)
        docs = retriever.invoke(query)
        logger.info(f"Retrieved {len(docs)} docs for query: '{query[:60]}'")
        return docs
    except Exception as e:
        logger.error(f"Retrieval failed: {e}")
        return []


def retrieve_for_voice(query: str) -> List[Document]:
    """Retrieve with a smaller k optimized for voice pipeline (shorter context)."""
    return retrieve_documents(query, k=VOICE_K)
