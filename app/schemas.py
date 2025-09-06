from __future__ import annotations
from pydantic import BaseModel, Field
from typing import List, Optional

class UploadResumeResponse(BaseModel):
    candidate_id: int
    name: Optional[str] = None
    email: Optional[str] = None

class CreateJobRequest(BaseModel):
    title: Optional[str] = None
    description: str = Field(..., min_length=20)

class CreateJobResponse(BaseModel):
    job_id: int

class ScreenRequest(BaseModel):
    job_id: int
    top_k: int = 10

class ScreenedCandidate(BaseModel):
    candidate_id: int
    score: float
    matched_skills: List[str]
    missing_skills: List[str]
    summary: str

class ScreenResponse(BaseModel):
    job_id: int
    results: List[ScreenedCandidate]
