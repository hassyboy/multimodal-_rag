import os
import sys

# Ensure the app module is in the path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app.utils.file_utils import get_all_pdf_files
from app.rag.document_loader import load_pdf_documents
from app.rag.text_splitter import split_documents
from app.rag.vector_store import add_documents_to_store, get_vector_store
from app.core.logger import get_logger

logger = get_logger(__name__)

DATA_DIR = os.path.join(os.path.dirname(__file__), '..', 'data', 'govt_schemes')

def main():
    logger.info("Starting document ingestion process...")
    
    # Step 1: Find PDFs
    pdf_files = get_all_pdf_files(DATA_DIR)
    if not pdf_files:
        logger.warning(f"No PDF files found in {DATA_DIR}. Please add some PDFs to ingest.")
        return

    logger.info(f"Found {len(pdf_files)} PDF files to process.")
    
    # Initialize the vector store once
    vector_store = get_vector_store()

    # Step 2 & 3: Process each PDF and add to store
    for file_path in pdf_files:
        try:
            # Load
            docs = load_pdf_documents(file_path)
            if not docs:
                continue
                
            # Split
            chunks = split_documents(docs)
            logger.info(f"Split {file_path} into {len(chunks)} chunks.")
            
            # Store
            add_documents_to_store(chunks, vector_store)
            
            logger.info(f"Successfully ingested {file_path}")
        except Exception as e:
            logger.error(f"Failed to ingest {file_path}: {e}")

    logger.info("Ingestion process completed successfully.")

if __name__ == "__main__":
    main()
