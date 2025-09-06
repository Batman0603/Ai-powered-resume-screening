from __future__ import annotations
import os
from typing import Optional
from fastapi import APIRouter, UploadFile, File, Form, Depends, HTTPException
from sqlalchemy.orm import Session
from app.deps import get_db
from app.schemas import UploadResumeResponse
from app.services.files import save_upload
from app.services.parser import extract_text_auto
from app.services.preprocess import clean_text, chunk_text
from app.services.embeddings import embed_texts, get_embedding_model
from app.services.indexer import FaissIndexer
from app.models.orm import Candidate, ResumeChunk

router = APIRouter(prefix="/resumes", tags=["resumes"])

# lazy singletons in app.state (wired in main.py)
def _get_indexer(request):
    return request.app.state.indexer

def _get_model_dim():
    # ensure model is loaded to know embedding dim
    model = get_embedding_model()
    return model.get_sentence_embedding_dimension()

@router.post("", response_model=UploadResumeResponse)
async def upload_resume(
    request,
    file: UploadFile = File(...),
    name: Optional[str] = Form(None),
    email: Optional[str] = Form(None),
    phone: Optional[str] = Form(None),
    db: Session = Depends(get_db),
):
    # save file
    upload_dir = os.getenv("UPLOAD_DIR", "./data/uploads")
    contents = await file.read()
    path = save_upload(contents, file.filename, upload_dir)

    # parse -> text
    try:
        text = extract_text_auto(path)
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Failed to parse file: {e}")

    # clean + chunk
    text_clean = clean_text(text)
    chunks = chunk_text(text_clean, max_chars=700)

    # persist candidate
    cand = Candidate(name=name, email=email, phone=phone, resume_path=path, resume_text=text_clean)
    db.add(cand)
    db.commit()
    db.refresh(cand)

    # embed + index
    vecs = embed_texts(chunks)  # normalized float32
    indexer: FaissIndexer = request.app.state.indexer
    # create chunk rows first
    chunk_rows = []
    for c in chunks:
        rc = ResumeChunk(candidate_id=cand.id, chunk_text=c, index_id=-1)
        db.add(rc)
        db.flush()  # get rc.id
        chunk_rows.append(rc)
    db.commit()
    vector_ids = indexer.add(vecs, candidate_id=cand.id, chunk_ids=[rc.id for rc in chunk_rows])

    # backfill index_id
    for rc, vid in zip(chunk_rows, vector_ids):
        rc.index_id = vid
    db.commit()

    return UploadResumeResponse(candidate_id=cand.id, name=cand.name, email=cand.email)
