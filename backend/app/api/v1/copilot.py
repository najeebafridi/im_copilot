"""Unified router entrypoint for grounded copilot chat."""

from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, Request, status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from sqlalchemy.orm import Session

from app.core.config import get_settings
from app.models.user import User
from app.schemas.copilot import CopilotChatRequest, CopilotChatResponse
from app.services.academic.service import AcademicQueryService, get_academic_query_service
from app.services.copilot.service import CopilotChatService, get_copilot_chat_service
from app.services.llm.exceptions import LLMConfigurationError, LLMProviderError
from app.services.router.graph_builder import RouterGraphBuilder
from app.services.router.router_service import RouterService, get_router_service

router = APIRouter(prefix="/copilot", tags=["copilot"])
oauth2_optional = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/login", auto_error=False)


@router.post("/chat", response_model=CopilotChatResponse, response_model_exclude_none=True)
def chat(
    payload: CopilotChatRequest,
    request: Request,
    token: str | None = Depends(oauth2_optional),
    router_service: RouterService = Depends(get_router_service),
    academic_service: AcademicQueryService = Depends(get_academic_query_service),
    copilot_service: CopilotChatService = Depends(get_copilot_chat_service),
) -> CopilotChatResponse:
    """Route the message to the appropriate existing backend service."""

    try:
        decision = router_service.route(payload.message)
        graph = RouterGraphBuilder()
        try:
            current_user = _resolve_current_user_if_needed(
                request=request,
                token=token,
                db=academic_service.db,
                selected_intent=decision.selected_intent,
            )
        except HTTPException as exc:
            if decision.selected_intent == "ACADEMIC" and exc.status_code == status.HTTP_401_UNAUTHORIZED:
                return graph.build_auth_required_response(decision)
            raise
        return graph.build_response(
            decision=decision,
            message=payload.message,
            conversation_id=payload.conversation_id,
            academic_service=academic_service,
            policy_service=copilot_service,
            current_user=current_user,
        )
    except LLMConfigurationError as exc:
        raise HTTPException(status_code=500, detail=str(exc)) from exc
    except LLMProviderError as exc:
        raise HTTPException(status_code=exc.status_code, detail=str(exc)) from exc


def _resolve_current_user_if_needed(
    request: Request,
    token: str | None,
    db: Session,
    selected_intent: str,
) -> User | None:
    """Resolve the authenticated user only when academic routing is selected."""

    if selected_intent != "ACADEMIC":
        return None

    if not token:
        authorization = request.headers.get("Authorization", "")
        scheme, _, header_token = authorization.partition(" ")
        if scheme.lower() == "bearer" and header_token:
            token = header_token

    if not token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication is required.",
            headers={"WWW-Authenticate": "Bearer"},
        )

    settings = get_settings()
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )

    try:
        payload = jwt.decode(token, settings.JWT_SECRET_KEY, algorithms=[settings.JWT_ALGORITHM])
        student_id: str | None = payload.get("sub")
        role: str | None = payload.get("role")
        if student_id is None or role is None:
            raise credentials_exception
    except JWTError as exc:
        raise credentials_exception from exc

    user = db.query(User).filter(User.student_id == student_id).first()
    if user is None:
        raise credentials_exception

    return user
