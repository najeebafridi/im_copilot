"""Build grounded context blocks from retrieved chunks."""

from __future__ import annotations

from collections import defaultdict
from typing import Any


class ContextBuilder:
    """Format retrieved chunks into a structured context string."""

    def build(self, chunks: list[dict[str, Any]]) -> tuple[str, list[dict[str, str | None]]]:
        """Return the prompt context and source metadata."""

        normalized_items: list[dict[str, Any]] = []
        seen_signatures: set[tuple[str, str, str]] = set()

        for chunk in chunks:
            metadata = self._normalize_metadata(chunk.get("metadata") or {})
            text = str(chunk.get("text", "")).strip()
            signature = (metadata["document"], metadata["heading_path"], text)
            if signature in seen_signatures:
                continue
            seen_signatures.add(signature)
            normalized_items.append(
                {
                    "metadata": metadata,
                    "text": text,
                    "distance": self._distance_value(chunk.get("distance")),
                }
            )

        grouped: dict[tuple[str, str], list[dict[str, Any]]] = defaultdict(list)
        for item in normalized_items:
            metadata = item["metadata"]
            grouped[(metadata["document"], metadata["heading_path"])].append(item)

        ordered_groups = sorted(
            grouped.items(),
            key=lambda item: min(self._group_distance(candidate) for candidate in item[1]),
        )

        sections: list[str] = []
        sources: list[dict[str, str | None]] = []

        for _, group_items in ordered_groups:
            group_items.sort(key=self._group_sort_key)
            group_metadata = group_items[0]["metadata"]
            sections.append(
                "\n".join(
                    [
                        f"Document: {group_metadata['document']}",
                        f"Heading Path: {group_metadata['heading_path']}",
                        f"Pages: {group_metadata['pages']}",
                    ]
                )
            )

            for index, item in enumerate(group_items, start=1):
                metadata = item["metadata"]
                sources.append(
                    {
                        "type": "document",
                        "table": None,
                        "document": metadata["document"],
                        "chapter": metadata["chapter"],
                        "section": metadata["section"],
                        "heading_path": metadata["heading_path"],
                        "pages": metadata["pages"],
                    }
                )
                sections.append(
                    "\n".join(
                        [
                            f"Chunk {index}",
                            f"Document: {metadata['document']}",
                            f"Chapter: {metadata['chapter']}",
                            f"Section: {metadata['section']}",
                            f"Subsection: {metadata['subsection']}",
                            f"Heading Path: {metadata['heading_path']}",
                            f"Pages: {metadata['pages']}",
                            f"Section Index: {metadata['section_index']}",
                            f"Chunk Number: {metadata['chunk_number']}",
                            f"Contains Table: {metadata['contains_table']}",
                            "Content:",
                            item["text"],
                        ]
                    )
                )

        return "\n\n---\n\n".join(sections), sources

    def _normalize_metadata(self, metadata: dict[str, Any]) -> dict[str, Any]:
        """Convert retriever metadata into safe display strings."""

        document = str(metadata.get("source_file") or metadata.get("document") or "Unknown document")
        chapter = str(metadata.get("chapter") or "N/A")
        section = str(metadata.get("section") or "N/A")
        subsection = str(metadata.get("subsection") or "N/A")
        fallback_heading_path = " > ".join(part for part in (chapter, section, subsection) if part and part != "N/A")
        heading_path = str(metadata.get("heading_path") or fallback_heading_path or "N/A")
        page_start = metadata.get("page_start")
        page_end = metadata.get("page_end")
        section_index = self._int_value(metadata.get("section_index"))
        chunk_number = self._int_value(metadata.get("chunk_number"))
        contains_table = bool(metadata.get("contains_table", False))

        if isinstance(page_start, int) and isinstance(page_end, int):
            pages = str(page_start) if page_start == page_end else f"{page_start}-{page_end}"
        elif isinstance(page_start, int):
            pages = str(page_start)
        elif isinstance(page_end, int):
            pages = str(page_end)
        else:
            pages = "N/A"

        return {
            "document": document,
            "chapter": chapter,
            "section": section,
            "subsection": subsection,
            "heading_path": heading_path,
            "pages": pages,
            "section_index": section_index,
            "chunk_number": chunk_number,
            "contains_table": contains_table,
        }

    def _group_sort_key(self, item: dict[str, Any]) -> tuple[int, int, int, float]:
        """Sort items within a section-aware group."""

        metadata = item["metadata"]
        return (
            self._int_value(metadata.get("page_start")),
            self._int_value(metadata.get("section_index")),
            self._int_value(metadata.get("chunk_number")),
            item["distance"],
        )

    def _group_distance(self, item: dict[str, Any]) -> float:
        """Return the primary distance for a grouped item."""

        return item["distance"]

    def _distance_value(self, distance: Any) -> float:
        """Normalize a distance value for sorting."""

        if isinstance(distance, (int, float)):
            return float(distance)
        return float("inf")

    def _int_value(self, value: Any) -> int:
        """Convert a metadata value to a stable integer."""

        if isinstance(value, int):
            return value
        if isinstance(value, str) and value.isdigit():
            return int(value)
        return 0
