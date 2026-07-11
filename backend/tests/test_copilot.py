"""Tests for the Phase 5 grounded copilot pipeline."""

from __future__ import annotations

from dataclasses import dataclass

import pytest
from httpx import ASGITransport, AsyncClient

from app.main import app
from app.schemas.llm import ChatResponse
from app.services.copilot.answer_validator import AnswerValidator
from app.services.copilot.context_builder import ContextBuilder
from app.services.copilot.prompt_builder import PromptBuilder
from app.services.copilot.query_preprocessor import QueryPreprocessor
from app.services.copilot.service import CopilotChatService, get_copilot_chat_service
from app.services.llm.llm_service import LLMGenerationResult


@dataclass(slots=True)
class DummyRetrievalService:
    """Return a fixed set of retrieval results for testing."""

    results: list[dict[str, object]]

    def search(self, query: str, k: int) -> list[dict[str, object]]:
        return self.results[:k]


@dataclass(slots=True)
class DummyLLMService:
    """Return a fixed generated answer for testing."""

    response: LLMGenerationResult

    def generate_with_metadata(self, message: str, prompt_name: str = "general_chat", system_prompt: str | None = None) -> LLMGenerationResult:
        return self.response


def test_query_preprocessor_normalizes_whitespace() -> None:
    """The preprocessor should trim and normalize spacing."""

    processor = QueryPreprocessor()

    assert processor.preprocess("  What   is   attendance?  ") == "what is attendance?"


def test_context_builder_formats_sources() -> None:
    """Retrieved chunks should be formatted into structured context blocks."""

    builder = ContextBuilder()
    context, sources = builder.build(
        [
            {
                "text": "Students must attend at least 75% of classes.",
                "metadata": {
                    "source_file": "handbook.md",
                    "chapter": "CHAPTER 1",
                    "section": "Attendance",
                    "subsection": "Policy",
                    "heading_path": "CHAPTER 1 > Attendance > Policy",
                    "page_start": 2,
                    "page_end": 3,
                },
            }
        ]
    )

    assert "Document: handbook.md" in context
    assert "Chapter: CHAPTER 1" in context
    assert "Heading Path: CHAPTER 1 > Attendance > Policy" in context
    assert "Pages: 2-3" in context
    assert sources == [
        {
            "document": "handbook.md",
            "chapter": "CHAPTER 1",
            "section": "Attendance",
            "heading_path": "CHAPTER 1 > Attendance > Policy",
            "pages": "2-3",
        }
    ]


def test_prompt_builder_uses_rag_prompt() -> None:
    """The prompt builder should load the reusable RAG prompt file."""

    builder = PromptBuilder()
    prompt = builder.build(question="What is attendance?", context="Document: handbook.md")

    assert "Answer only from supplied context" in prompt
    assert "Supplied context:" in prompt
    assert "Document: handbook.md" in prompt


def test_answer_validator_strips_generic_prefix() -> None:
    """Generic AI phrases should be cleaned from the start of the answer."""

    validator = AnswerValidator()

    assert validator.validate("As an AI language model, attendance is 75%.") == "attendance is 75%."


def test_copilot_chat_service_returns_structured_response() -> None:
    """The copilot pipeline should return answer text, sources, and metadata."""

    retrieval_service = DummyRetrievalService(
        results=[
            {
                "text": "Students must attend at least 75% of classes.",
                "metadata": {
                    "source_file": "handbook.md",
                    "chapter": "CHAPTER 1",
                    "section": "Attendance",
                    "subsection": "Policy",
                    "heading_path": "CHAPTER 1 > Attendance > Policy",
                    "page_start": 2,
                    "page_end": 2,
                },
            }
        ]
    )
    llm_service = DummyLLMService(
        response=LLMGenerationResult(
            response=ChatResponse(response="Students must attend 75% of classes.", model="mock-model", provider="mock"),
            cached=False,
            latency_ms=15,
        )
    )
    service = CopilotChatService(
        retrieval_service=retrieval_service,
        llm_service=llm_service,  # type: ignore[arg-type]
        preprocessor=QueryPreprocessor(),
        context_builder=ContextBuilder(),
        prompt_builder=PromptBuilder(),
        validator=AnswerValidator(),
        top_k=3,
    )

    response = service.chat("What is the attendance requirement?")

    assert response.answer == "Students must attend 75% of classes."
    assert response.sources[0].document == "handbook.md"
    assert response.sources[0].heading_path == "CHAPTER 1 > Attendance > Policy"
    assert response.metadata.cached is False
    assert response.metadata.retrieved_chunks == 1


@pytest.mark.anyio
async def test_copilot_chat_endpoint_returns_structured_response() -> None:
    """The API endpoint should expose the grounded response model."""

    service = CopilotChatService(
        retrieval_service=DummyRetrievalService(
            results=[
                {
                    "text": "Students must attend at least 75% of classes.",
                    "metadata": {
                        "source_file": "handbook.md",
                        "chapter": "CHAPTER 1",
                        "section": "Attendance",
                        "subsection": "Policy",
                        "page_start": 2,
                        "page_end": 2,
                    },
                }
            ]
        ),
        llm_service=DummyLLMService(
            response=LLMGenerationResult(
                response=ChatResponse(response="Students must attend 75% of classes.", model="mock-model", provider="mock"),
                cached=True,
                latency_ms=0,
            )
        ),  # type: ignore[arg-type]
        preprocessor=QueryPreprocessor(),
        context_builder=ContextBuilder(),
        prompt_builder=PromptBuilder(),
        validator=AnswerValidator(),
        top_k=3,
    )
    app.dependency_overrides[get_copilot_chat_service] = lambda: service

    try:
        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://test") as client:
            response = await client.post(
                "/api/v1/copilot/chat",
                json={"conversation_id": "demo-thread", "message": "What is the attendance requirement?"},
            )
    finally:
        app.dependency_overrides.clear()

    assert response.status_code == 200
    payload = response.json()
    assert payload["answer"] == "Students must attend 75% of classes."
    assert payload["metadata"]["cached"] is True
    assert payload["metadata"]["retrieved_chunks"] == 1
