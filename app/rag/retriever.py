from langchain_community.vectorstores import Chroma
from typing import List
from langchain_core.documents import Document
from app.rag.vector_store import get_vector_store

def get_retriever(vector_store: Chroma = None, k: int = 4):
    """
    Get a retriever instance from the vector store.
    """
    if vector_store is None:
        vector_store = get_vector_store()
    
    return vector_store.as_retriever(search_kwargs={"k": k})

def retrieve_documents(query: str, retriever=None) -> List[Document]:
    """
    Retrieve documents relevant to the given query.
    """
    if retriever is None:
        retriever = get_retriever()
        
    return retriever.invoke(query)
