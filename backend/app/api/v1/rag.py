"""Retrieval testing endpoint."""

from __future__ import annotations

from fastapi import APIRouter, Query

from app.schemas.documents import RetrievalResponse, RetrievalResult
from app.services.documents.retrieval import RetrievalService

router = APIRouter(prefix="/rag", tags=["rag"])


@router.get("/search", response_model=RetrievalResponse)
def search_documents(
    query: str = Query(..., min_length=1),
    k: int = Query(5, ge=1, le=20),
) -> RetrievalResponse:
    """Return top-k retrieved chunks for the query string."""

    service = RetrievalService()
    results = service.search(query=query, k=k)
    return RetrievalResponse(
        query=query,
        results=[
            RetrievalResult(
                text=str(item["text"]),
                metadata=dict(item["metadata"]),
                distance=item.get("distance"),
            )
            for item in results
        ],
    )

