"""Shared types for document processing."""

from __future__ import annotations

from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any


@dataclass(slots=True)
class ExtractedPage:
    """Single extracted page and its text."""

    page: int
    text: str
    source_file: str

    def to_dict(self) -> dict[str, Any]:
        """Convert the page record to a JSON-serializable dict."""

        return asdict(self)


@dataclass(slots=True)
class StructuredSection:
    """Logical section created after structure detection."""

    source_file: str
    document_type: str
    section_index: int
    chapter: str
    section: str
    subsection: str
    content: str
    page_start: int
    page_end: int

    def to_dict(self) -> dict[str, Any]:
        """Convert the section record to a JSON-serializable dict."""

        return asdict(self)


@dataclass(slots=True)
class ChunkRecord:
    """Chunk ready for embedding and Chroma insertion."""

    chunk_id: str
    source_file: str
    document_type: str
    page_start: int
    page_end: int
    chapter: str
    section: str
    subsection: str
    text: str

    def to_metadata(self) -> dict[str, Any]:
        """Return Chroma-compatible metadata."""

        return {
            "chunk_id": self.chunk_id,
            "source_file": self.source_file,
            "document_type": self.document_type,
            "page_start": self.page_start,
            "page_end": self.page_end,
            "chapter": self.chapter,
            "section": self.section,
            "subsection": self.subsection,
        }

    def to_dict(self) -> dict[str, Any]:
        """Convert the chunk to a JSON-serializable dict."""

        payload = self.to_metadata()
        payload["text"] = self.text
        return payload


@dataclass(slots=True)
class LoadedDocument:
    """A file that has been extracted into page-level text."""

    path: Path
    document_type: str
    pages: list[ExtractedPage]

