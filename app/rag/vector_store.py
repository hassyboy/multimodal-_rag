from langchain_community.vectorstores import Chroma
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain.schema import Document
from typing import List
from app.core.config import settings
from app.rag.embeddings import get_embeddings_model
from app.core.logger import get_logger

logger = get_logger(__name__)

def get_vector_store(embeddings: HuggingFaceEmbeddings = None) -> Chroma:
    """
    Initialize and return the ChromaDB vector store.
    """
    if embeddings is None:
        embeddings = get_embeddings_model()
        
    vector_store = Chroma(
        collection_name=settings.COLLECTION_NAME,
        embedding_function=embeddings,
        persist_directory=settings.CHROMA_DB_PATH
    )
    return vector_store

def add_documents_to_store(documents: List[Document], vector_store: Chroma = None):
    """
    Add a list of document chunks to the ChromaDB vector store.
    """
    if vector_store is None:
        vector_store = get_vector_store()
        
    logger.info(f"Adding {len(documents)} chunks to ChromaDB at {settings.CHROMA_DB_PATH} in collection {settings.COLLECTION_NAME}")
    vector_store.add_documents(documents)
    # Chroma persists automatically in recent versions of langchain/chromadb when configured with persist_directory
    logger.info("Successfully added documents to vector store.")
