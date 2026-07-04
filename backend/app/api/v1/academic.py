"""Academic data retrieval endpoint."""

from __future__ import annotations

from fastapi import APIRouter, Depends

from app.core.security import get_current_user
from app.models.user import User
from app.schemas.copilot import CopilotChatRequest, CopilotChatResponse
from app.services.academic.service import AcademicQueryService, get_academic_query_service

router = APIRouter(prefix="/academic", tags=["academic"])


@router.post("/chat", response_model=CopilotChatResponse)
def chat(
    payload: CopilotChatRequest,
    current_user: User = Depends(get_current_user),
    academic_service: AcademicQueryService = Depends(get_academic_query_service),
) -> CopilotChatResponse:
    """Return a grounded answer from the authenticated student's academic data."""

    return academic_service.answer(
        message=payload.message,
        current_user=current_user,
        conversation_id=payload.conversation_id,
    )
