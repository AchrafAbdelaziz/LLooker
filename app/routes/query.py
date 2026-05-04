from fastapi  import APIRouter, Depends
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
    
    response = ollama_client.embeddings(
        model="nomic-embed-text",
        prompt=request.question
    )
    question_embedding = response['embedding']
    
    chunks = db.query(DocumentChunk).order_by(DocumentChunk.embedding.cosine_distance(question_embedding)).limit(3).all()
    
    context = "\n\n".join([chunk.content for chunk in chunks])
    
    llm_response = ollama.chat(
     model = "llama3.2",
     messages = [
     {"role": "system", "content": "You are a helpful assistant that answers questions based on the provided context."},
     {"role": "user", "content": f"Context: {context}\n\nQuestion: {request.question}"}
     ]  
    )
    return {
        "question": request.question,
        "answer": llm_response['message']['content'],
        "sources": [chunk.filename for chunk in chunks]
        
    }