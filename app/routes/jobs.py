from __future__ import annotations
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.deps import get_db
from app.schemas import CreateJobRequest, CreateJobResponse
from app.models.orm import Job
from app.services.preprocess import clean_text

router = APIRouter(prefix="/jobs", tags=["jobs"])

@router.post("", response_model=CreateJobResponse)
def create_job(payload: CreateJobRequest, db: Session = Depends(get_db)):
    job = Job(title=payload.title, description=clean_text(payload.description))
    db.add(job)
    db.commit()
    db.refresh(job)
    return CreateJobResponse(job_id=job.id)
