from langchain_community.document_loaders import PyPDFLoader
from typing import List
from langchain_core.documents import Document
from app.core.logger import get_logger

logger = get_logger(__name__)

def load_pdf_documents(file_path: str) -> List[Document]:
    """
    Load a single PDF file and extract its content as LangChain Documents.
    """
    try:
        logger.info(f"Loading PDF document: {file_path}")
        loader = PyPDFLoader(file_path)
        documents = loader.load()
        logger.info(f"Successfully loaded {len(documents)} pages from {file_path}")
        return documents
    except Exception as e:
        logger.error(f"Error loading PDF document {file_path}: {e}")
        return []
