from typing import List
from langchain_core.documents import Document
from app.models.response_models import AskResponse, SourceItem

def format_ask_response(answer: str, docs: List[Document], language: str = "english") -> AskResponse:
    """
    Format the raw answer and LangChain Documents into a structured Pydantic response model.
    Also preserves metadata like source, page, and chunk_id.
    """
    sources = []
    for doc in docs:
        source_item = SourceItem(
            content=doc.page_content,
            metadata=doc.metadata
        )
        sources.append(source_item)
        
    return AskResponse(
        language=language,
        answer=answer,
        sources=sources
    )
