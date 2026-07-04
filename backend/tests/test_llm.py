"""Tests for the refactored reusable LLM service layer."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

import pytest
from httpx import ASGITransport, AsyncClient

from app.core.config import Settings
from app.main import app
from app.schemas.llm import ChatResponse
from app.services.llm.cache import CachedChatResponse, LLMResponseCache
from app.services.llm.exceptions import LLMConfigurationError
from app.services.llm.llm_service import LLMService
from app.services.llm.prompt_loader import PromptLoader
from app.services.llm.providers.base_provider import BaseProvider, ProviderResult
from app.services.llm.providers.mock_provider import MockProvider
from app.services.llm.providers.provider_factory import ProviderFactory
from app.services.llm.service import get_llm_service


@dataclass(slots=True)
class RecordingProvider(BaseProvider):
    """Test provider that records how many times it is called."""

    model: str = "test-model"
    provider_name: str = "custom"
    calls: int = 0

    def generate(self, system_prompt: str, user_message: str) -> ProviderResult:
        self.calls += 1
        return ProviderResult(
            response=f"{system_prompt} :: {user_message}",
            model=self.model,
            provider=self.provider_name,
        )


def test_mock_provider_response() -> None:
    """Mock mode should return a deterministic response."""

    provider = MockProvider()
    result = provider.generate(
        "You are IM Copilot.\nSupplied context:\nDocument: handbook.md\nChapter: CHAPTER 1\nSection: Attendance\nSubsection: Policy\nPages: 2-3\nContent:\nStudents must attend at least 75% of classes.",
        "What is attendance?",
    )

    assert "[MOCK MODE]" in result.response
    assert "Prompt successfully built." in result.response
    assert "Retrieved context received." in result.response
    assert "Document Count: 1" in result.response
    assert "Retrieved Chunks: 1" in result.response
    assert result.provider == "mock"
    assert result.model == "mock-model"


def test_mock_provider_sql_debug_response() -> None:
    """Mock mode should summarize structured academic data."""

    provider = MockProvider()
    result = provider.generate(
        "You are IM Copilot.\nStructured data:\n{\n  \"student_id\": \"DS001\",\n  \"cgpa\": 3.72,\n  \"program\": \"BS Data Science\"\n}",
        "What is my CGPA?",
    )

    assert "[MOCK MODE]" in result.response
    assert "Academic data retrieved successfully." in result.response
    assert "Structured data received:" in result.response
    assert "\"student_id\": \"DS001\"" in result.response
    assert "No external LLM call was made." in result.response


def test_provider_factory_mock_mode() -> None:
    """The provider factory should select the mock provider when configured."""

    settings = Settings(MOCK_LLM=True, LLM_PROVIDER="mock")

    provider = ProviderFactory.create(settings)

    assert isinstance(provider, MockProvider)


def test_provider_factory_invalid_provider() -> None:
    """The factory should reject unsupported providers."""

    settings = Settings(MOCK_LLM=False, LLM_PROVIDER="invalid-provider", LLM_MODEL="demo", LLM_API_KEY="key")

    with pytest.raises(LLMConfigurationError):
        ProviderFactory.create(settings)


def test_prompt_loader_reads_prompt_file(tmp_path: Path) -> None:
    """Prompt files should load from disk without code changes."""

    prompts_dir = tmp_path / "prompts"
    prompts_dir.mkdir()
    (prompts_dir / "general_chat.txt").write_text("Prompt text from disk", encoding="utf-8")

    loader = PromptLoader(prompts_dir=prompts_dir)

    assert loader.load("general_chat") == "Prompt text from disk"


def test_llm_cache_hit_and_miss(tmp_path: Path) -> None:
    """Repeated identical requests should be served from cache."""

    prompts_dir = tmp_path / "prompts"
    prompts_dir.mkdir()
    (prompts_dir / "general_chat.txt").write_text("System prompt", encoding="utf-8")

    provider = RecordingProvider()
    service = LLMService(
        provider=provider,
        prompt_loader=PromptLoader(prompts_dir=prompts_dir),
        cache=LLMResponseCache(enabled=True, max_size=10),
    )

    first = service.generate("Hello")
    second = service.generate("Hello")

    assert provider.calls == 1
    assert first == second
    assert first.response == "System prompt :: Hello"


def test_llm_health_check_returns_configuration_snapshot() -> None:
    """Health check should expose safe, non-secret LLM details."""

    service = LLMService(
        provider=MockProvider(model="mock-model"),
        prompt_loader=PromptLoader(),
        cache=LLMResponseCache(enabled=False, max_size=10),
    )

    snapshot = service.health_check()

    assert snapshot["provider"] == "mock"
    assert snapshot["model"] == "mock-model"
    assert snapshot["mock_mode"] is True
    assert snapshot["cache_enabled"] is False


@pytest.mark.anyio
async def test_llm_endpoint_validation() -> None:
    """The endpoint should enforce the request schema."""

    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        response = await client.post("/api/v1/llm/test", json={})

    assert response.status_code == 422


@pytest.mark.anyio
async def test_llm_endpoint_mock_response() -> None:
    """The endpoint should return the mock response when mock mode is used."""

    service = LLMService(
        provider=MockProvider(),
        prompt_loader=PromptLoader(),
        cache=LLMResponseCache(enabled=False, max_size=10),
    )
    app.dependency_overrides[get_llm_service] = lambda: service

    try:
        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://test") as client:
            response = await client.post("/api/v1/llm/test", json={"message": "Hello"})
    finally:
        app.dependency_overrides.clear()

    assert response.status_code == 200
    assert response.json()["provider"] == "mock"
    assert response.json()["model"] == "mock-model"
    assert "[MOCK MODE]" in response.json()["response"]
