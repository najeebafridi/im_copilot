"""Conversation records and enums."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum


class ConversationStatus(str, Enum):
    """Lifecycle state for a conversation."""

    ACTIVE = "ACTIVE"
    LOADING = "LOADING"
    ERROR = "ERROR"
    EXPIRED = "EXPIRED"


class ConversationType(str, Enum):
    """Conversation classification."""

    GENERAL = "GENERAL"
    ACADEMIC = "ACADEMIC"
    POLICY = "POLICY"
    ADMIN = "ADMIN"


@dataclass(slots=True)
class ConversationMessageRecord:
    """In-memory message record."""

    message_id: str
    conversation_id: str
    role: str
    content: str
    timestamp: datetime


@dataclass(slots=True)
class ConversationRecord:
    """In-memory conversation record."""

    conversation_id: str
    owner_id: str
    owner_type: str
    title: str
    conversation_type: ConversationType
    status: ConversationStatus
    created_at: datetime
    last_activity: datetime
    message_count: int = 0
    messages: list[ConversationMessageRecord] = field(default_factory=list)
