# AgriConnect AI Service

AgriConnect AI Service is an independent AI microservice backend designed to answer questions about agriculture government schemes. It uses a Retrieval-Augmented Generation (RAG) pipeline powered by FastAPI, ChromaDB, LangChain, and an Ollama-compatible LLM.

## Project Overview

This phase 1 project focuses strictly on building a modular, RAG-based backend system for answering questions about agriculture schemes by processing government scheme PDFs.

## Architecture

The application is built with a clean, modular architecture:
- **FastAPI**: Provides high-performance async REST API endpoints.
- **ChromaDB**: Serves as the persistent vector store for document embeddings.
- **LangChain**: Orchestrates the RAG pipeline.
- **intfloat/multilingual-e5-small**: Used for generating multilingual embeddings.
- **Ollama**: Connects to the local LLM (llama3 or gemma3) for generating grounded responses.

## Folder Structure

```
AgriConnect-AI-Service/
├── app/                  # Main application package
│   ├── api/routes/       # API endpoints (/ask, /health)
│   ├── core/             # Configuration and logging
│   ├── rag/              # RAG pipeline components (loaders, splitters, vector store)
│   ├── llm/              # LLM service and formatting
│   ├── models/           # Pydantic schemas for requests/responses
│   ├── services/         # Business logic
│   └── utils/            # Helper utilities
├── data/                 # Directory for storing PDFs and processed data
├── chroma_db/            # Persistent storage for ChromaDB
├── scripts/              # Scripts for document ingestion and DB maintenance
├── tests/                # Placeholder for future tests
├── .env                  # Environment variables
├── requirements.txt      # Python dependencies
├── run.py                # Uvicorn entrypoint
└── README.md             # This file
```

## Environment Setup

1. Clone or copy the project folder.
2. Create a virtual environment (optional but recommended):
   ```bash
   python -m venv venv
   # On Windows:
   venv\Scripts\activate
   # On macOS/Linux:
   source venv/bin/activate
   ```
3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
4. Ensure Ollama is installed on your system and running with your chosen model:
   ```bash
   ollama run llama3
   ```

## Configuration

Environment variables are managed via the `.env` file:
- `OLLAMA_BASE_URL`: URL of the Ollama instance (default: `http://localhost:11434`)
- `MODEL_NAME`: LLM model to use (default: `llama3`)
- `CHROMA_DB_PATH`: Path to store the vector database (default: `./chroma_db`)
- `COLLECTION_NAME`: ChromaDB collection name (default: `agri_schemes`)

## How to Ingest Documents

1. Place your agriculture scheme PDFs in the `data/govt_schemes/` directory.
2. Run the ingestion script:
   ```bash
   python scripts/ingest_documents.py
   ```
   This will read the PDFs, split them into chunks, generate embeddings, and store them in ChromaDB.

## How to Run the Server

Start the FastAPI application using the provided run script:
```bash
python run.py
```
The server will be available at `http://localhost:8000`. Automatic API documentation is at `http://localhost:8000/docs`.

## Example API Usage

### Health Check

```bash
curl -X 'GET' \
  'http://localhost:8000/health' \
  -H 'accept: application/json'
```

### Ask a Question

```bash
curl -X 'POST' \
  'http://localhost:8000/ask' \
  -H 'accept: application/json' \
  -H 'Content-Type: application/json' \
  -d '{
  "question": "What schemes exist for rice farmers in Karnataka?"
}'
```

## Future Roadmap

- Native Kannada language support
- Voice integration
- Personalized scheme recommendations
- OCR for image-based documents
- Extended Agriculture AI assistant capabilities
