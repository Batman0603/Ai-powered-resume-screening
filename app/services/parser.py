from __future__ import annotations
from pathlib import Path
import fitz  # PyMuPDF
import docx

def extract_text_from_pdf(path: str) -> str:
    doc = fitz.open(path)
    texts = []
    for page in doc:
        texts.append(page.get_text("text"))
    doc.close()
    return "\n".join(texts)

def extract_text_from_docx(path: str) -> str:
    d = docx.Document(path)
    return "\n".join(p.text for p in d.paragraphs)

def extract_text_auto(path: str) -> str:
    ext = Path(path).suffix.lower()
    if ext.endswith(".pdf"):
        return extract_text_from_pdf(path)
    elif ext.endswith(".docx"):
        return extract_text_from_docx(path)
    else:
        # brute fallback: try PDF first then DOCX
        try:
            return extract_text_from_pdf(path)
        except Exception:
            return extract_text_from_docx(path)
