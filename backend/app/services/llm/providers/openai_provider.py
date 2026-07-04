"""OpenAI-compatible provider implementation."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

import httpx

from app.services.llm.exceptions import LLMProviderError
from app.services.llm.providers.base_provider import BaseProvider, ProviderResult, ProviderUsage


@dataclass(slots=True)
class OpenAICompatibleProvider(BaseProvider):
    """Call any OpenAI-compatible HTTP endpoint directly."""

    api_key: str
    base_url: str
    model: str
    provider_name: str
    temperature: float = 0.7
    max_tokens: int = 256
    timeout_seconds: float = 30.0
    client: httpx.Client | None = None

    def generate(self, system_prompt: str, user_message: str) -> ProviderResult:
        """Send a completion request to the configured endpoint."""

        client = self.client or httpx.Client(timeout=self.timeout_seconds)
        close_client = self.client is None
        try:
            headers = {
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json",
            }
            payload = {
                "model": self.model,
                "input": [
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_message},
                ],
            }
            response = client.post(f"{self.base_url.rstrip('/')}/responses", headers=headers, json=payload)
            if response.status_code >= 400:
                raise self._map_http_error(response)

            data = response.json()
            text = self._extract_text(data)
            usage = self._extract_usage(data)
            return ProviderResult(
                response=text,
                model=self.model,
                provider=self.provider_name,
                usage=usage,
                raw=data if isinstance(data, dict) else None,
            )
        except httpx.TimeoutException as exc:
            raise LLMProviderError("LLM request timed out", status_code=504) from exc
        except httpx.RequestError as exc:
            raise LLMProviderError("Unable to reach the LLM provider", status_code=503) from exc
        finally:
            if close_client:
                client.close()

    def health_check(self) -> dict[str, Any]:
        """Return a non-sensitive description of the provider configuration."""

        return {
            "provider": self.provider_name,
            "model": self.model,
            "base_url": self.base_url.rstrip("/"),
        }

    def _map_http_error(self, response: httpx.Response) -> LLMProviderError:
        """Translate HTTP errors into API-safe exceptions."""

        detail = self._extract_error_detail(response)

        if response.status_code in {401, 403}:
            return LLMProviderError(detail or "Invalid LLM API key", status_code=401)
        if response.status_code == 429:
            return LLMProviderError(detail or "LLM rate limit exceeded", status_code=429)
        if response.status_code >= 500:
            return LLMProviderError(detail or "LLM provider error", status_code=502)
        return LLMProviderError(detail or "LLM request failed", status_code=response.status_code)

    def _extract_error_detail(self, response: httpx.Response) -> str:
        """Extract a readable message from provider error payloads."""

        try:
            payload = response.json()
        except ValueError:
            text = response.text.strip()
            return text if text else ""

        if isinstance(payload, dict):
            error = payload.get("error")
            if isinstance(error, dict):
                message = error.get("message")
                if isinstance(message, str) and message.strip():
                    return message.strip()

            message = payload.get("message")
            if isinstance(message, str) and message.strip():
                return message.strip()

        text = response.text.strip()
        return text if text else ""

    def _extract_text(self, payload: dict[str, Any]) -> str:
        """Extract assistant text from an OpenAI-compatible response."""

        if "choices" in payload and payload["choices"]:
            choice = payload["choices"][0]
            message = choice.get("message") or {}
            if isinstance(message, dict):
                content = message.get("content")
                if isinstance(content, str) and content.strip():
                    return content.strip()
            text = choice.get("text")
            if isinstance(text, str) and text.strip():
                return text.strip()

        if "output_text" in payload and isinstance(payload["output_text"], str):
            return payload["output_text"].strip()

        if "output" in payload and isinstance(payload["output"], list):
            for item in payload["output"]:
                if not isinstance(item, dict):
                    continue
                content = item.get("content")
                if isinstance(content, list):
                    for block in content:
                        if isinstance(block, dict):
                            text = block.get("text")
                            if isinstance(text, str) and text.strip():
                                return text.strip()

        return "No response content returned by the provider."

    def _extract_usage(self, payload: dict[str, Any]) -> ProviderUsage | None:
        """Extract usage information when the provider returns it."""

        usage = payload.get("usage")
        if not isinstance(usage, dict):
            return None

        prompt_tokens = usage.get("prompt_tokens")
        completion_tokens = usage.get("completion_tokens")
        total_tokens = usage.get("total_tokens")

        if not any(isinstance(value, int) for value in (prompt_tokens, completion_tokens, total_tokens)):
            return None

        return ProviderUsage(
            prompt_tokens=prompt_tokens if isinstance(prompt_tokens, int) else None,
            completion_tokens=completion_tokens if isinstance(completion_tokens, int) else None,
            total_tokens=total_tokens if isinstance(total_tokens, int) else None,
        )
