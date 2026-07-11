"""Retrieval service for querying stored chunks."""

from __future__ import annotations

from collections import defaultdict

from app.core.config import get_settings
from app.services.documents.chroma_store import ChromaStore
from app.services.documents.embeddings import LocalHashEmbeddingService
from app.services.documents.types import build_heading_path


class RetrievalService:
    """Return top-k chunks for a query string."""

    def __init__(self, chroma_path: str | None = None, embedding_model: str | None = None) -> None:
        settings = get_settings()
        self.embedding_service = LocalHashEmbeddingService(embedding_model or settings.EMBEDDING_MODEL)
        self.store = ChromaStore(chroma_path or settings.CHROMA_PATH, self.embedding_service)

    def search(self, query: str, k: int) -> list[dict[str, object]]:
        """Retrieve the most relevant chunks for a query."""

        print(f"[SEARCH] Querying top {k} result(s) for: {query}")
        search_k = max(k * 4, k + 8, 20)
        candidates = self.store.query(query=query, k=search_k)
        results = self._rank_candidates(candidates, k)
        print(f"[SEARCH] Retrieved {len(results)} result(s) from {len(candidates)} candidate(s)")
        return results

    def _rank_candidates(self, candidates: list[dict[str, object]], k: int) -> list[dict[str, object]]:
        """Deduplicate and regroup candidate chunks before returning them."""

        grouped: dict[tuple[str, str], list[dict[str, object]]] = defaultdict(list)
        seen_signatures: set[tuple[str, str, str]] = set()

        for candidate in candidates:
            metadata = dict(candidate.get("metadata") or {})
            document = str(metadata.get("source_file") or metadata.get("document") or "Unknown document")
            heading_path = str(
                metadata.get("heading_path")
                or build_heading_path(
                    str(metadata.get("chapter") or ""),
                    str(metadata.get("section") or ""),
                    str(metadata.get("subsection") or ""),
                )
            )
            text = str(candidate.get("text") or "").strip()
            signature = (
                str(metadata.get("chunk_id") or ""),
                heading_path,
                text,
            )
            if signature in seen_signatures:
                continue
            seen_signatures.add(signature)

            candidate["metadata"] = metadata
            grouped[(document, heading_path)].append(candidate)

        ordered_groups = sorted(
            grouped.items(),
            key=lambda item: min(self._distance_value(candidate) for candidate in item[1]),
        )

        ordered: list[dict[str, object]] = []
        for _, group_candidates in ordered_groups:
            ordered.extend(
                sorted(
                    group_candidates,
                    key=self._candidate_sort_key,
                )
            )

        return ordered[:k]

    def _candidate_sort_key(self, candidate: dict[str, object]) -> tuple[float, int, int, int, str]:
        """Sort chunks by similarity and document order."""

        metadata = dict(candidate.get("metadata") or {})
        page_start = self._int_value(metadata.get("page_start"))
        section_index = self._int_value(metadata.get("section_index"))
        chunk_number = self._int_value(metadata.get("chunk_number"))
        heading_path = str(metadata.get("heading_path") or "")
        return (self._distance_value(candidate), page_start, section_index, chunk_number, heading_path)

    def _distance_value(self, candidate: dict[str, object]) -> float:
        """Normalize the Chroma distance for sorting."""

        distance = candidate.get("distance")
        if isinstance(distance, (int, float)):
            return float(distance)
        return float("inf")

    def _int_value(self, value: object) -> int:
        """Convert a metadata field to a stable integer sort key."""

        if isinstance(value, int):
            return value
        if isinstance(value, str) and value.isdigit():
            return int(value)
        return 0
