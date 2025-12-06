# backend/app/api/v1/documents.py
from pathlib import Path
from typing import List

from fastapi import APIRouter, Depends, File, HTTPException, UploadFile
from sqlalchemy.orm import Session

from app.api.v1.auth import get_current_admin, get_current_user
from app.core.logger import logger
from app.db.database import get_db
from app.models import Chunk, Document
from app.services.chunking import chunk_text
from app.services.rag_service import add_chunks_to_vector_store
from app.services.text_extraction import extract_text

router = APIRouter(prefix="/documents", tags=["documents"])

UPLOAD_DIR = Path("uploaded_docs")
UPLOAD_DIR.mkdir(exist_ok=True)


@router.post("/upload")
def upload_document(
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user=Depends(get_current_admin),
):
    suffix = Path(file.filename).suffix.lower()
    allowed = [".pdf", ".docx", ".pptx", ".xlsx", ".xls"]
    if suffix not in allowed:
        raise HTTPException(status_code=400, detail="Unsupported file type")

    stored_path = UPLOAD_DIR / file.filename
    with stored_path.open("wb") as f:
        f.write(file.file.read())

    doc = Document(
        original_filename=file.filename,
        stored_path=str(stored_path),
        content_type=file.content_type,
        uploaded_by_id=current_user.id,
    )
    db.add(doc)
    db.commit()
    db.refresh(doc)

    logger.info(f"Extracting text from {stored_path}")
    pages = extract_text(stored_path, file.content_type)

    chunks_to_add: List[Chunk] = []
    for page_text, page_no in pages:
        for idx, chunk in enumerate(chunk_text(page_text)):
            c = Chunk(
                document_id=doc.id,
                text=chunk,
                page_number=page_no,
                chunk_index=idx,
            )
            db.add(c)
            db.flush()
            chunks_to_add.append(c)

    db.commit()
    add_chunks_to_vector_store(db, chunks_to_add)

    return {"message": "File uploaded and indexed", "document_id": doc.id}


@router.get("/", response_model=list)
def list_documents(
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    docs = db.query(Document).all()
    return [
        {
            "id": d.id,
            "filename": d.original_filename,
            "uploaded_by": d.uploaded_by_id,
            "created_at": d.created_at,
        }
        for d in docs
    ]
