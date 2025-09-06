from __future__ import annotations
import os, uuid
from pathlib import Path

def ensure_dir(path: str):
    Path(path).mkdir(parents=True, exist_ok=True)

def save_upload(file_bytes: bytes, filename: str, upload_dir: str) -> str:
    ensure_dir(upload_dir)
    ext = Path(filename).suffix or ".bin"
    safe = f"{uuid.uuid4().hex}{ext}"
    out = Path(upload_dir) / safe
    with open(out, "wb") as f:
        f.write(file_bytes)
    return str(out)
