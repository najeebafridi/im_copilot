"""Build grounded context blocks from retrieved chunks."""

from __future__ import annotations

from typing import Any


class ContextBuilder:
    """Format retrieved chunks into a structured context string."""

    def build(self, chunks: list[dict[str, Any]]) -> tuple[str, list[dict[str, str | None]]]:
        """Return the prompt context and source metadata."""

        sections: list[str] = []
        sources: list[dict[str, str | None]] = []

        for index, chunk in enumerate(chunks, start=1):
            metadata = self._normalize_metadata(chunk.get("metadata") or {})
            sources.append(
                {
                    "type": "document",
                    "table": None,
                    "document": metadata["document"],
                    "chapter": metadata["chapter"],
                    "section": metadata["section"],
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
                        f"Pages: {metadata['pages']}",
                        "Content:",
                        str(chunk.get("text", "")).strip(),
                    ]
                )
            )

        return "\n\n---\n\n".join(sections), sources

    def _normalize_metadata(self, metadata: dict[str, Any]) -> dict[str, str]:
        """Convert retriever metadata into safe display strings."""

        document = str(metadata.get("source_file") or metadata.get("document") or "Unknown document")
        chapter = str(metadata.get("chapter") or "N/A")
        section = str(metadata.get("section") or "N/A")
        subsection = str(metadata.get("subsection") or "N/A")
        page_start = metadata.get("page_start")
        page_end = metadata.get("page_end")

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
            "pages": pages,
        }
