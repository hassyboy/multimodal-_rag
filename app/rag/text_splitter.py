"""
Improved Text Splitter
Uses smarter chunking with scheme-aware separators for better RAG retrieval.
"""
from langchain_text_splitters import RecursiveCharacterTextSplitter
import uuid
from typing import List
from langchain_core.documents import Document
from app.core.logger import get_logger

logger = get_logger(__name__)

# Tuned for government scheme PDFs:
# - Larger chunks preserve full scheme descriptions
# - Higher overlap ensures cross-boundary context is captured
CHUNK_SIZE = 800
CHUNK_OVERLAP = 150

# Agriculture/scheme-specific separators — split on section breaks first
SEPARATORS = [
    "\n\n\n",   # Major section breaks
    "\n\n",     # Paragraph breaks
    "\n",       # Line breaks
    "। ",       # Devanagari/Kannada sentence end
    ". ",       # English sentence end
    ", ",       # Clause boundary
    " ",        # Word boundary
    "",         # Character fallback
]


def split_documents(
    documents: List[Document],
    chunk_size: int = CHUNK_SIZE,
    chunk_overlap: int = CHUNK_OVERLAP,
) -> List[Document]:
    """
    Split documents into overlapping chunks with rich metadata.
    Uses scheme-aware separators for better boundary detection.
    """
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=chunk_size,
        chunk_overlap=chunk_overlap,
        separators=SEPARATORS,
        length_function=len,
        is_separator_regex=False,
    )

    chunks = splitter.split_documents(documents)

    for i, chunk in enumerate(chunks):
        chunk.metadata["chunk_id"] = str(uuid.uuid4())
        chunk.metadata["chunk_index"] = i
        chunk.metadata["total_chunks"] = len(chunks)

    logger.info(
        f"Split {len(documents)} document(s) → {len(chunks)} chunks "
        f"(size={chunk_size}, overlap={chunk_overlap})"
    )
    return chunks
