from __future__ import annotations
import os, json, threading
import numpy as np
import faiss

_DEFAULT_INDEX_PATH = os.getenv("FAISS_INDEX_PATH", "./data/indices/resume_chunks.faiss")
_DEFAULT_META_PATH  = os.getenv("FAISS_META_PATH", "./data/indices/resume_chunks_meta.json")

class FaissIndexer:
    def __init__(self, dim: int, index_path: str = _DEFAULT_INDEX_PATH, meta_path: str = _DEFAULT_META_PATH):
        self.dim = dim
        self.index_path = index_path
        self.meta_path = meta_path
        self._lock = threading.Lock()
        self._id_counter = 0
        self._meta = {}  # str(id) -> {"candidate_id": int, "chunk_id": int}
        self._index = None
        self._load()

    def _load(self):
        os.makedirs(os.path.dirname(self.index_path), exist_ok=True)
        if os.path.exists(self.index_path):
            self._index = faiss.read_index(self.index_path)
        else:
            self._index = faiss.IndexFlatIP(self.dim)
        if os.path.exists(self.meta_path):
            with open(self.meta_path, "r", encoding="utf-8") as f:
                self._meta = json.load(f)
            if self._meta:
                self._id_counter = max(int(k) for k in self._meta.keys()) + 1

    def _persist(self):
        faiss.write_index(self._index, self.index_path)
        with open(self.meta_path, "w", encoding="utf-8") as f:
            json.dump(self._meta, f)

    def add(self, vecs: np.ndarray, candidate_id: int, chunk_ids: list[int]) -> list[int]:
        assert vecs.shape[0] == len(chunk_ids)
        n = vecs.shape[0]
        with self._lock:
            start = self._id_counter
            ids = list(range(start, start + n))
            self._id_counter += n
            # FAISS IndexFlatIP doesn't support add_with_ids by default; we simulate mapping in meta
            self._index.add(vecs)
            for i, cid in zip(ids, chunk_ids):
                self._meta[str(i)] = {"candidate_id": int(candidate_id), "chunk_id": int(cid)}
            self._persist()
        return ids

    def search(self, query_vecs: np.ndarray, top_k: int = 10):
        with self._lock:
            D, I = self._index.search(query_vecs, top_k)
        # map ids to metadata
        meta_rows = []
        for row in I:
            meta_rows.append([self._meta.get(str(i), None) if i >=0 else None for i in row])
        return D, I, meta_rows
