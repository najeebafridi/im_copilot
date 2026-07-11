"""Routing orchestration for IM Copilot."""

from __future__ import annotations

import logging
import time
from dataclasses import dataclass, field
from functools import lru_cache

from app.core.config import get_settings
from app.services.router.config_loader import RouterConfig, get_router_config
from app.services.router.intent_classifier import RouterClassification, classify_intents
from app.services.router.query_normalizer import normalize_query

logger = logging.getLogger(__name__)


@dataclass(slots=True)
class RouterDecision:
    """Final routing decision after classification and overrides."""

    classification: RouterClassification
    selected_intent: str
    selected_node: str
    routing_time_ms: int
    debug_enabled: bool
    detected_intents: list[str] = field(default_factory=list)
    multiple_intents: bool = False

    def debug_payload(self) -> dict[str, object] | None:
        """Return the optional debug payload."""

        if not self.debug_enabled:
            return None
        return {
            "normalized_query": self.classification.normalized_query,
            "matched_keywords": self.classification.matched_keywords,
            "scores": self.classification.scores,
            "selected_intent": self.selected_intent,
            "selected_node": self.selected_node,
            "routing_time_ms": self.routing_time_ms,
        }


class RouterService:
    """Resolve the destination service for a question."""

    def __init__(self, config: RouterConfig, debug_enabled: bool) -> None:
        self.config = config
        self.debug_enabled = debug_enabled

    def route(self, question: str) -> RouterDecision:
        """Return the selected intent and node for a user question."""

        start = time.perf_counter()
        normalized_question = normalize_query(question)
        detected_intents = [intent.upper().strip() for intent in classify_intents(normalized_question) if intent.strip()]
        if not detected_intents:
            detected_intents = ["GENERAL"]

        selected_label = detected_intents[0]
        selected_intent = self._intent_to_node_key(selected_label)
        selected_node = self._intent_to_node(selected_intent)
        classification = self._build_classification(normalized_question, detected_intents, selected_intent)
        routing_time_ms = int((time.perf_counter() - start) * 1000)

        if get_settings().DEBUG:
            logger.info(
                "Router question=%s normalized=%s detected_intents=%s selected_intent=%s selected_node=%s routing_time_ms=%s",
                question,
                normalized_question,
                detected_intents,
                selected_intent,
                selected_node,
                routing_time_ms,
            )
            print(
                f"[ROUTER] Original Query: {question!r}\n"
                f"[ROUTER] Normalized Query: {normalized_question!r}\n"
                f"[ROUTER] Detected Intents: {','.join(detected_intents)}\n"
                f"[ROUTER] Selected Intent: {selected_label}\n"
                f"[ROUTER] Selected Tool: {selected_node}\n"
                f"[ROUTER] routing_time_ms={routing_time_ms}"
            )

        return RouterDecision(
            classification=classification,
            selected_intent=selected_intent,
            selected_node=selected_node,
            routing_time_ms=routing_time_ms,
            debug_enabled=self.debug_enabled,
            detected_intents=detected_intents,
            multiple_intents=len(detected_intents) > 1,
        )

    def _build_classification(self, normalized_question: str, detected_intents: list[str], selected_intent: str) -> RouterClassification:
        """Create a compatibility classification payload for debug output."""

        scores = {intent: 0 for intent in ("GREETING", "ACADEMIC", "POLICY", "UNKNOWN")}
        scores[selected_intent] = 100
        tokens = normalized_question.split()
        return RouterClassification(
            intent=selected_intent,
            confidence=100,
            scores=scores,
            matched_keywords=tokens,
            reason=f"Detected intents: {','.join(detected_intents)}.",
            normalized_query=normalized_question,
            tokens=tokens,
        )

    def _intent_to_node_key(self, label: str) -> str:
        """Map a classifier label to the existing router intent key."""

        mapping = {
            "SQL": "ACADEMIC",
            "RAG": "POLICY",
            "GENERAL": "GREETING",
        }
        return mapping.get(label.upper(), "GREETING")

    def _intent_to_node(self, intent: str) -> str:
        """Map an intent to the corresponding backend node."""

        mapping = {
            "GREETING": "Greeting Node",
            "ACADEMIC": "Academic SQL Tool",
            "POLICY": "RAG Tool",
            "UNKNOWN": "Fallback Node",
        }
        return mapping.get(intent, "Fallback Node")


@lru_cache
def get_router_service() -> RouterService:
    """Return the cached router service."""

    from app.core.config import get_settings

    settings = get_settings()
    return RouterService(config=get_router_config(), debug_enabled=settings.ROUTER_DEBUG)
