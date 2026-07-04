"""Load and validate configuration for the Phase 7A router."""

from __future__ import annotations

import json
from dataclasses import dataclass
from functools import lru_cache
from pathlib import Path
from typing import Any

from app.services.router.exceptions import RouterConfigurationError


@dataclass(slots=True)
class IntentGroupConfig:
    """Routing group metadata for a single intent."""

    id: str
    weight: int
    keywords: list[str]
    aliases: list[str]
    examples: list[str]


@dataclass(slots=True)
class IntentConfig:
    """Routing rules for one intent."""

    intent: str
    groups: list[IntentGroupConfig]
    keywords: list[str]


@dataclass(slots=True)
class NormalizationConfig:
    """Normalization switches loaded from JSON."""

    lowercase: bool
    remove_punctuation: bool
    collapse_spaces: bool
    trim: bool


@dataclass(slots=True)
class RouterRulesConfig:
    """Priority and scoring weights loaded from JSON."""

    priority: list[str]
    minimum_confidence: int
    primary_keyword_weight: int
    alias_weight: int
    example_weight: int
    group_bonus: int


@dataclass(slots=True)
class NegativeRuleConfig:
    """A routing override rule loaded from JSON."""

    if_contains: list[str]
    prefer: str


@dataclass(slots=True)
class RouterConfig:
    """Fully loaded router configuration bundle."""

    normalization: NormalizationConfig
    router_rules: RouterRulesConfig
    negative_rules: list[NegativeRuleConfig]
    intents: dict[str, IntentConfig]
    stopwords: set[str]
    fallback_response: str


