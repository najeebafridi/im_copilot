"""Validate and lightly clean LLM answers."""

from __future__ import annotations

import re

from app.services.llm.exceptions import LLMResponseValidationError


class AnswerValidator:
    """Apply minimal response checks for grounded answers."""

    GENERIC_PREFIXES = (
        "as an ai language model",
        "i am an ai language model",
        "as a language model",
    )

    def validate(self, answer: str) -> str:
        """Return a cleaned answer or raise if it is unusable."""

        cleaned = answer.strip()
        cleaned = self._remove_generic_prefix(cleaned)
        cleaned = re.sub(r"\s+", " ", cleaned).strip()

        if not cleaned:
            raise LLMResponseValidationError("Empty response returned by the copilot pipeline")

        return cleaned

    def _remove_generic_prefix(self, answer: str) -> str:
        """Strip common generic AI phrases from the start of an answer."""

        lowered = answer.lower()
        for prefix in self.GENERIC_PREFIXES:
            if lowered.startswith(prefix):
                return answer[len(prefix) :].lstrip(" ,:-")
        return answer
