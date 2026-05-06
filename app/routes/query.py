from fastapi  import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.db.session import get_db
from app.db.models import DocumentChunk
from pydantic import BaseModel
import ollama
import os
ollama_client = ollama.Client(host=os.getenv("OLLAMA_HOST", "http://localhost:11434"))
router = APIRouter()

class QueryRequest(BaseModel):
    question: str
    
@router.post("/query")
def query_document(request:QueryRequest, db: Session = Depends(get_db)):
    if not request.question.strip():
        raise HTTPException(
            status_code=400,
            detail="Question cannot be empty"
        )
    doc_count = db.query(DocumentChunk).count()
    if doc_count == 0:
        raise HTTPException(
            status_code=404,
            detail="No documents found — please ingest a document first"
        )
    try:
        response = ollama_client.embeddings(
            model="nomic-embed-text",
            prompt=request.question
        )
        question_embedding = response['embedding']
    except Exception:
        raise HTTPException(
            status_code=503,
            detail="Embedding service unavailable — make sure Ollama is running"
        )

    
    try:
        chunks = db.query(DocumentChunk).order_by(DocumentChunk.embedding.cosine_distance(question_embedding)).limit(3).all()
    except Exception:
        raise HTTPException(
            status_code=500,
            detail="Failed document search"
        )
    context = "\n\n".join([chunk.content for chunk in chunks])
    try:
        llm_response = ollama_client.chat(
        model = "llama3.2",
        messages = [
        {"role": "system", "content": "You are a helpful assistant that answers questions based on the provided context."},
        {"role": "user", "content": f"Context: {context}\n\nQuestion: {request.question}"}
        ]  
        )
    except Exception:
        raise HTTPException(
            status_code=503,
            detail="LLM service unavailable — make sure Ollama is running"
            )
    return {
        "question": request.question,
        "answer": llm_response['message']['content'],
        "sources": [chunk.filename for chunk in chunks]
        
    }