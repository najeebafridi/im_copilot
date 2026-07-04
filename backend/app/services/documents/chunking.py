"""Smart chunking for structured document sections."""

from __future__ import annotations

from app.services.documents.types import ChunkRecord, StructuredSection
from app.services.documents.utils import slugify


class Chunker:
    """Chunk sections while preserving structure and page context."""

    def __init__(self, chunk_size: int, chunk_overlap: int) -> None:
        self.chunk_size = max(1, chunk_size)
        self.chunk_overlap = max(0, min(chunk_overlap, chunk_size - 1))

    def chunk_sections(self, sections: list[StructuredSection]) -> list[ChunkRecord]:
        """Split sections into semantically meaningful chunks."""

        chunks: list[ChunkRecord] = []
        for section in sections:
            chunks.extend(self._chunk_section(section))
        return chunks

    def _chunk_section(self, section: StructuredSection) -> list[ChunkRecord]:
        """Chunk a single logical section."""

        words = section.content.split()
        if len(words) <= self.chunk_size:
            return [self._build_chunk(section, 1, section.content)]

        chunks: list[ChunkRecord] = []
        step = max(1, self.chunk_size - self.chunk_overlap)
        section_slug = self._section_slug(section)
        for chunk_number, start in enumerate(range(0, len(words), step), start=1):
            end = start + self.chunk_size
            chunk_words = words[start:end]
            if not chunk_words:
                continue
            text = " ".join(chunk_words).strip()
            if not text:
                continue
            chunk_id = f"{section_slug}_{section.page_start:03d}_{section.section_index:03d}_{chunk_number:03d}"
            chunks.append(
                ChunkRecord(
                    chunk_id=chunk_id,
                    source_file=section.source_file,
                    document_type=section.document_type,
                    page_start=section.page_start,
                    page_end=section.page_end,
                    chapter=section.chapter,
                    section=section.section,
                    subsection=section.subsection,
                    text=text,
                )
            )
        return chunks

    def _build_chunk(self, section: StructuredSection, chunk_number: int, text: str) -> ChunkRecord:
        """Build a chunk record for a section."""

        chunk_id = f"{self._section_slug(section)}_{section.page_start:03d}_{section.section_index:03d}_{chunk_number:03d}"
        return ChunkRecord(
            chunk_id=chunk_id,
            source_file=section.source_file,
            document_type=section.document_type,
            page_start=section.page_start,
            page_end=section.page_end,
            chapter=section.chapter,
            section=section.section,
            subsection=section.subsection,
            text=text,
        )

    def _section_slug(self, section: StructuredSection) -> str:
        """Build a stable slug for chunk IDs."""

        return slugify(f"{section.source_file}_{section.chapter}_{section.section}_{section.subsection}")

