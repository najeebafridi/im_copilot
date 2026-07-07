"""Tests for the in-memory conversation infrastructure."""

from __future__ import annotations

from datetime import datetime, timedelta, timezone
from uuid import UUID

import pytest
from httpx import ASGITransport, AsyncClient

from app.main import app
from app.services.conversation.classifier import classify_conversation_type
from app.services.conversation.models import ConversationType
from app.services.conversation.scheduler import ConversationCleanupScheduler
from app.services.conversation.service import (
    ConversationLimitError,
    ConversationNotFoundError,
    ConversationService,
)


def _build_service(
    *,
    ttl_hours: int = 24,
    max_conversations_per_user: int = 30,
    max_messages_per_conversation: int = 200,
) -> ConversationService:
    return ConversationService(
        memory_enabled=True,
        ttl_hours=ttl_hours,
        max_conversations_per_user=max_conversations_per_user,
        max_messages_per_conversation=max_messages_per_conversation,
        max_title_length=40,
    )


async def _login(client: AsyncClient, student_id: str, password: str) -> str:
    response = await client.post(
        "/api/v1/auth/login",
        json={"student_id": student_id, "password": password},
    )
    assert response.status_code == 200
    return response.json()["access_token"]


def test_conversation_creation_generates_uuid_and_defaults() -> None:
    """A new conversation should get a UUID and default metadata."""

    service = _build_service()
    conversation = service.create_conversation(owner_id="DS001", owner_type="student")

    UUID(conversation.conversation_id)
    assert conversation.owner_id == "DS001"
    assert conversation.owner_type == "student"
    assert conversation.title == "New Conversation"
    assert conversation.conversation_type == ConversationType.GENERAL
    assert conversation.message_count == 0


def test_title_generation_uses_first_user_message() -> None:
    """The first user message should become the conversation title."""

    service = _build_service()
    conversation = service.create_conversation(owner_id="DS001", owner_type="student")
    updated, assistant_message = service.send_message(
        owner_id="DS001",
        owner_type="student",
        conversation_id=conversation.conversation_id,
        message="Tell me my attendance policy for semester five",
    )

    assert updated.title == "Attendance Policy Semester Five"
    assert assistant_message.role == "assistant"
    assert updated.message_count == 2


def test_conversation_type_classification_uses_keywords() -> None:
    """Keyword matching should map to the expected conversation type."""

    assert classify_conversation_type("What is my CGPA?") == ConversationType.ACADEMIC
    assert classify_conversation_type("Show me the handbook policy") == ConversationType.POLICY
    assert classify_conversation_type("Admin reports and approvals") == ConversationType.ADMIN
    assert classify_conversation_type("Hello there") == ConversationType.GENERAL


def test_conversation_deletion_removes_record() -> None:
    """Deleting a conversation should make it unavailable afterwards."""

    service = _build_service()
    conversation = service.create_conversation(owner_id="DS001", owner_type="student")

    service.delete_conversation(
        owner_id="DS001",
        owner_type="student",
        conversation_id=conversation.conversation_id,
    )

    with pytest.raises(ConversationNotFoundError):
        service.get_conversation(
            owner_id="DS001",
            owner_type="student",
            conversation_id=conversation.conversation_id,
        )


def test_ttl_expiration_is_removed_by_cleanup() -> None:
    """Expired conversations should be removed by cleanup."""

    service = _build_service(ttl_hours=1)
    conversation = service.create_conversation(owner_id="DS001", owner_type="student")
    service._conversations[conversation.conversation_id].last_activity = datetime.now(timezone.utc) - timedelta(hours=2)

    removed = service.cleanup_expired_conversations()

    assert removed == 1
    assert service.status()["conversation_count"] == 0


def test_conversation_limit_is_enforced_per_owner() -> None:
    """A user should not exceed the configured conversation limit."""

    service = _build_service(max_conversations_per_user=1)
    service.create_conversation(owner_id="DS001", owner_type="student")

    with pytest.raises(ConversationLimitError):
        service.create_conversation(owner_id="DS001", owner_type="student")


def test_message_limit_is_enforced_per_conversation() -> None:
    """A conversation should not exceed the configured message limit."""

    service = _build_service(max_messages_per_conversation=2)
    conversation = service.create_conversation(owner_id="DS001", owner_type="student")
    service.send_message(
        owner_id="DS001",
        owner_type="student",
        conversation_id=conversation.conversation_id,
        message="What is my CGPA?",
    )

    with pytest.raises(ConversationLimitError):
        service.send_message(
            owner_id="DS001",
            owner_type="student",
            conversation_id=conversation.conversation_id,
            message="Show me my timetable",
        )


def test_cleanup_scheduler_runs_once() -> None:
    """The cleanup scheduler should invoke the cleanup cycle."""

    service = _build_service(ttl_hours=1)
    conversation = service.create_conversation(owner_id="DS001", owner_type="student")
    service._conversations[conversation.conversation_id].last_activity = datetime.now(timezone.utc) - timedelta(hours=2)
    scheduler = ConversationCleanupScheduler(service=service, interval_minutes=30)

    assert scheduler.run_once() == 1
    assert service.status()["conversation_count"] == 0


@pytest.mark.anyio
async def test_status_endpoint_reports_memory_state() -> None:
    """The status endpoint should report the in-memory chat state."""

    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        response = await client.get("/api/v1/chat/status")

    assert response.status_code == 200
    payload = response.json()
    assert payload["memory_enabled"] is True
    assert payload["ttl_hours"] == 24
    assert "conversation_count" in payload


@pytest.mark.anyio
async def test_guest_conversation_lifecycle() -> None:
    """Guests should be able to manage guest-owned conversations without auth."""

    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        create_response = await client.post("/api/v1/chat/new")
        assert create_response.status_code == 200
        conversation_id = create_response.json()["conversation_id"]

        list_response = await client.get("/api/v1/chat/list")
        assert list_response.status_code == 200
        assert list_response.json()["conversations"]

        detail_response = await client.get(f"/api/v1/chat/{conversation_id}")
        assert detail_response.status_code == 200

        delete_response = await client.delete(f"/api/v1/chat/{conversation_id}")
        assert delete_response.status_code == 200


@pytest.mark.anyio
async def test_conversation_ownership_is_enforced() -> None:
    """A student should not be able to access another user's conversation."""

    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        student_token = await _login(client, "DS001", "password123")
        admin_token = await _login(client, "admin", "admin123")

        create_response = await client.post(
            "/api/v1/chat/new",
            headers={"Authorization": f"Bearer {student_token}"},
        )
        conversation_id = create_response.json()["conversation_id"]

        forbidden_response = await client.get(
            f"/api/v1/chat/{conversation_id}",
            headers={"Authorization": f"Bearer {admin_token}"},
        )

    assert forbidden_response.status_code == 403


@pytest.mark.anyio
async def test_authenticated_conversation_uses_existing_user() -> None:
    """Authenticated users should own their own conversation space."""

    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        token = await _login(client, "DS001", "password123")
        create_response = await client.post(
            "/api/v1/chat/new",
            headers={"Authorization": f"Bearer {token}"},
        )
        conversation_id = create_response.json()["conversation_id"]

        detail_response = await client.get(
            f"/api/v1/chat/{conversation_id}",
            headers={"Authorization": f"Bearer {token}"},
        )

    assert detail_response.status_code == 200
    assert detail_response.json()["owner_id"] == "DS001"
