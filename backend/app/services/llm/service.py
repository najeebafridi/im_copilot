"""Compatibility wrapper for the refactored LLM service."""

from __future__ import annotations

from app.services.llm.llm_service import LLMGenerationResult, LLMService, get_llm_service

__all__ = ["LLMGenerationResult", "LLMService", "get_llm_service"]
