"""LLM-specific exceptions."""

from __future__ import annotations


class LLMError(Exception):
    """Base class for LLM failures."""


class LLMConfigurationError(LLMError):
    """Raised when required LLM configuration is missing."""


class LLMProviderError(LLMError):
    """Raised when the provider returns an error or is unreachable."""

    def __init__(self, message: str, status_code: int = 503) -> None:
        super().__init__(message)
        self.status_code = status_code


class LLMResponseValidationError(LLMError):
    """Raised when a provider response cannot be accepted."""
