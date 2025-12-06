# backend/app/services/rag_service.py
from typing import List, Tuple

import numpy as np
import requests
from sqlalchemy.orm import Session

from app.core.config import settings
from app.core.logger import logger
from app.models import Chunk, Document
from .embedding_service import embed_texts
from .vector_store import vector_store


def add_chunks_to_vector_store(db: Session, chunks: List[Chunk]):
    texts = [c.text for c in chunks]
    ids = [c.id for c in chunks]
    embeddings = embed_texts(texts)
    vector_store.add_embeddings(np.array(embeddings), ids)


def retrieve_relevant_chunks(
    db: Session, query: str, top_k: int = 5
) -> List[Tuple[Chunk, float]]:
    embeddings = embed_texts([query])
    results = vector_store.search(np.array(embeddings), top_k=top_k)
    chunk_ids = [cid for cid, _ in results]
    if not chunk_ids:
        return []

    chunks = db.query(Chunk).filter(Chunk.id.in_(chunk_ids)).all()
    id_to_chunk = {c.id: c for c in chunks}
    return [(id_to_chunk[cid], score) for cid, score in results if cid in id_to_chunk]


def call_llm_openai(prompt: str, context: str) -> str:
    """
    Simple placeholder – you will plug your OpenAI / Gemini call here.
    For now, it just concatenates.
    """
    logger.info("Calling LLM (placeholder)...")
    return f"Answer (demo mode):\n\nBased on the following context:\n{context[:1000]}\n\nQuestion:\n{prompt}"


def build_context_from_chunks(chunk_score_pairs: List[Tuple[Chunk, float]]) -> str:
    contexts = []
    for chunk, score in chunk_score_pairs:
        doc: Document = chunk.document
        header = f"[{doc.original_filename} | page {chunk.page_number} | score={score:.2f}]"
        contexts.append(header + "\n" + chunk.text)
    return "\n\n---\n\n".join(contexts)
