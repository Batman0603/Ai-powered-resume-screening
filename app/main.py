from __future__ import annotations
import os
from fastapi import FastAPI
from dotenv import load_dotenv
from app.db import init_db
from app.routes import health, resumes, jobs, screening
from app.services.embeddings import get_embedding_model
from app.services.indexer import FaissIndexer

load_dotenv()

def create_app() -> FastAPI:
    app = FastAPI(title="AI Resume Screening (RAG)", version="0.1.0")

    # DB init
    init_db()

    # Load embedding model once
    model = get_embedding_model()
    dim = model.get_sentence_embedding_dimension()

    # Prepare FAISS index
    app.state.indexer = FaissIndexer(dim=dim)

    # Routers
    app.include_router(health.router)
    app.include_router(resumes.router)
    app.include_router(jobs.router)
    app.include_router(screening.router)

    @app.get("/")
    def root():
        return {"service": "resume-screening-backend", "ok": True}

    return app

# Create a module-level app variable for uvicorn
app = create_app()

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app.main:app", host="127.0.0.1", port=8000, reload=True)
