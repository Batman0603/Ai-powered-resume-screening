from __future__ import annotations
import re
from typing import List

def clean_text(t: str) -> str:
    t = t.replace("\x00", " ")
    t = re.sub(r"[ \t]+", " ", t)
    t = re.sub(r"\n{3,}", "\n\n", t)
    return t.strip()

def naive_sections(text: str) -> dict:
    # very simple section splitter by common headings
    sections = {
        "skills": "",
        "experience": "",
        "projects": "",
        "education": "",
        "summary": ""
    }
    # lower + marker split
    lower = text.lower()
    def cut(head):
        i = lower.find(head)
        return i if i >= 0 else None

    anchors = {
        "skills": ["skills", "technical skills", "key skills"],
        "experience": ["experience", "work experience", "employment"],
        "projects": ["projects", "personal projects"],
        "education": ["education", "academic"],
        "summary": ["summary", "profile", "about"]
    }

    # greedy approach: for each anchor, slice between its index and the next anchor
    points = []
    for key, keys in anchors.items():
        for k in keys:
            i = cut(k)
            if i is not None:
                points.append((i, key))
                break
    points = sorted(points, key=lambda x: x[0])
    if not points:
        sections["summary"] = text
        return sections

    for idx, (start_i, key) in enumerate(points):
        end_i = points[idx+1][0] if idx+1 < len(points) else len(text)
        sections[key] = text[start_i:end_i]

    return {k: v.strip() for k, v in sections.items()}

def chunk_text(text: str, max_chars: int = 700) -> List[str]:
    # simple paragraph chunks capped at ~700 chars
    paras = [p.strip() for p in re.split(r"\n\s*\n", text) if p.strip()]
    chunks, buf = [], ""
    for p in paras:
        if len(buf) + len(p) + 1 <= max_chars:
            buf = (buf + "\n" + p).strip()
        else:
            if buf:
                chunks.append(buf)
            buf = p
    if buf:
        chunks.append(buf)
    # ensure at least one chunk
    return chunks if chunks else [text[:max_chars]]
