"""Schemas for the reusable LLM service."""

from __future__ import annotations

from pydantic import BaseModel, Field


class ChatRequest(BaseModel):
    """Input payload for the LLM test endpoint."""

    message: str = Field(min_length=1)


class ChatResponse(BaseModel):
    """Output payload from the LLM service."""

    response: str
    model: str
    provider: str

