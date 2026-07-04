"""Base interfaces and shared data structures for LLM providers."""

from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Any


@dataclass(slots=True)
class ProviderUsage:
    """Token usage returned by a provider."""

    prompt_tokens: int | None = None
    completion_tokens: int | None = None
    total_tokens: int | None = None


@dataclass(slots=True)
class ProviderResult:
    """Normalized provider response."""

    response: str
    model: str
    provider: str
    usage: ProviderUsage | None = None
    raw: dict[str, Any] | None = None


class BaseProvider(ABC):
    """Contract all LLM providers must follow."""

    provider_name: str
    model: str

    @abstractmethod
    def generate(self, system_prompt: str, user_message: str) -> ProviderResult:
        """Generate a model response from a system prompt and user message."""

    def health_check(self) -> dict[str, Any]:
        """Return non-sensitive provider information."""

        return {
            "provider": self.provider_name,
            "model": self.model,
        }
