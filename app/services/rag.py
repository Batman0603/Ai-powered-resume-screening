from __future__ import annotations
from typing import Dict, List, Tuple
import numpy as np
from collections import defaultdict
from app.services.skills import extract_skills, diff_skills

def aggregate_scores(
    D: np.ndarray, I: np.ndarray, meta_rows: List[List[dict]], chunks_lookup: Dict[int, str], top_per_candidate: int = 5
) -> Dict[int, dict]:
    """
    Group top chunks by candidate and compute a candidate-level score.
    """
    candidate_hits: Dict[int, list[Tuple[float, str]]] = defaultdict(list)
    for row_scores, row_idx, row_meta in zip(D, I, meta_rows):
        for score, idx, meta in zip(row_scores, row_idx, row_meta):
            if idx < 0 or not meta:
                continue
            cid = meta["candidate_id"]
            chunk_id = meta["chunk_id"]
            text = chunks_lookup.get(chunk_id, "")
            candidate_hits[cid].append((float(score), text))

    candidate_agg: Dict[int, dict] = {}
    for cid, hits in candidate_hits.items():
        hits = sorted(hits, key=lambda x: x[0], reverse=True)[:top_per_candidate]
        # simple candidate score = mean of top chunk scores scaled to 0-100
        score = max(0.0, min(100.0, float(np.mean([h[0] for h in hits]) * 100.0)))
        context = "\n---\n".join(h[1] for h in hits)
        candidate_agg[cid] = {"score": score, "context": context}
    return candidate_agg

def build_explanation(jd_text: str, resume_text: str, context: str) -> tuple[list[str], list[str], str]:
    req = extract_skills(jd_text)
    have = extract_skills(resume_text + "\n" + context)
    matched, missing = diff_skills(req, have)
    # short summary without external LLM
    lines = []
    if matched:
        lines.append(f"Strong in: {', '.join(matched)}.")
    if missing:
        lines.append(f"Missing/weak: {', '.join(missing)}.")
    if not lines:
        lines.append("General fit based on semantic similarity; no clear skill anchors found.")
    summary = " ".join(lines)
    return matched, missing, summary
