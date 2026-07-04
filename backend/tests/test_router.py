"""Tests for the configuration-driven router."""

from __future__ import annotations

from app.core.config import get_settings
from app.services.router.config_loader import get_router_config
from app.services.router.router_service import get_router_service


def test_router_config_loads_all_intents() -> None:
    """The router should load its intent data from JSON files."""

    config = get_router_config()

    assert "GREETING" in config.intents
    assert "ACADEMIC" in config.intents
    assert "POLICY" in config.intents
    assert config.router_rules.minimum_confidence > 0


def test_router_selects_greeting_intent() -> None:
    """Greeting messages should route to the greeting node."""

    service = get_router_service()
    decision = service.route("Hi")

    assert decision.selected_intent == "GREETING"
    assert decision.selected_node == "Greeting Node"
    assert decision.debug_payload() is None


def test_router_applies_negative_rule_for_policy_questions() -> None:
    """Attendance policy questions should route to the policy node."""

    service = get_router_service()
    decision = service.route("What is attendance policy?")

    assert decision.selected_intent == "POLICY"
    assert decision.selected_node == "RAG Tool"
    assert "policy" in decision.classification.matched_keywords


def test_router_falls_back_for_out_of_domain_questions() -> None:
    """Unsupported questions should fall back cleanly."""

    service = get_router_service()
    decision = service.route("Who won the FIFA World Cup?")

    assert decision.selected_intent == "UNKNOWN"
    assert decision.selected_node == "Fallback Node"


def test_router_debug_mode_can_be_enabled(monkeypatch) -> None:
    """The debug block should be controlled by ROUTER_DEBUG."""

    monkeypatch.setenv("ROUTER_DEBUG", "True")
    get_settings.cache_clear()
    get_router_service.cache_clear()

    try:
        service = get_router_service()
        decision = service.route("What is my CGPA?")
        debug = decision.debug_payload()

        assert service.debug_enabled is True
        assert debug is not None
        assert debug["selected_intent"] == "ACADEMIC"
        assert debug["selected_node"] == "Academic SQL Tool"
        assert "cgpa" in debug["matched_keywords"]
    finally:
        get_router_service.cache_clear()
        get_settings.cache_clear()
