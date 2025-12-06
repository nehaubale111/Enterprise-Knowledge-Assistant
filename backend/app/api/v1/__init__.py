# backend/app/api/v1/__init__.py
from fastapi import APIRouter

from . import auth, documents, rag

api_router = APIRouter()
api_router.include_router(auth.router)
api_router.include_router(documents.router)
api_router.include_router(rag.router)
