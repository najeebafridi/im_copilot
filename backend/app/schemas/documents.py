"""Schemas for document ingestion and retrieval APIs."""

from __future__ import annotations

from pydantic import BaseModel


class IngestResponse(BaseModel):
    """Response after document ingestion."""

    documents_processed: int
    chunks_created: int


class RetrievalResult(BaseModel):
    """Single retrieved chunk with metadata."""

    text: str
    metadata: dict[str, object]
    distance: float | None = None


class RetrievalResponse(BaseModel):
    """Retrieval endpoint response."""

    query: str
    results: list[RetrievalResult]

