"""In-memory conversation manager."""

from __future__ import annotations

from copy import deepcopy
from datetime import datetime, timedelta, timezone
from threading import RLock
from typing import Any
from uuid import uuid4

from app.core.config import get_settings
from app.services.conversation.classifier import classify_conversation_type
from app.services.conversation.models import (
    ConversationMessageRecord,
    ConversationRecord,
    ConversationStatus,
    ConversationType,
)
from app.services.conversation.title_generator import generate_title

DEFAULT_ASSISTANT_REPLY = "Assistant infrastructure ready. No LLM call was made."
DEFAULT_TITLE = "New Conversation"


class ConversationError(Exception):
    """Base conversation service error."""


class ConversationNotFoundError(ConversationError):
    """Raised when a conversation does not exist."""


class ConversationOwnershipError(ConversationError):
    """Raised when an owner accesses another owner's conversation."""


class ConversationLimitError(ConversationError):
    """Raised when a memory limit is exceeded."""


class ConversationService:
    """Store conversations in memory with TTL and ownership checks."""

    def __init__(
        self,
        *,
        memory_enabled: bool,
        ttl_hours: int,
        max_conversations_per_user: int,
        max_messages_per_conversation: int,
        max_title_length: int,
    ) -> None:
        self.memory_enabled = memory_enabled
        self.ttl_hours = ttl_hours
        self.max_conversations_per_user = max_conversations_per_user
        self.max_messages_per_conversation = max_messages_per_conversation
        self.max_title_length = max_title_length
        self._lock = RLock()
        self._conversations: dict[str, ConversationRecord] = {}

    def reset(self) -> None:
        """Clear all in-memory conversations."""

        with self._lock:
            self._conversations.clear()

    def create_conversation(
        self,
        *,
        owner_id: str,
        owner_type: str,
        initial_message: str | None = None,
    ) -> ConversationRecord:
        """Create a new conversation for the given owner."""

        with self._lock:
            self._ensure_memory_enabled()
            self._enforce_conversation_limit(owner_id, owner_type)
            now = datetime.now(timezone.utc)
            conversation_type = (
                classify_conversation_type(initial_message)
                if initial_message
                else ConversationType.GENERAL
            )
            title = (
                generate_title(initial_message, self.max_title_length)
                if initial_message
                else DEFAULT_TITLE
            )
            record = ConversationRecord(
                conversation_id=str(uuid4()),
                owner_id=owner_id,
                owner_type=owner_type,
                title=title,
                conversation_type=conversation_type,
                status=ConversationStatus.ACTIVE,
                created_at=now,
                last_activity=now,
            )
            self._conversations[record.conversation_id] = record
            return deepcopy(record)

    def list_conversations(self, *, owner_id: str, owner_type: str) -> list[ConversationRecord]:
        """List all active conversations for the given owner."""

        with self._lock:
            self._remove_expired_locked()
            conversations = [
                deepcopy(record)
                for record in self._conversations.values()
                if record.owner_id == owner_id and record.owner_type == owner_type
            ]
            conversations.sort(key=lambda record: record.last_activity, reverse=True)
            return conversations

    def get_conversation(
        self,
        *,
        owner_id: str,
        owner_type: str,
        conversation_id: str,
    ) -> ConversationRecord:
        """Return a single conversation after validating ownership."""

        with self._lock:
            self._remove_expired_locked()
            record = self._conversations.get(conversation_id)
            if record is None:
                raise ConversationNotFoundError(conversation_id)
            self._assert_ownership(record, owner_id, owner_type)
            return deepcopy(record)

    def send_message(
        self,
        *,
        owner_id: str,
        owner_type: str,
        conversation_id: str,
        message: str,
        assistant_content: str | None = None,
    ) -> tuple[ConversationRecord, ConversationMessageRecord]:
        """Append a user message and an assistant reply."""

        with self._lock:
            self._remove_expired_locked()
            record = self._conversations.get(conversation_id)
            if record is None:
                raise ConversationNotFoundError(conversation_id)
            self._assert_ownership(record, owner_id, owner_type)
            self._ensure_message_capacity(record)

            now = datetime.now(timezone.utc)
            if record.title == DEFAULT_TITLE:
                record.title = generate_title(message, self.max_title_length)
            if record.conversation_type == ConversationType.GENERAL:
                record.conversation_type = classify_conversation_type(message)

            user_message = ConversationMessageRecord(
                message_id=str(uuid4()),
                conversation_id=conversation_id,
                role="user",
                content=message,
                timestamp=now,
            )
            assistant_message = ConversationMessageRecord(
                message_id=str(uuid4()),
                conversation_id=conversation_id,
                role="assistant",
                content=assistant_content or DEFAULT_ASSISTANT_REPLY,
                timestamp=now,
            )
            record.messages.extend([user_message, assistant_message])
            record.message_count = len(record.messages)
            record.last_activity = now
            record.status = ConversationStatus.ACTIVE
            return deepcopy(record), deepcopy(assistant_message)

    def delete_conversation(
        self,
        *,
        owner_id: str,
        owner_type: str,
        conversation_id: str,
    ) -> None:
        """Delete a conversation if the owner matches."""

        with self._lock:
            record = self._conversations.get(conversation_id)
            if record is None:
                raise ConversationNotFoundError(conversation_id)
            self._assert_ownership(record, owner_id, owner_type)
            del self._conversations[conversation_id]

    def status(self) -> dict[str, Any]:
        """Return memory health and usage information."""

        with self._lock:
            self._remove_expired_locked()
            memory_usage_estimate = sum(
                len(record.title)
                + sum(len(message.content) for message in record.messages)
                + 256
                for record in self._conversations.values()
            )
            return {
                "memory_enabled": self.memory_enabled,
                "ttl_hours": self.ttl_hours,
                "conversation_count": len(self._conversations),
                "memory_usage_estimate": memory_usage_estimate,
            }

    def cleanup_expired_conversations(self) -> int:
        """Remove expired conversations and return the number deleted."""

        with self._lock:
            return self._remove_expired_locked()

    def _remove_expired_locked(self) -> int:
        """Remove expired conversations while the lock is held."""

        now = datetime.now(timezone.utc)
        expired_ids = [
            conversation_id
            for conversation_id, record in self._conversations.items()
            if now - record.last_activity > timedelta(hours=self.ttl_hours)
        ]
        for conversation_id in expired_ids:
            del self._conversations[conversation_id]
        return len(expired_ids)

    def _assert_ownership(self, record: ConversationRecord, owner_id: str, owner_type: str) -> None:
        """Ensure the caller owns the conversation."""

        if record.owner_id != owner_id or record.owner_type != owner_type:
            raise ConversationOwnershipError(record.conversation_id)

    def _enforce_conversation_limit(self, owner_id: str, owner_type: str) -> None:
        """Prevent a user from exceeding the configured conversation limit."""

        count = sum(
            1
            for record in self._conversations.values()
            if record.owner_id == owner_id and record.owner_type == owner_type
        )
        if count >= self.max_conversations_per_user:
            raise ConversationLimitError("conversation limit reached")

    def _ensure_message_capacity(self, record: ConversationRecord) -> None:
        """Prevent a conversation from exceeding the configured message limit."""

        if record.message_count + 2 > self.max_messages_per_conversation:
            raise ConversationLimitError("message limit reached")

    def _ensure_memory_enabled(self) -> None:
        """Reject operations if memory is disabled."""

        if not self.memory_enabled:
            raise ConversationError("conversation memory is disabled")


def _build_service() -> ConversationService:
    settings = get_settings()
    return ConversationService(
        memory_enabled=settings.CHAT_MEMORY_ENABLED,
        ttl_hours=settings.CHAT_TTL_HOURS,
        max_conversations_per_user=settings.CHAT_MAX_CONVERSATIONS_PER_USER,
        max_messages_per_conversation=settings.CHAT_MAX_MESSAGES_PER_CONVERSATION,
        max_title_length=settings.CHAT_MAX_TITLE_LENGTH,
    )


_conversation_service = _build_service()


def get_conversation_service() -> ConversationService:
    """Return the singleton conversation service."""

    return _conversation_service
