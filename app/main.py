from fastapi import FastAPI
from app.db.session import engine, Base
import app.db.models
from app.routes.ingest import router as ingest_router

Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="RAG Document API",
    description="Upload PDFs and ask questions about them",
    version="1.0.0"
)

app.include_router(ingest_router)

@app.get("/")
def root():
    return {"message": "RAG Document API is running"}