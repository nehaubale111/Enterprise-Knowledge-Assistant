# backend/app/services/vector_store.py
from pathlib import Path
from typing import List, Tuple

import faiss
import numpy as np

from app.core.logger import logger

VECTOR_STORE_PATH = Path("faiss_index.bin")
METADATA_PATH = Path("faiss_metadata.npy")


class VectorStore:
    def __init__(self):
        self.index = None
        self.metadata = []  # list of (chunk_id,)
        self._load()

    def _load(self):
        if VECTOR_STORE_PATH.exists() and METADATA_PATH.exists():
            logger.info("Loading existing FAISS index...")
            self.index = faiss.read_index(str(VECTOR_STORE_PATH))
            self.metadata = np.load(METADATA_PATH, allow_pickle=True).tolist()
        else:
            self.index = None
            self.metadata = []

    def _save(self):
        if self.index is not None:
            faiss.write_index(self.index, str(VECTOR_STORE_PATH))
            np.save(METADATA_PATH, np.array(self.metadata, dtype=object))

    def add_embeddings(self, embeddings: np.ndarray, chunk_ids: List[int]):
        embeddings = embeddings.astype("float32")
        d = embeddings.shape[1]

        if self.index is None:
            self.index = faiss.IndexFlatIP(d)

        # normalize for cosine similarity
        faiss.normalize_L2(embeddings)

        self.index.add(embeddings)
        self.metadata.extend([(cid,) for cid in chunk_ids])
        self._save()

    def search(
        self, query_embedding: np.ndarray, top_k: int = 5
    ) -> List[Tuple[int, float]]:
        if self.index is None or len(self.metadata) == 0:
            return []

        query_embedding = query_embedding.astype("float32")
        faiss.normalize_L2(query_embedding)

        D, I = self.index.search(query_embedding, top_k)
        results = []
        for idx, score in zip(I[0], D[0]):
            if idx == -1:
                continue
            chunk_id = self.metadata[idx][0]
            results.append((chunk_id, float(score)))
        return results


vector_store = VectorStore()
