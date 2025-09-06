from __future__ import annotations
import os
from sentence_transformers import SentenceTransformer
import numpy as np

_model = None

def get_embedding_model():
    global _model
    if _model is None:
        model_name = os.getenv("EMBEDDING_MODEL", "sentence-transformers/all-MiniLM-L6-v2")
        _model = SentenceTransformer(model_name)
    return _model

def embed_texts(texts: list[str]) -> np.ndarray:
    model = get_embedding_model()
    vecs = model.encode(texts, normalize_embeddings=True, convert_to_numpy=True, show_progress_bar=False)
    return vecs.astype("float32")
