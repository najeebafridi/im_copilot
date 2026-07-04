"""Config-driven intent classification for the Phase 7A router."""

from __future__ import annotations

import re
from dataclasses import dataclass

from app.services.router.config_loader import IntentConfig, NormalizationConfig, RouterConfig, RouterRulesConfig


@dataclass(slots=True)
class NormalizedQuery:
    """Normalized text and token output."""

    normalized_query: str
    tokens: list[str]


@dataclass(slots=True)
class RouterClassification:
    """Classification output before negative-rule and priority resolution."""

    intent: str
    confidence: int
    scores: dict[str, int]
    matched_keywords: list[str]
    reason: str
    normalized_query: str
    tokens: list[str]


class IntentClassifier:
    """Score the supported intents using only loaded JSON configuration."""

    def __init__(self, config: RouterConfig) -> None:
        self.config = config

    def normalize(self, query: str) -> NormalizedQuery:
        """Normalize a query using the configured operations."""

        text = query
        normalization = self.config.normalization

        if normalization.lowercase:
            text = text.lower()
        if normalization.remove_punctuation:
            text = re.sub(r"[^\w\s]", " ", text)
        if normalization.collapse_spaces:
            text = re.sub(r"\s+", " ", text)
        if normalization.trim:
            text = text.strip()

        tokens = [token for token in text.split() if token and token not in self.config.stopwords]
        return NormalizedQuery(normalized_query=text, tokens=tokens)

    def classify(self, query: str) -> RouterClassification:
        """Return intent scores and matched keywords for a question."""

        normalized = self.normalize(query)
        rules = self.config.router_rules

        scores: dict[str, int] = {intent: 0 for intent in self._supported_intents()}
        matched_keywords: list[str] = []

        for intent_name, intent_config in self.config.intents.items():
            if intent_name == "GREETING":
                score, matches = self._score_keywords(
                    normalized.normalized_query,
                    normalized.tokens,
                    intent_config.keywords,
                    rules.primary_keyword_weight,
                )
                scores[intent_name] = score
                self._extend_unique(matched_keywords, matches)
                continue

            intent_score = 0
            intent_matches: list[str] = []

            for group in intent_config.groups:
                group_score = 0
                group_matches: list[str] = []

                keyword_score, keyword_matches = self._score_keywords(
                    normalized.normalized_query,
                    normalized.tokens,
                    group.keywords,
                    rules.primary_keyword_weight,
                )
                alias_score, alias_matches = self._score_keywords(
                    normalized.normalized_query,
                    normalized.tokens,
                    group.aliases,
                    rules.alias_weight,
                )
                example_score, example_matches = self._score_keywords(
                    normalized.normalized_query,
                    normalized.tokens,
                    group.examples,
                    rules.example_weight,
                )

                group_score += keyword_score + alias_score + example_score
                if keyword_matches or alias_matches or example_matches:
                    group_score += rules.group_bonus
                    group_matches.extend(keyword_matches)
                    group_matches.extend(alias_matches)
                    group_matches.extend(example_matches)

                if group_matches:
                    intent_score += group_score + group.weight
                    intent_matches.extend(group_matches)

            if intent_config.keywords:
                keyword_score, keyword_matches = self._score_keywords(
                    normalized.normalized_query,
                    normalized.tokens,
                    intent_config.keywords,
                    rules.primary_keyword_weight,
                )
                intent_score += keyword_score
                intent_matches.extend(keyword_matches)

            scores[intent_name] = intent_score
            self._extend_unique(matched_keywords, intent_matches)

        selected_intent = self._select_highest_scoring_intent(scores, rules)
        confidence = scores.get(selected_intent, 0)
        reason = self._build_reason(selected_intent, confidence, matched_keywords)

        return RouterClassification(
            intent=selected_intent,
            confidence=confidence,
            scores=scores,
            matched_keywords=matched_keywords,
            reason=reason,
            normalized_query=normalized.normalized_query,
            tokens=normalized.tokens,
        )

    def _score_keywords(
        self,
        normalized_query: str,
        tokens: list[str],
        keywords: list[str],
        weight: int,
    ) -> tuple[int, list[str]]:
        """Score keyword phrases against the normalized query."""

        score = 0
        matches: list[str] = []
        token_set = set(tokens)

        for keyword in keywords:
            if " " in keyword:
                if keyword in normalized_query:
                    score += weight
                    matches.append(keyword)
            elif keyword in token_set:
                score += weight
                matches.append(keyword)

        return score, matches

    def _select_highest_scoring_intent(self, scores: dict[str, int], rules: RouterRulesConfig) -> str:
        """Choose the best intent using confidence and configured priority."""

        highest_score = max(scores.values()) if scores else 0
        if highest_score < rules.minimum_confidence:
            return "UNKNOWN"

        top_intents = [intent for intent, score in scores.items() if score == highest_score]
        if len(top_intents) == 1:
            return top_intents[0]

        for preferred_intent in rules.priority:
            if preferred_intent in top_intents:
                return preferred_intent

        return top_intents[0]

    def _build_reason(self, intent: str, confidence: int, matched_keywords: list[str]) -> str:
        """Create a short explanation for the selected intent."""

        if intent == "UNKNOWN":
            return "No intent reached the minimum confidence threshold."
        if matched_keywords:
            return f"Matched {intent.lower()} keywords with confidence {confidence}."
        return f"Selected {intent.lower()} by score."

    def _extend_unique(self, target: list[str], values: list[str]) -> None:
        """Append items while preserving order and avoiding duplicates."""

        for value in values:
            if value not in target:
                target.append(value)

    def _supported_intents(self) -> list[str]:
        """Return the intents that are scored in debug output."""

        return [intent for intent in self.config.intents if intent != "UNKNOWN"]
