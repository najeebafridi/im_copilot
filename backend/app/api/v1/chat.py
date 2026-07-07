"""Conversation management endpoints."""

from __future__ import annotations

from dataclasses import dataclass

from fastapi import APIRouter, Depends, HTTPException, Request, status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from sqlalchemy.orm import Session

from app.core.config import get_settings
from app.core.database import get_db
from app.models.user import User
from app.schemas.conversation import (
    ConversationCreateRequest,
    ConversationCreateResponse,
    ConversationDeleteResponse,
    ConversationListResponse,
    ConversationMessageRequest,
    ConversationMessageResponse,
    ConversationResponse,
    ConversationSendResponse,
    ConversationStatusResponse,
    ConversationSummaryResponse,
)
from app.services.conversation.models import ConversationRecord
from app.services.conversation.service import (
    ConversationLimitError,
    ConversationNotFoundError,
    ConversationOwnershipError,
    get_conversation_service,
)

router = APIRouter(prefix="/chat", tags=["chat"])
oauth2_optional = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/login", auto_error=False)


@dataclass(slots=True)
class OwnerContext:
    """Resolved conversation owner."""

    owner_id: str
    owner_type: str


@router.post("/new", response_model=ConversationCreateResponse)
def create_conversation(
    request: Request,
    payload: ConversationCreateRequest | None = None,
    token: str | None = Depends(oauth2_optional),
    db: Session = Depends(get_db),
) -> ConversationCreateResponse:
    """Create a new conversation for the current owner."""

    owner = _resolve_owner(request, token, db)
    conversation = get_conversation_service().create_conversation(
        owner_id=owner.owner_id,
        owner_type=owner.owner_type,
    )
    return ConversationCreateResponse(
        conversation_id=conversation.conversation_id,
        title=conversation.title,
        type=conversation.conversation_type.value,
        status=conversation.status.value,
    )


@router.get("/list", response_model=ConversationListResponse)
def list_conversations(
    request: Request,
    token: str | None = Depends(oauth2_optional),
    db: Session = Depends(get_db),
) -> ConversationListResponse:
    """List conversations for the current owner."""

    owner = _resolve_owner(request, token, db)
    conversations = get_conversation_service().list_conversations(
        owner_id=owner.owner_id,
        owner_type=owner.owner_type,
    )
    return ConversationListResponse(conversations=[_to_summary_response(record) for record in conversations])


@router.post("/{conversation_id}/message", response_model=ConversationSendResponse)
def send_message(
    conversation_id: str,
    payload: ConversationMessageRequest,
    request: Request,
    token: str | None = Depends(oauth2_optional),
    db: Session = Depends(get_db),
) -> ConversationSendResponse:
    """Append the user message and a placeholder assistant reply."""

    owner = _resolve_owner(request, token, db)
    try:
        conversation, assistant_message = get_conversation_service().send_message(
            owner_id=owner.owner_id,
            owner_type=owner.owner_type,
            conversation_id=conversation_id,
            message=payload.message,
        )
    except ConversationNotFoundError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Conversation not found") from exc
    except ConversationOwnershipError as exc:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Conversation access denied") from exc
    except ConversationLimitError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc

    return ConversationSendResponse(
        conversation=_to_detail_response(conversation),
        assistant_message=_to_message_response(assistant_message),
    )


@router.delete("/{conversation_id}", response_model=ConversationDeleteResponse)
def delete_conversation(
    conversation_id: str,
    request: Request,
    token: str | None = Depends(oauth2_optional),
    db: Session = Depends(get_db),
) -> ConversationDeleteResponse:
    """Delete a conversation if the current owner matches."""

    owner = _resolve_owner(request, token, db)
    try:
        get_conversation_service().delete_conversation(
            owner_id=owner.owner_id,
            owner_type=owner.owner_type,
            conversation_id=conversation_id,
        )
    except ConversationNotFoundError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Conversation not found") from exc
    except ConversationOwnershipError as exc:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Conversation access denied") from exc

    return ConversationDeleteResponse(deleted=True, conversation_id=conversation_id)


@router.get("/status", response_model=ConversationStatusResponse)
def conversation_status() -> ConversationStatusResponse:
    """Return memory health for the conversation engine."""

    return ConversationStatusResponse(**get_conversation_service().status())


@router.get("/{conversation_id}", response_model=ConversationResponse)
def get_conversation(
    conversation_id: str,
    request: Request,
    token: str | None = Depends(oauth2_optional),
    db: Session = Depends(get_db),
) -> ConversationResponse:
    """Return conversation metadata and messages."""

    owner = _resolve_owner(request, token, db)
    try:
        record = get_conversation_service().get_conversation(
            owner_id=owner.owner_id,
            owner_type=owner.owner_type,
            conversation_id=conversation_id,
        )
    except ConversationNotFoundError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Conversation not found") from exc
    except ConversationOwnershipError as exc:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Conversation access denied") from exc

    return _to_detail_response(record)


def _resolve_owner(request: Request | None, token: str | None, db: Session) -> OwnerContext:
    """Resolve the current owner from JWT or fall back to guest memory."""

    if token is None and request is not None:
        authorization = request.headers.get("Authorization", "")
        scheme, _, header_token = authorization.partition(" ")
        if scheme.lower() == "bearer" and header_token:
            token = header_token

    if not token:
        return OwnerContext(owner_id="guest", owner_type="guest")

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

    return OwnerContext(owner_id=user.student_id, owner_type=user.role)


def _to_summary_response(record: ConversationRecord) -> ConversationSummaryResponse:
    """Convert a conversation record to a summary payload."""

    return ConversationSummaryResponse(
        conversation_id=record.conversation_id,
        owner_id=record.owner_id,
        owner_type=record.owner_type,
        title=record.title,
        conversation_type=record.conversation_type.value,
        status=record.status.value,
        created_at=record.created_at.isoformat(),
        last_activity=record.last_activity.isoformat(),
        message_count=record.message_count,
    )


def _to_message_response(message) -> ConversationMessageResponse:
    """Convert an in-memory message record to a payload."""

    return ConversationMessageResponse(
        message_id=message.message_id,
        conversation_id=message.conversation_id,
        role=message.role,
        content=message.content,
        timestamp=message.timestamp.isoformat(),
    )


def _to_detail_response(record: ConversationRecord) -> ConversationResponse:
    """Convert a conversation record to a detailed payload."""

    return ConversationResponse(
        conversation_id=record.conversation_id,
        owner_id=record.owner_id,
        owner_type=record.owner_type,
        title=record.title,
        conversation_type=record.conversation_type.value,
        status=record.status.value,
        created_at=record.created_at.isoformat(),
        last_activity=record.last_activity.isoformat(),
        message_count=record.message_count,
        messages=[_to_message_response(message) for message in record.messages],
    )
