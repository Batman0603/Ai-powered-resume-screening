from __future__ import annotations
from typing import Dict
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import select
from app.deps import get_db
from app.schemas import ScreenRequest, ScreenResponse, ScreenedCandidate
from app.models.orm import Job, Candidate, ResumeChunk, ScreeningResult
from app.services.embeddings import embed_texts
from app.services.indexer import FaissIndexer
from app.services.rag import aggregate_scores, build_explanation

router = APIRouter(prefix="/screen", tags=["screening"])

@router.post("", response_model=ScreenResponse)
def screen(
    request,
    payload: ScreenRequest,
    db: Session = Depends(get_db)
):
    job = db.get(Job, payload.job_id)
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")

    indexer: FaissIndexer = request.app.state.indexer
    qvec = embed_texts([job.description])  # (1, d)
    D, I, meta_rows = indexer.search(qvec, top_k=max(10, payload.top_k))

    # build lookup for chunk_id -> text
    chunk_ids = set()
    for row in meta_rows:
        for m in row:
            if m: chunk_ids.add(m["chunk_id"])
    if not chunk_ids:
        return ScreenResponse(job_id=job.id, results=[])

    chunks = (
        db.execute(
            select(ResumeChunk.id, ResumeChunk.candidate_id, ResumeChunk.chunk_text)
            .where(ResumeChunk.id.in_(chunk_ids))
        ).all()
    )
    chunk_lookup: Dict[int, str] = {row.id: row.chunk_text for row in chunks}

    agg = aggregate_scores(D, I, meta_rows, chunk_lookup, top_per_candidate=5)

    # fetch resume_text for each candidate once
    cids = list(agg.keys())
    candidates = db.execute(select(Candidate).where(Candidate.id.in_(cids))).scalars().all()
    cand_map = {c.id: c for c in candidates}

    results = []
    for cid, data in agg.items():
        c = cand_map[cid]
        matched, missing, summary = build_explanation(job.description, c.resume_text or "", data["context"])
        results.append(
            ScreenedCandidate(
                candidate_id=cid,
                score=round(float(data["score"]), 2),
                matched_skills=matched,
                missing_skills=missing,
                summary=summary,
            )
        )

        # (optional) persist results row for history
        sr = ScreeningResult(
            job_id=job.id,
            candidate_id=cid,
            score=float(data["score"]),
            matched_skills_csv=",".join(matched),
            missing_skills_csv=",".join(missing),
            summary=summary
        )
        db.add(sr)
    db.commit()

    # sort by score desc and trim to top_k
    results = sorted(results, key=lambda r: r.score, reverse=True)[:payload.top_k]
    return ScreenResponse(job_id=job.id, results=results)
