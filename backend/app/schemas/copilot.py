"""Schemas for the Phase 5 copilot chat endpoint."""

from __future__ import annotations

from pydantic import BaseModel, Field


class CopilotChatRequest(BaseModel):
    """Incoming chat request for grounded document answers."""

    conversation_id: str | None = None
    message: str = Field(min_length=1)


class CopilotSource(BaseModel):
    """Source used to ground the answer."""

    type: str | None = None
    table: str | None = None
    document: str
    chapter: str | None = None
    section: str | None = None
    heading_path: str | None = None
    pages: str | None = None


class CopilotMetadata(BaseModel):
    """Response metadata for the copilot endpoint."""

    provider: str
    model: str
    cached: bool
    latency_ms: int
    retrieved_chunks: int


class CopilotDebug(BaseModel):
    """Optional router debug information for development."""

    normalized_query: str
    matched_keywords: list[str]
    scores: dict[str, int]
    selected_intent: str
    selected_node: str
    routing_time_ms: int


class CopilotChatResponse(BaseModel):
    """Structured grounded answer returned to the client."""

    answer: str
    sources: list[CopilotSource]
    metadata: CopilotMetadata
    debug: CopilotDebug | None = None
