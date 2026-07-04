"""Retrieval service for querying stored chunks."""

from __future__ import annotations

from app.core.config import get_settings
from app.services.documents.chroma_store import ChromaStore
from app.services.documents.embeddings import LocalHashEmbeddingService


class RetrievalService:
    """Return top-k chunks for a query string."""

    def __init__(self, chroma_path: str | None = None, embedding_model: str | None = None) -> None:
        settings = get_settings()
        self.embedding_service = LocalHashEmbeddingService(embedding_model or settings.EMBEDDING_MODEL)
        self.store = ChromaStore(chroma_path or settings.CHROMA_PATH, self.embedding_service)

    def search(self, query: str, k: int) -> list[dict[str, object]]:
        """Retrieve the most relevant chunks for a query."""

        print(f"[SEARCH] Querying top {k} result(s) for: {query}")
        results = self.store.query(query=query, k=k)
        print(f"[SEARCH] Retrieved {len(results)} result(s)")
        return results

