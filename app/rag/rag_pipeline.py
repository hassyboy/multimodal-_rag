from app.rag.retriever import retrieve_documents
from app.rag.prompt_builder import get_rag_prompt
from app.llm.llm_service import generate_response
from app.core.logger import get_logger
from typing import Tuple, List
from langchain.schema import Document

logger = get_logger(__name__)

def run_rag_pipeline(question: str, language: str = "english") -> Tuple[str, List[Document]]:
    """
    Execute the RAG pipeline for a given question and language.
    Returns the generated answer and the source documents used.
    """
    logger.info(f"Running RAG pipeline for question in {language}")
    
    # Step 1: Retrieve relevant documents
    docs = retrieve_documents(question)
    
    # Step 2: Prepare context
    context = "\n\n".join([doc.page_content for doc in docs])
    
    # Step 3: Build prompt
    prompt_template = get_rag_prompt()
    prompt = prompt_template.format(context=context, question=question, language=language)
    
    # Step 4: Generate response from LLM
    answer = generate_response(prompt)
    
    return answer, docs
