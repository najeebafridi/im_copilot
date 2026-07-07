"""Top-level API router."""

from fastapi import APIRouter

from app.api.v1.auth import router as auth_router
from app.api.v1.academic import router as academic_router
from app.api.v1.copilot import router as copilot_router
from app.api.v1.chat import router as chat_router
from app.api.v1.documents import router as documents_router
from app.api.v1.llm import router as llm_router
from app.api.v1.health import router as health_router
from app.api.v1.rag import router as rag_router

api_router = APIRouter()
api_router.include_router(health_router)
api_router.include_router(auth_router)
api_router.include_router(chat_router)
api_router.include_router(academic_router)
api_router.include_router(documents_router)
api_router.include_router(rag_router)
api_router.include_router(llm_router)
api_router.include_router(copilot_router)
