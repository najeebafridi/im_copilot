"""Tests for the secure academic data retrieval flow."""

from __future__ import annotations

from dataclasses import dataclass

import pytest
from httpx import ASGITransport, AsyncClient

from app.core.database import SessionLocal
from app.main import app
from app.models.user import User
from app.schemas.llm import ChatResponse
from app.services.academic.prompt_builder import AcademicPromptBuilder
from app.services.copilot.answer_validator import AnswerValidator
from app.services.academic.intent_matcher import AcademicIntent, AcademicIntentMatcher
from app.services.academic.service import AcademicQueryService, get_academic_query_service
from app.services.copilot.query_preprocessor import QueryPreprocessor
from app.services.llm.llm_service import LLMGenerationResult


@dataclass(slots=True)
class DummyLLMService:
    """Return a fixed generated answer for testing."""

    response: LLMGenerationResult

    def generate_with_metadata(self, message: str, prompt_name: str = "general_chat", system_prompt: str | None = None) -> LLMGenerationResult:
        return self.response


def test_academic_intent_matcher_detects_supported_intents() -> None:
    """Keyword rules should map questions to the right academic intent."""

    matcher = AcademicIntentMatcher()

    assert matcher.match("What is my CGPA?").intent == AcademicIntent.PROFILE
    assert matcher.match("What is my attendance?").intent == AcademicIntent.ATTENDANCE_SUMMARY
    assert matcher.match("What is my attendance in DS301?").intent == AcademicIntent.ATTENDANCE_COURSE
    assert matcher.match("What are my grades?").intent == AcademicIntent.GRADES
    assert matcher.match("What is my timetable?").intent == AcademicIntent.TIMETABLE


def test_academic_service_returns_profile_response() -> None:
    """The academic service should return only the authenticated student's data."""

    db = SessionLocal()
    try:
        user = db.query(User).filter(User.student_id == "DS001").first()
        assert user is not None
        service = AcademicQueryService(
            db=db,
            llm_service=DummyLLMService(
                response=LLMGenerationResult(
                    response=ChatResponse(
                        response="Your CGPA is 3.72.",
                        model="mock-model",
                        provider="mock",
                    ),
                    cached=False,
                    latency_ms=12,
                )
            ),  # type: ignore[arg-type]
            preprocessor=QueryPreprocessor(),
            intent_matcher=AcademicIntentMatcher(),
            prompt_builder=AcademicPromptBuilder(),
            validator=AnswerValidator(),
        )

        response = service.answer("What is my CGPA?", user)

        assert response.answer == "Your CGPA is 3.72."
        assert response.sources
        assert any(source.table == "students" for source in response.sources)
        assert response.metadata.provider == "mock"
    finally:
        db.close()


@pytest.mark.anyio
async def test_academic_endpoint_requires_authentication() -> None:
    """The endpoint should reject unauthenticated requests."""

    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        response = await client.post("/api/v1/academic/chat", json={"message": "What is my CGPA?"})

    assert response.status_code == 401


@pytest.mark.anyio
async def test_academic_endpoint_returns_structured_response() -> None:
    """The endpoint should return a grounded response for the authenticated student."""

    db = SessionLocal()
    try:
        user = db.query(User).filter(User.student_id == "DS001").first()
        assert user is not None
        service = AcademicQueryService(
            db=db,
            llm_service=DummyLLMService(
                response=LLMGenerationResult(
                    response=ChatResponse(
                        response="Your CGPA is 3.72.",
                        model="mock-model",
                        provider="mock",
                    ),
                    cached=True,
                    latency_ms=0,
                )
            ),  # type: ignore[arg-type]
            preprocessor=QueryPreprocessor(),
            intent_matcher=AcademicIntentMatcher(),
            prompt_builder=AcademicPromptBuilder(),
            validator=AnswerValidator(),
        )

        app.dependency_overrides[get_academic_query_service] = lambda: service
        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://test") as client:
            login_response = await client.post(
                "/api/v1/auth/login",
                json={"student_id": "DS001", "password": "password123"},
            )
            token = login_response.json()["access_token"]
            response = await client.post(
                "/api/v1/academic/chat",
                json={"message": "What is my CGPA?"},
                headers={"Authorization": f"Bearer {token}"},
            )
    finally:
        app.dependency_overrides.clear()
        db.close()

    assert response.status_code == 200
    payload = response.json()
    assert payload["answer"] == "Your CGPA is 3.72."
    assert payload["metadata"]["cached"] is True
    assert payload["sources"][0]["type"] == "database"
