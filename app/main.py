from fastapi import FastAPI
from app.db.session import engine, Base

Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="RAG Document API",
    description="Upload PDFs and ask questions about them",
    version="1.0.0"
)

@app.get("/")
def root():
    return {"message": "RAG Document API is running"}