"""Reusable LLM service orchestration layer."""

from __future__ import annotations

import logging
import time
from dataclasses import dataclass

from app.core.config import Settings, get_settings
from app.schemas.llm import ChatResponse
from app.services.llm.cache import CachedChatResponse, LLMResponseCache, get_response_cache
from app.services.llm.exceptions import LLMConfigurationError
from app.services.llm.prompt_loader import PromptLoader
from app.services.llm.providers.base_provider import BaseProvider
from app.services.llm.providers.mock_provider import MockProvider
from app.services.llm.providers.provider_factory import ProviderFactory

logger = logging.getLogger(__name__)


@dataclass(slots=True)
class LLMGenerationResult:
    """Normalized LLM response plus execution metadata."""

    response: ChatResponse
    cached: bool
    latency_ms: int
    usage_prompt_tokens: int | None = None
    usage_completion_tokens: int | None = None
    usage_total_tokens: int | None = None


@dataclass(slots=True)
class LLMService:
    """Single orchestration point for all future LLM features."""

    provider: BaseProvider
    prompt_loader: PromptLoader
    cache: LLMResponseCache

    @classmethod
    def from_settings(cls, settings: Settings | None = None) -> "LLMService":
        """Build the service from application settings."""

        settings = settings or get_settings()
        provider = ProviderFactory.create(settings)
        prompt_loader = PromptLoader()
        cache = get_response_cache(enabled=settings.ENABLE_CACHE, max_size=settings.CACHE_SIZE)
        return cls(provider=provider, prompt_loader=prompt_loader, cache=cache)

    def generate(self, message: str, prompt_name: str = "general_chat") -> ChatResponse:
        """Generate a response using the configured provider and prompt."""

        return self.generate_with_metadata(message=message, prompt_name=prompt_name).response

    def generate_with_metadata(
        self,
        message: str,
        prompt_name: str = "general_chat",
        system_prompt: str | None = None,
    ) -> LLMGenerationResult:
        """Generate a response and return execution metadata."""

        prompt_label = prompt_name if system_prompt is None else "custom"
        prompt_text = system_prompt or self.prompt_loader.load(prompt_name)
        cache_key = (self.provider.model, prompt_text, message)
        cached = self.cache.get(cache_key)
        if cached is not None:
            logger.info("LLM cache hit model=%s prompt=%s", self.provider.model, prompt_label)
            print(f"[LLM] cache hit model={self.provider.model} prompt={prompt_label}")
            return LLMGenerationResult(response=cached.to_schema(), cached=True, latency_ms=0)

        start = time.perf_counter()
        logger.info("LLM request started provider=%s model=%s", self.provider.provider_name, self.provider.model)
        print(f"[LLM] request started provider={self.provider.provider_name} model={self.provider.model}")

        result = self.provider.generate(prompt_text, message)

        if result.usage is not None:
            logger.info(
                "LLM usage provider=%s prompt_tokens=%s completion_tokens=%s total_tokens=%s",
                result.provider,
                result.usage.prompt_tokens,
                result.usage.completion_tokens,
                result.usage.total_tokens,
            )

        response = ChatResponse(response=result.response, model=result.model, provider=result.provider)
        self.cache.set(
            cache_key,
            CachedChatResponse(response=response.response, model=response.model, provider=response.provider),
        )

        latency_ms = int((time.perf_counter() - start) * 1000)
        logger.info("LLM request completed provider=%s latency=%.3f", response.provider, latency_ms / 1000)
        print(f"[LLM] request completed provider={response.provider} latency={latency_ms / 1000:.3f}s")
        return LLMGenerationResult(
            response=response,
            cached=False,
            latency_ms=latency_ms,
            usage_prompt_tokens=result.usage.prompt_tokens if result.usage else None,
            usage_completion_tokens=result.usage.completion_tokens if result.usage else None,
            usage_total_tokens=result.usage.total_tokens if result.usage else None,
        )

    def health_check(self) -> dict[str, object]:
        """Return a non-sensitive snapshot of the current LLM setup."""

        status = self.provider.health_check()
        status.update(
            {
                "mock_mode": isinstance(self.provider, MockProvider),
                "cache_enabled": self.cache.enabled,
            }
        )
        return status


def get_llm_service() -> LLMService:
    """Dependency provider for FastAPI."""

    try:
        return LLMService.from_settings()
    except LLMConfigurationError:
        raise
