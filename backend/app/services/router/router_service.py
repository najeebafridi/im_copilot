"""Routing orchestration for IM Copilot."""

from __future__ import annotations

import logging
import time
from dataclasses import dataclass
from functools import lru_cache

from app.services.router.config_loader import RouterConfig, get_router_config
from app.services.router.intent_classifier import IntentClassifier, RouterClassification

logger = logging.getLogger(__name__)


@dataclass(slots=True)
class RouterDecision:
    """Final routing decision after classification and overrides."""

    classification: RouterClassification
    selected_intent: str
    selected_node: str
    routing_time_ms: int
    debug_enabled: bool

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
        self.classifier = IntentClassifier(config)

    def route(self, question: str) -> RouterDecision:
        """Return the selected intent and node for a user question."""

        start = time.perf_counter()
        classification = self.classifier.classify(question)
        selected_intent = self._apply_negative_rules(classification)
        selected_node = self._intent_to_node(selected_intent)
        final_confidence = classification.scores.get(selected_intent, classification.confidence)
        classification.intent = selected_intent
        classification.confidence = final_confidence
        routing_time_ms = int((time.perf_counter() - start) * 1000)

        logger.info(
            "Router question=%s normalized=%s matched_keywords=%s scores=%s confidence=%s selected_intent=%s selected_node=%s routing_time_ms=%s",
            question,
            classification.normalized_query,
            classification.matched_keywords,
            classification.scores,
            final_confidence,
            selected_intent,
            selected_node,
            routing_time_ms,
        )
        print(
            f"[ROUTER] question={question!r} normalized={classification.normalized_query!r} "
            f"matched_keywords={classification.matched_keywords} scores={classification.scores} "
            f"confidence={final_confidence} selected_intent={selected_intent} "
            f"selected_node={selected_node} routing_time_ms={routing_time_ms}"
        )

        return RouterDecision(
            classification=classification,
            selected_intent=selected_intent,
            selected_node=selected_node,
            routing_time_ms=routing_time_ms,
            debug_enabled=self.debug_enabled,
        )

    def _apply_negative_rules(self, classification: RouterClassification) -> str:
        """Apply ordered override rules before final route selection."""

        normalized_text = classification.normalized_query
        tokens = set(classification.tokens)
        scores = dict(classification.scores)

        for rule in self.config.negative_rules:
            matched_terms = self._matched_override_terms(rule.if_contains, normalized_text, tokens)
            if matched_terms:
                preferred = rule.prefer
                scores[preferred] = max(scores.values(), default=0) + self.config.router_rules.group_bonus + self.config.router_rules.primary_keyword_weight
                classification.scores = scores
                for term in matched_terms:
                    if term not in classification.matched_keywords:
                        classification.matched_keywords.append(term)
                return preferred

        selected_intent = classification.intent
        classification.scores = scores
        return selected_intent

    def _matched_override_terms(self, phrases: list[str], normalized_text: str, tokens: set[str]) -> list[str]:
        """Return the override terms that matched the query."""

        matches: list[str] = []
        for phrase in phrases:
            phrase = phrase.lower().strip()
            if " " in phrase:
                if phrase in normalized_text:
                    matches.append(phrase)
            elif phrase in tokens:
                matches.append(phrase)
        return matches

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
