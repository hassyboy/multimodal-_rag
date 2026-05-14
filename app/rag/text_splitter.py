from langchain_text_splitters import RecursiveCharacterTextSplitter
import uuid
from typing import List
from langchain_core.documents import Document
from app.core.constants import DEFAULT_CHUNK_SIZE, DEFAULT_CHUNK_OVERLAP

def split_documents(documents: List[Document], chunk_size: int = DEFAULT_CHUNK_SIZE, chunk_overlap: int = DEFAULT_CHUNK_OVERLAP) -> List[Document]:
    """
    Split a list of LangChain Documents into smaller chunks and enrich with chunk_id metadata.
    """
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=chunk_size,
        chunk_overlap=chunk_overlap,
        separators=["\n\n", "\n", " ", ""]
    )
    
    chunks = text_splitter.split_documents(documents)
    
    # Enrich metadata with unique chunk IDs
    for chunk in chunks:
        chunk.metadata['chunk_id'] = str(uuid.uuid4())
        
    return chunks
