"""Schemas for the in-memory conversation engine."""

from __future__ import annotations

from pydantic import BaseModel, Field


class AssistantContext(BaseModel):
    """Reusable assistant context supplied by the frontend."""

    page: str | None = None
    widget: str | None = None
    source: str | None = None


class ConversationCreateRequest(BaseModel):
    """Request payload for creating a new conversation."""

    assistant_context: AssistantContext | None = None


class ConversationMessageRequest(BaseModel):
    """Request payload for sending a conversation message."""

    message: str = Field(min_length=1)
    assistant_context: AssistantContext | None = None


class ConversationMessageResponse(BaseModel):
    """Stored conversation message."""

    message_id: str
    conversation_id: str
    role: str
    content: str
    timestamp: str


class ConversationResponse(BaseModel):
    """Conversation metadata with its stored messages."""

    conversation_id: str
    owner_id: str
    owner_type: str
    title: str
    conversation_type: str
    status: str
    created_at: str
    last_activity: str
    message_count: int
    messages: list[ConversationMessageResponse]


class ConversationSummaryResponse(BaseModel):
    """Conversation metadata without messages."""

    conversation_id: str
    owner_id: str
    owner_type: str
    title: str
    conversation_type: str
    status: str
    created_at: str
    last_activity: str
    message_count: int


class ConversationListResponse(BaseModel):
    """List of conversations for the current owner."""

    conversations: list[ConversationSummaryResponse]


class ConversationCreateResponse(BaseModel):
    """Response returned when a conversation is created."""

    conversation_id: str
    title: str
    type: str
    status: str


class ConversationSendResponse(BaseModel):
    """Response returned when a placeholder assistant reply is appended."""

    conversation: ConversationResponse
    assistant_message: ConversationMessageResponse


class ConversationDeleteResponse(BaseModel):
    """Response returned after deleting a conversation."""

    deleted: bool
    conversation_id: str


class ConversationStatusResponse(BaseModel):
    """Conversation memory status payload."""

    memory_enabled: bool
    ttl_hours: int
    conversation_count: int
    memory_usage_estimate: int
