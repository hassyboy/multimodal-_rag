"""
POST /upload-pdf — Upload government scheme PDF and ingest into ChromaDB
POST /process-documents — Re-run ingestion on all existing PDFs
GET /documents — List all uploaded PDFs
"""
import os
from pathlib import Path
from fastapi import APIRouter, UploadFile, File, HTTPException
from fastapi.responses import JSONResponse
from app.core.logger import get_logger

router = APIRouter()
logger = get_logger(__name__)

# Always resolve relative to the project root (where run.py lives)
PROJECT_ROOT = Path(__file__).resolve().parents[3]
SCHEMES_DIR = str(PROJECT_ROOT / "data" / "govt_schemes")


@router.post("/upload-pdf")
async def upload_pdf(file: UploadFile = File(..., description="Government scheme PDF")):
    """
    Upload a government scheme PDF to the data directory.
    After upload, call /process-documents to ingest into ChromaDB.
    """
    if not file.filename.endswith(".pdf"):
        raise HTTPException(status_code=400, detail="Only PDF files are accepted.")

    os.makedirs(SCHEMES_DIR, exist_ok=True)
    dest_path = os.path.join(SCHEMES_DIR, file.filename)

    try:
        content = await file.read()
        if len(content) == 0:
            raise HTTPException(status_code=400, detail="Uploaded file is empty.")

        with open(dest_path, "wb") as f:
            f.write(content)

        size_kb = round(len(content) / 1024, 1)
        logger.info(f"PDF uploaded: {file.filename} ({size_kb} KB)")

        return JSONResponse({
            "success": True,
            "filename": file.filename,
            "size_kb": size_kb,
            "message": f"'{file.filename}' uploaded successfully. Click 'Process Documents' to ingest.",
        })
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Upload failed for {file.filename}: {e}")
        raise HTTPException(status_code=500, detail=f"Upload failed: {str(e)}")


@router.post("/process-documents")
async def process_documents():
    """
    Ingest all PDFs in data/govt_schemes/ into ChromaDB.
    This rebuilds the vector store from all available documents.
    """
    try:
        from app.rag.document_loader import load_pdf_documents
        from app.rag.text_splitter import split_documents
        from app.rag.vector_store import add_documents_to_store, get_vector_store

        pdf_files = [
            f for f in os.listdir(SCHEMES_DIR)
            if f.endswith(".pdf") and not f.startswith(".")
        ] if os.path.exists(SCHEMES_DIR) else []

        if not pdf_files:
            return JSONResponse({
                "success": False,
                "message": "No PDF files found in data/govt_schemes/. Please upload PDFs first.",
                "processed": 0,
            })

        logger.info(f"Processing {len(pdf_files)} PDF(s)...")

        all_chunks = []
        failed = []

        for pdf_file in pdf_files:
            pdf_path = os.path.join(SCHEMES_DIR, pdf_file)
            try:
                docs = load_pdf_documents(pdf_path)
                chunks = split_documents(docs)
                all_chunks.extend(chunks)
                logger.info(f"  {pdf_file} → {len(chunks)} chunks")
            except Exception as e:
                logger.error(f"Failed to process {pdf_file}: {e}")
                failed.append(pdf_file)

        if all_chunks:
            add_documents_to_store(all_chunks)

        return JSONResponse({
            "success": True,
            "processed_files": [f for f in pdf_files if f not in failed],
            "failed_files": failed,
            "total_chunks": len(all_chunks),
            "message": f"Ingested {len(all_chunks)} chunks from {len(pdf_files) - len(failed)} PDF(s).",
        })

    except Exception as e:
        logger.error(f"Document processing failed: {e}")
        raise HTTPException(status_code=500, detail=f"Processing failed: {str(e)}")


@router.get("/documents")
async def list_documents():
    """List all uploaded PDF files."""
    try:
        if not os.path.exists(SCHEMES_DIR):
            return {"files": [], "count": 0}

        files = []
        for f in os.listdir(SCHEMES_DIR):
            if f.endswith(".pdf") and not f.startswith("."):
                path = os.path.join(SCHEMES_DIR, f)
                files.append({
                    "filename": f,
                    "size_kb": round(os.path.getsize(path) / 1024, 1),
                })

        return {"files": files, "count": len(files)}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
