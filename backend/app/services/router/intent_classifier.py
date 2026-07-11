"""LLM-backed intent classification for the router."""

from __future__ import annotations

import logging
import re
from dataclasses import dataclass
from functools import lru_cache
from typing import Final

from app.services.llm.exceptions import LLMConfigurationError, LLMProviderError
from app.services.llm.llm_service import LLMService
from app.services.router.query_normalizer import normalize_query

logger = logging.getLogger(__name__)

SUPPORTED_INTENTS: Final[tuple[str, ...]] = ("SQL", "RAG", "GENERAL")
INTENT_TO_NODE: Final[dict[str, str]] = {
    "SQL": "ACADEMIC",
    "RAG": "POLICY",
    "GENERAL": "GREETING",
}


@dataclass(slots=True)
class NormalizedQuery:
    """Normalized text and token output."""

    normalized_query: str
    tokens: list[str]


@dataclass(slots=True)
class RouterClassification:
    """Compatibility wrapper used by the router debug payload."""

    intent: str
    confidence: int
    scores: dict[str, int]
    matched_keywords: list[str]
    reason: str
    normalized_query: str
    tokens: list[str]


@dataclass(slots=True)
class IntentClassificationResult:
    """Internal result returned by the LLM classifier."""

    intents: list[str]
    raw_response: str


class IntentClassifier:
    """Compatibility class that now uses the LLM-backed classifier."""

    def __init__(self, _config: object | None = None) -> None:
        self.config = _config

    def normalize(self, query: str) -> NormalizedQuery:
        """Keep the existing helper shape for compatibility."""

        normalized = normalize_query(query)
        return NormalizedQuery(normalized_query=normalized, tokens=normalized.split())

    def classify(self, query: str) -> RouterClassification:
        """Return a compatibility classification object."""

        normalized = self.normalize(query)
        intents = classify_intents(normalized.normalized_query)
        selected_intent = intents[0] if intents else "GENERAL"
        selected_node = INTENT_TO_NODE.get(selected_intent, "GREETING")
        node_scores = {node: 0 for node in ("GREETING", "ACADEMIC", "POLICY", "UNKNOWN")}
        node_scores[selected_node] = 100

        return RouterClassification(
            intent=selected_node,
            confidence=100,
            scores=node_scores,
            matched_keywords=normalized.tokens,
            reason=f"Detected intents: {','.join(intents) if intents else 'GENERAL'}.",
            normalized_query=normalized.normalized_query,
            tokens=normalized.tokens,
        )


def classify_intents(query: str) -> list[str]:
    """Classify a query into one or more supported routing intents."""

    result = _classify_intents(query)
    return result.intents


@lru_cache(maxsize=1)
def _get_llm_service() -> LLMService:
    """Create and cache the shared LLM service."""

    return LLMService.from_settings()


def _classify_intents(query: str) -> IntentClassificationResult:
    """Run the lightweight classifier prompt and parse the response."""

    llm_service = _get_llm_service()
    generation = llm_service.generate_with_metadata(message=query, prompt_name="intent_classifier")
    intents = _parse_intents(generation.response.response)
    if not intents:
        intents = ["GENERAL"]

    return IntentClassificationResult(intents=intents, raw_response=generation.response.response)


def _parse_intents(raw_response: str) -> list[str]:
    """Parse a comma-separated intent response safely."""

    matches = re.findall(r"\b(SQL|RAG|GENERAL)\b", raw_response.upper())
    ordered: list[str] = []
    for match in matches:
        if match not in ordered:
            ordered.append(match)
    return ordered


__all__ = [
    "IntentClassifier",
    "IntentClassificationResult",
    "NormalizedQuery",
    "RouterClassification",
    "classify_intents",
]
