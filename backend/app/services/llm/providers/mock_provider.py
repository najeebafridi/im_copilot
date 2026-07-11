"""Mock provider used for safe local development and testing."""

from __future__ import annotations

from dataclasses import dataclass
import json
import re
from typing import Any

from app.services.llm.providers.base_provider import BaseProvider, ProviderResult


@dataclass(slots=True)
class MockProvider(BaseProvider):
    """Return deterministic responses without making network calls."""

    model: str = "mock-model"
    provider_name: str = "mock"

    def generate(self, system_prompt: str, user_message: str) -> ProviderResult:
        """Return prompt-aware debugging output without making network calls."""

        response = self._build_debug_response(system_prompt=system_prompt, user_message=user_message)

        return ProviderResult(
            response=response,
            model=self.model,
            provider=self.provider_name,
        )

    def _build_debug_response(self, system_prompt: str, user_message: str) -> str:
        """Build a short, useful development response from the incoming prompt."""

        normalized = system_prompt.lower()
        if "intent classification engine" in normalized or "comma-separated list" in normalized:
            return self._build_intent_classifier_response(user_message)
        if "structured data:" in normalized:
            return self._build_sql_debug_response(system_prompt)
        if "supplied context:" in normalized:
            return self._build_rag_debug_response(system_prompt)

        return self._build_generic_debug_response(system_prompt, user_message)

    def _build_intent_classifier_response(self, user_message: str) -> str:
        """Return a deterministic intent classification for mock mode."""

        text = user_message.lower()
        matches: list[tuple[int, str]] = []

        for label, phrases in (
            ("GENERAL", ("hello", "hi", "hey", "thank you", "thanks", "who are you", "help me", "help me use im copilot")),
            ("SQL", ("gpa", "cgpa", "attendance", "credit hours", "grade", "grades", "timetable", "schedule", "transcript", "courses", "course")),
            ("RAG", ("probation", "policy", "hostel", "scholarship", "transfer", "fee", "admission", "handbook", "library", "rules", "university", "registration", "wifi", "transport", "detained", "detention")),
        ):
            position = self._first_match_position(text, phrases)
            if position is not None:
                matches.append((position, label))

        if not matches:
            return "GENERAL"

        ordered: list[str] = []
        for _, label in sorted(matches, key=lambda item: item[0]):
            if label not in ordered:
                ordered.append(label)
        return ",".join(ordered)

    def _build_rag_debug_response(self, system_prompt: str) -> str:
        """Summarize the retrieved context that would have been sent to an LLM."""

        context = self._extract_section(system_prompt, "Supplied context:")
        context_preview = self._truncate(context, 500)
        document_count = self._count_documents(context)
        retrieved_chunks = context.count("Chunk ")

        return "\n".join(
            [
                "[MOCK MODE]",
                "",
                "Prompt successfully built.",
                "Retrieved context received.",
                "The following context would be sent to the LLM.",
                "",
                "----------------------------------",
                "",
                f"Document Count: {document_count}",
                f"Retrieved Chunks: {retrieved_chunks}",
                "",
                "Context Preview:",
                "",
                context_preview or "(no context available)",
                "",
                "----------------------------------",
                "",
                "No external API request was made.",
            ]
        )

    def _build_sql_debug_response(self, system_prompt: str) -> str:
        """Summarize structured academic data without exposing huge payloads."""

        data_section = self._extract_section(system_prompt, "Structured data:")
        data_preview = self._truncate(data_section, 500)
        parsed_preview = self._pretty_json_preview(data_section)

        preview_block = parsed_preview or data_preview or "(no structured data available)"

        return "\n".join(
            [
                "[MOCK MODE]",
                "",
                "Academic data retrieved successfully.",
                "Structured data received:",
                "",
                preview_block,
                "",
                "No external LLM call was made.",
            ]
        )

    def _build_generic_debug_response(self, system_prompt: str, user_message: str) -> str:
        """Fallback debug output for non-RAG, non-SQL prompts."""

        prompt_preview = self._truncate(system_prompt, 500)
        return "\n".join(
            [
                "[MOCK MODE]",
                "",
                "Prompt successfully built.",
                "No external LLM call was made.",
                "",
                f"User message: {user_message}",
                "",
                "Prompt Preview:",
                "",
                prompt_preview or "(empty prompt)",
            ]
        )

    def _extract_section(self, prompt: str, marker: str) -> str:
        """Extract text that follows a named prompt marker."""

        pattern = re.escape(marker) + r"\s*(.*)"
        match = re.search(pattern, prompt, flags=re.IGNORECASE | re.DOTALL)
        if not match:
            return ""
        return match.group(1).strip()

    def _count_documents(self, context: str) -> int:
        """Count distinct document headers inside a retrieved context block."""

        documents = re.findall(r"^Document:\s*(.+)$", context, flags=re.IGNORECASE | re.MULTILINE)
        unique_documents = {document.strip() for document in documents if document.strip()}
        return len(unique_documents)

    def _pretty_json_preview(self, data_section: str) -> str:
        """Render a compact JSON preview when the structured data is valid JSON."""

        try:
            payload: Any = json.loads(data_section)
        except Exception:
            return ""

        if isinstance(payload, dict):
            limited: dict[str, Any] = {}
            for index, (key, value) in enumerate(payload.items()):
                if index >= 5:
                    break
                limited[key] = value
            return json.dumps(limited, indent=2, ensure_ascii=False)

        if isinstance(payload, list):
            return json.dumps(payload[:3], indent=2, ensure_ascii=False)

        return json.dumps(payload, indent=2, ensure_ascii=False)

    def _truncate(self, text: str, limit: int) -> str:
        """Trim long text to a safe preview length."""

        normalized = re.sub(r"\s+\n", "\n", text).strip()
        if len(normalized) <= limit:
            return normalized
        return normalized[:limit].rstrip() + "..."

    def _first_match_position(self, text: str, phrases: tuple[str, ...]) -> int | None:
        """Return the earliest phrase position in the text."""

        positions = [text.find(phrase) for phrase in phrases if phrase in text]
        if not positions:
            return None
        return min(positions)
