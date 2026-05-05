#LLooker a RAG Document API scanner
 
A production-ready REST API that lets you upload documents and ask questions about them using Retrieval-Augmented Generation (RAG).
 
## How it works
 
1. Upload a PDF via `/ingest` — the document is split into chunks, converted to vector embeddings, and stored in PostgreSQL
2. Ask a question via `/query` — the question is embedded, semantically searched against stored chunks, and answered by a local LLM
## Tech Stack
 
- **FastAPI** — REST API framework
- **PostgreSQL + pgvector** — vector storage and semantic search
- **Ollama** — local LLM inference (llama3.2 + nomic-embed-text)
- **LangChain** — document chunking
- **Docker** — containerized deployment
## Architecture
 
```
User Request
     ↓
FastAPI (port 8000)
     ↓
PostgreSQL + pgvector (port 5432)
     ↓
Ollama (local LLM + embeddings)
```
 
## Prerequisites
 
- Docker Desktop
- Ollama installed and running with the following models:
```bash
ollama pull llama3.2
ollama pull nomic-embed-text
```
 
## Running the project
 
1. Clone the repository:
```bash
git clone https://github.com/AchrafAbdelaziz/rag-document-api.git
cd rag-document-api
```
 
2. Start Ollama:
```bash
ollama serve
```
 
3. Start the API and database:
```bash
docker compose up --build
```
 
4. Open API docs:
```
http://localhost:8000/docs
```
 
## API Endpoints
 
### POST /ingest
Upload a PDF document to be processed and stored.
 
**Request:** multipart/form-data with a PDF file
 
**Response:**
```json
{
  "message": "Successfully ingested document.pdf",
  "chunks": 6
}
```
 
### POST /query
Ask a question about your uploaded documents.
 
**Request:**
```json
{
  "question": "Ask a question about your PDF file"
}
```
 
**Response:**
```json
{
  "question": "question ?",
  "answer": "Get your answer !!",
  "sources": ["document.pdf"]
}
```
 
## Project Structure
 
```
├── app/
│   ├── db/
│   │   ├── models.py        # Database table definitions
│   │   └── session.py       # Database connection
│   ├── routes/
│   │   ├── ingest.py        # PDF ingestion endpoint
│   │   └── query.py         # RAG query endpoint
│   └── services/
├── main.py                  # FastAPI entry point
├── Dockerfile               # API container
├── docker-compose.yml       # Full stack orchestration
└── requirements.txt
```