class RouterConfigLoader:
    """Read all router configuration from backend/config/router."""

    def __init__(self, config_dir: Path | None = None) -> None:
        self.config_dir = config_dir or Path(__file__).resolve().parents[3] / "config" / "router"

    def load(self) -> RouterConfig:
        """Load and validate the router configuration bundle."""

        if not self.config_dir.exists():
            raise RouterConfigurationError(f"Router config directory not found: {self.config_dir}")

        normalization_data: dict[str, Any] | None = None
        router_rules_data: dict[str, Any] | None = None
        negative_rules_data: dict[str, Any] | None = None
        stopwords_data: dict[str, Any] | None = None
        fallback_data: dict[str, Any] | None = None
        intents: dict[str, IntentConfig] = {}

        for path in sorted(self.config_dir.glob("*.json")):
            payload = self._read_json(path)
            stem = path.stem.lower()

            if stem == "normalization":
                normalization_data = payload
                continue
            if stem == "router_rules":
                router_rules_data = payload
                continue
            if stem == "negative_rules":
                negative_rules_data = payload
                continue
            if stem == "stopwords":
                stopwords_data = payload
                continue
            if stem == "fallback":
                fallback_data = payload
                continue

            intent_name = str(payload.get("intent", "")).strip().upper()
            if intent_name:
                intents[intent_name] = self._parse_intent(payload, path)

        missing = []
        if normalization_data is None:
            missing.append("normalization.json")
        if router_rules_data is None:
            missing.append("router_rules.json")
        if negative_rules_data is None:
            missing.append("negative_rules.json")
        if stopwords_data is None:
            missing.append("stopwords.json")
        if fallback_data is None:
            missing.append("fallback.json")
        for required_intent in ("GREETING", "ACADEMIC", "POLICY"):
            if required_intent not in intents:
                missing.append(f"{required_intent.lower()}.json")
        if missing:
            raise RouterConfigurationError(f"Missing router configuration file(s): {', '.join(missing)}")

        return RouterConfig(
            normalization=self._parse_normalization(normalization_data or {}),
            router_rules=self._parse_router_rules(router_rules_data or {}),
            negative_rules=self._parse_negative_rules(negative_rules_data or {}),
            intents=intents,
            stopwords=self._parse_stopwords(stopwords_data or {}),
            fallback_response=self._parse_fallback(fallback_data or {}),
        )

    def _read_json(self, path: Path) -> dict[str, Any]:
        """Read one JSON file with graceful validation."""

        try:
            raw = path.read_text(encoding="utf-8")
            payload = json.loads(raw)
        except json.JSONDecodeError as exc:
            raise RouterConfigurationError(f"Invalid JSON in {path.name}: {exc}") from exc
        except OSError as exc:
            raise RouterConfigurationError(f"Could not read {path.name}: {exc}") from exc

        if not isinstance(payload, dict):
            raise RouterConfigurationError(f"Router config must be an object: {path.name}")
        return payload

    def _parse_normalization(self, payload: dict[str, Any]) -> NormalizationConfig:
        """Parse normalization switches from JSON."""

        return NormalizationConfig(
            lowercase=bool(payload.get("lowercase", True)),
            remove_punctuation=bool(payload.get("remove_punctuation", True)),
            collapse_spaces=bool(payload.get("collapse_spaces", True)),
            trim=bool(payload.get("trim", True)),
        )

    def _parse_router_rules(self, payload: dict[str, Any]) -> RouterRulesConfig:
        """Parse router scoring and priority settings."""

        priority = payload.get("priority")
        if not isinstance(priority, list) or not priority or not all(isinstance(item, str) for item in priority):
            raise RouterConfigurationError("router_rules.json must define a string priority list")

        return RouterRulesConfig(
            priority=[item.upper() for item in priority],
            minimum_confidence=int(payload.get("minimum_confidence", 0)),
            primary_keyword_weight=int(payload.get("primary_keyword_weight", 0)),
            alias_weight=int(payload.get("alias_weight", 0)),
            example_weight=int(payload.get("example_weight", 0)),
            group_bonus=int(payload.get("group_bonus", 0)),
        )

    def _parse_negative_rules(self, payload: dict[str, Any]) -> list[NegativeRuleConfig]:
        """Parse ordered override rules."""

        rules = payload.get("rules")
        if not isinstance(rules, list):
            raise RouterConfigurationError("negative_rules.json must define a rules list")

        parsed: list[NegativeRuleConfig] = []
        for index, item in enumerate(rules):
            if not isinstance(item, dict):
                raise RouterConfigurationError(f"Invalid negative rule at index {index}")
            if_contains = item.get("if_contains")
            prefer = str(item.get("prefer", "")).strip().upper()
            if not isinstance(if_contains, list) or not if_contains:
                raise RouterConfigurationError(f"negative rule {index} must define if_contains")
            if not all(isinstance(value, str) for value in if_contains):
                raise RouterConfigurationError(f"negative rule {index} must use strings")
            if not prefer:
                raise RouterConfigurationError(f"negative rule {index} must define prefer")
            if prefer not in {"GREETING", "ACADEMIC", "POLICY", "UNKNOWN"}:
                raise RouterConfigurationError(f"negative rule {index} has unsupported prefer target: {prefer}")
            parsed.append(
                NegativeRuleConfig(
                    if_contains=[value.lower() for value in if_contains],
                    prefer=prefer,
                )
            )
        return parsed

    def _parse_stopwords(self, payload: dict[str, Any]) -> set[str]:
        """Parse stopwords from JSON."""

        words = payload.get("words")
        if not isinstance(words, list) or not all(isinstance(word, str) for word in words):
            raise RouterConfigurationError("stopwords.json must define a words list")
        return {word.lower() for word in words}

    def _parse_fallback(self, payload: dict[str, Any]) -> str:
        """Parse the fallback response text."""

        response = str(payload.get("response", "")).strip()
        if not response:
            raise RouterConfigurationError("fallback.json must define a response")
        return response

    def _parse_intent(self, payload: dict[str, Any], path: Path) -> IntentConfig:
        """Parse an intent definition from JSON."""

        intent = str(payload.get("intent", "")).strip().upper()
        groups_data = payload.get("groups", [])
        keywords_data = payload.get("keywords", [])

        if not intent:
            raise RouterConfigurationError(f"Missing intent name in {path.name}")
        if groups_data and not isinstance(groups_data, list):
            raise RouterConfigurationError(f"Invalid groups list in {path.name}")
        if keywords_data and not isinstance(keywords_data, list):
            raise RouterConfigurationError(f"Invalid keywords list in {path.name}")

        groups: list[IntentGroupConfig] = []
        for index, group in enumerate(groups_data or []):
            if not isinstance(group, dict):
                raise RouterConfigurationError(f"Invalid intent group {index} in {path.name}")
            keywords = group.get("keywords", [])
            aliases = group.get("aliases", [])
            examples = group.get("examples", [])
            if not isinstance(keywords, list) or not all(isinstance(item, str) for item in keywords):
                raise RouterConfigurationError(f"Invalid keywords in group {index} of {path.name}")
            if not isinstance(aliases, list) or not all(isinstance(item, str) for item in aliases):
                raise RouterConfigurationError(f"Invalid aliases in group {index} of {path.name}")
            if not isinstance(examples, list) or not all(isinstance(item, str) for item in examples):
                raise RouterConfigurationError(f"Invalid examples in group {index} of {path.name}")
            groups.append(
                IntentGroupConfig(
                    id=str(group.get("id", f"group_{index}")),
                    weight=int(group.get("weight", 0)),
                    keywords=[item.lower() for item in keywords],
                    aliases=[item.lower() for item in aliases],
                    examples=[item.lower() for item in examples],
                )
            )

        if intent == "GREETING":
            if not isinstance(keywords_data, list) or not all(isinstance(item, str) for item in keywords_data):
                raise RouterConfigurationError(f"Invalid greeting keywords in {path.name}")
            return IntentConfig(
                intent=intent,
                groups=[],
                keywords=[item.lower() for item in keywords_data],
            )

        return IntentConfig(
            intent=intent,
            groups=groups,
            keywords=[item.lower() for item in keywords_data] if isinstance(keywords_data, list) else [],
        )


@lru_cache
def get_router_config() -> RouterConfig:
    """Return the cached router configuration bundle."""

    return RouterConfigLoader().load()
