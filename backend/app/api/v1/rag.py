# backend/app/api/v1/rag.py
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.api.v1.auth import get_current_user
from app.db.database import get_db
from app.models import QueryLog
from app.services.rag_service import (
    build_context_from_chunks,
    call_llm_openai,
    retrieve_relevant_chunks,
)

router = APIRouter(prefix="/rag", tags=["rag"])


class QueryRequest(BaseModel):
    question: str
    top_k: int = 5


class QueryResponse(BaseModel):
    answer: str
    sources: list[str]


@router.post("/query", response_model=QueryResponse)
def ask_rag(
    query: QueryRequest,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    if not query.question.strip():
        raise HTTPException(status_code=400, detail="Question cannot be empty")

    chunk_score_pairs = retrieve_relevant_chunks(
        db, query.question, top_k=query.top_k
    )
    if not chunk_score_pairs:
        answer = "I could not find relevant information in the knowledge base."
        sources = []
    else:
        context = build_context_from_chunks(chunk_score_pairs)
        answer = call_llm_openai(query.question, context)
        sources = list(
            {
                f"{c.document.original_filename} (page {c.page_number})"
                for c, _ in chunk_score_pairs
            }
        )

    log = QueryLog(
        user_id=current_user.id,
        question=query.question,
        answer=answer,
        sources=", ".join(sources),
    )
    db.add(log)
    db.commit()

    return QueryResponse(answer=answer, sources=sources)
