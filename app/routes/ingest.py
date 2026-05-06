import re
from fastapi import APIRouter, HTTPException, UploadFile, File, Depends
from sqlalchemy.orm import Session
from app.db.session import get_db
from app.db.models import DocumentChunk
import ollama
from pypdf import PdfReader
from langchain_text_splitters import RecursiveCharacterTextSplitter
import io
import os
ollama_client = ollama.Client(host=os.getenv("OLLAMA_HOST", "http://localhost:11434"))
router = APIRouter()

def extract_text_from_pdf(file_bytes: bytes) -> str:
    reader = PdfReader(io.BytesIO(file_bytes))
    text = ""
    for page in reader.pages:
        extracted = page.extract_text() or ""
        # Remove non-printable and non-ASCII characters
        extracted = re.sub(r'[^\x20-\x7E\n]', '', extracted)
        # Collapse multiple spaces and blank lines
        extracted = re.sub(r' +', ' ', extracted)
        extracted = re.sub(r'\n{3,}', '\n\n', extracted)
        text += extracted.strip() + "\n"
    return text

def chunk_text(text: str):
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=500,
        chunk_overlap=50
    )
    return splitter.split_text(text)

def get_embedding(text: str):
    response = ollama_client.embeddings(
        model="nomic-embed-text",
        prompt=text
    )
    return response["embedding"]

@router.post("/ingest")
async def ingest_document(file: UploadFile = File(...),db: Session = Depends(get_db)):
    if not file.filename.endswith(".pdf"):
        raise HTTPException(
            status_code=400,
            detail="Only PDF files are supported"
        )
    
    contents = await file.read()
    if len(contents) > 10 * 1024 * 1024:
        raise HTTPException(
            status_code=400,
            detail="File size exceeds 10MB limit"
        )
    try:
        text = extract_text_from_pdf(contents)
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail="Error occurred while extracting text from PDF"
        )
    if not text.strip():
        raise HTTPException(
            status_code=422,
            detail="No text could be extracted from this PDF"
        )

    chunks = chunk_text(text)
    try:
        for chunk in chunks:
            embedding = get_embedding(chunk)
            doc_chunk = DocumentChunk(
                filename=file.filename,
                content=chunk,
                embedding=embedding
            )
            db.add(doc_chunk)
    except  Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=500,
            detail=f"Failed to store document: {str(e)}"
        )
    db.commit()

    return {
        "message": f"Successfully ingested {file.filename}",
        "chunks": len(chunks)
    }