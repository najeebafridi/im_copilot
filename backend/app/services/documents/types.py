"""Shared types for document processing."""

from __future__ import annotations

from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any


def build_heading_path(chapter: str, section: str, subsection: str) -> str:
    """Build a compact hierarchical heading path."""

    parts = [part.strip() for part in (chapter, section, subsection) if part.strip()]
    return " > ".join(parts)


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
    heading_path: str = ""

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
    section_index: int = 0
    chunk_number: int = 1
    contains_table: bool = False
    heading_path: str = ""

    def to_metadata(self) -> dict[str, Any]:
        """Return Chroma-compatible metadata."""

        heading_path = self.heading_path or build_heading_path(self.chapter, self.section, self.subsection)
        return {
            "chunk_id": self.chunk_id,
            "source_file": self.source_file,
            "document_type": self.document_type,
            "page_start": self.page_start,
            "page_end": self.page_end,
            "chapter": self.chapter,
            "section": self.section,
            "subsection": self.subsection,
            "section_index": self.section_index,
            "chunk_number": self.chunk_number,
            "heading_path": heading_path,
            "contains_table": self.contains_table,
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
