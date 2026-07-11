"""Factory for selecting an LLM provider from settings."""

from __future__ import annotations

from app.core.config import Settings
from app.services.llm.exceptions import LLMConfigurationError
from app.services.llm.providers.base_provider import BaseProvider
from app.services.llm.providers.mock_provider import MockProvider
from app.services.llm.providers.openai_provider import OpenAICompatibleProvider


class ProviderFactory:
    """Create provider instances without leaking provider-specific code."""

    DEFAULT_BASE_URLS = {
        "openai": "https://api.openai.com/v1",
        "openrouter": "https://openrouter.ai/api/v1",
        "grok": "https://api.x.ai/v1",
        "groq": "https://api.groq.com/openai/v1",
    }

    @classmethod
    def create(cls, settings: Settings) -> BaseProvider:
        """Create the appropriate provider based on environment settings."""

        provider_name = (settings.LLM_PROVIDER or "").strip().lower()

        if settings.MOCK_LLM or provider_name == "mock":
            return MockProvider(model=settings.LLM_MODEL or "mock-model")

        if not provider_name:
            provider_name = cls._infer_provider(settings.LLM_BASE_URL)

        if provider_name not in {"openai", "openrouter", "grok", "groq"}:
            raise LLMConfigurationError(f"Invalid LLM provider: {provider_name}")

        base_url = settings.LLM_BASE_URL.strip() or cls.DEFAULT_BASE_URLS[provider_name]
        api_key = settings.LLM_API_KEY.strip()
        model = settings.LLM_MODEL.strip()

        missing = []
        if not api_key:
            missing.append("LLM_API_KEY")
        if not model:
            missing.append("LLM_MODEL")
        if missing:
            raise LLMConfigurationError(f"Missing LLM configuration: {', '.join(missing)}")

        return OpenAICompatibleProvider(
            api_key=api_key,
            base_url=base_url,
            model=model,
            provider_name=provider_name,
            temperature=settings.LLM_TEMPERATURE,
            max_tokens=settings.LLM_MAX_TOKENS,
        )

    @staticmethod
    def _infer_provider(base_url: str) -> str:
        """Infer a provider from the configured base URL."""

        normalized = base_url.lower()
        if "openrouter" in normalized:
            return "openrouter"
        if "x.ai" in normalized or "xai" in normalized or "grok" in normalized:
            return "grok"
        if "groq" in normalized:
            return "groq"
        if "openai" in normalized:
            return "openai"
        return "openai"
