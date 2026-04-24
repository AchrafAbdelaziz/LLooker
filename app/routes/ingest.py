from fastapi import APIRouter, UploadFile, File, Depends
from sqlalchemy.orm import Session
from app.db.session import get_db
from app.db.models import DocumentChunk
import ollama
from pypdf import PdfReader
from langchain_text_splitters import RecursiveCharacterTextSplitter
import io

router = APIRouter()

def extract_text_from_pdf(file_bytes: bytes) -> str:
    reader = PdfReader(io.BytesIO(file_bytes))
    text = ""
    for page in reader.pages:
        text += page.extract_text() or ""
    return text

def chunk_text(text: str):
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=500,
        chunk_overlap=50
    )
    return splitter.split_text(text)

def get_embedding(text: str):
    response = ollama.embeddings(
        model="nomic-embed-text",
        prompt=text
    )
    return response["embedding"]

@router.post("/ingest")
async def ingest_document(
    file: UploadFile = File(...),
    db: Session = Depends(get_db)
):
    contents = await file.read()
    text = extract_text_from_pdf(contents)
    chunks = chunk_text(text)

    for chunk in chunks:
        embedding = get_embedding(chunk)
        doc_chunk = DocumentChunk(
            filename=file.filename,
            content=chunk,
            embedding=embedding
        )
        db.add(doc_chunk)

    db.commit()

    return {
        "message": f"Successfully ingested {file.filename}",
        "chunks": len(chunks)
    }