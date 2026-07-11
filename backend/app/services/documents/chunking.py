"""Smart chunking for structured document sections."""

from __future__ import annotations

from dataclasses import dataclass
import re

from app.services.documents.cleaning import TABLE_BEGIN_MARKERS, TABLE_END_MARKERS
from app.services.documents.types import ChunkRecord, StructuredSection, build_heading_path
from app.services.documents.utils import slugify


@dataclass(slots=True)
class ContentBlock:
    """Atomic block preserved during chunking."""

    text: str
    kind: str
    word_count: int
    contains_table: bool = False


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

        blocks = self._expand_blocks(self._split_into_blocks(section.content))
        if not blocks:
            return []

        chunks: list[ChunkRecord] = []
        current_blocks: list[ContentBlock] = []
        current_words = 0
        chunk_number = 0

        for block in blocks:
            if current_blocks and current_words + block.word_count > self.chunk_size and block.kind != "table":
                chunk_number += 1
                chunks.append(self._build_chunk(section, chunk_number, current_blocks))
                current_blocks = self._build_overlap(current_blocks)
                current_words = sum(item.word_count for item in current_blocks)

            current_blocks.append(block)
            current_words += block.word_count

            if block.kind == "table" and current_words >= self.chunk_size:
                chunk_number += 1
                chunks.append(self._build_chunk(section, chunk_number, current_blocks))
                current_blocks = self._build_overlap(current_blocks)
                current_words = sum(item.word_count for item in current_blocks)

        if current_blocks:
            chunk_number += 1
            chunks.append(self._build_chunk(section, chunk_number, current_blocks))

        return chunks

    def _split_into_blocks(self, content: str) -> list[ContentBlock]:
        """Split section content into paragraph, list, and table blocks."""

        raw_blocks = [block.strip() for block in re.split(r"\n\s*\n", content) if block.strip()]
        blocks: list[ContentBlock] = []

        for raw_block in raw_blocks:
            kind = self._classify_block(raw_block)
            blocks.append(
                ContentBlock(
                    text=raw_block.strip(),
                    kind=kind,
                    word_count=self._word_count(raw_block),
                    contains_table=kind == "table",
                )
            )

        return blocks

    def _expand_blocks(self, blocks: list[ContentBlock]) -> list[ContentBlock]:
        """Split oversized blocks only when necessary."""

        expanded: list[ContentBlock] = []
        for block in blocks:
            if block.word_count <= self.chunk_size:
                expanded.append(block)
                continue

            expanded.extend(self._split_oversized_block(block))

        return expanded

    def _split_oversized_block(self, block: ContentBlock) -> list[ContentBlock]:
        """Split a large block while preserving the most meaningful boundaries."""

        if block.kind == "table":
            return self._split_table_block(block)
        return self._split_text_block(block)

    def _split_table_block(self, block: ContentBlock) -> list[ContentBlock]:
        """Split an oversized table by row groups as a last resort."""

        rows = [line.strip() for line in block.text.splitlines() if line.strip()]
        if len(rows) <= 2:
            return [block]

        pieces: list[ContentBlock] = []
        buffer: list[str] = []
        buffer_words = 0

        for row in rows:
            row_words = self._word_count(row)
            if buffer and buffer_words + row_words > self.chunk_size:
                text = "\n".join(buffer).strip()
                pieces.append(ContentBlock(text=text, kind="table", word_count=self._word_count(text), contains_table=True))
                buffer = []
                buffer_words = 0
            buffer.append(row)
            buffer_words += row_words

        if buffer:
            text = "\n".join(buffer).strip()
            pieces.append(ContentBlock(text=text, kind="table", word_count=self._word_count(text), contains_table=True))

        return pieces or [block]

    def _split_text_block(self, block: ContentBlock) -> list[ContentBlock]:
        """Split a large paragraph or list block by sentences and words."""

        sentences = [sentence.strip() for sentence in re.split(r"(?<=[.!?])\s+", block.text) if sentence.strip()]
        if len(sentences) <= 1:
            return self._split_by_words(block.text, block.kind)

        pieces: list[ContentBlock] = []
        buffer: list[str] = []
        buffer_words = 0

        for sentence in sentences:
            sentence_words = self._word_count(sentence)
            if buffer and buffer_words + sentence_words > self.chunk_size:
                text = " ".join(buffer).strip()
                pieces.append(ContentBlock(text=text, kind=block.kind, word_count=self._word_count(text), contains_table=False))
                buffer = []
                buffer_words = 0
            buffer.append(sentence)
            buffer_words += sentence_words

        if buffer:
            text = " ".join(buffer).strip()
            pieces.append(ContentBlock(text=text, kind=block.kind, word_count=self._word_count(text), contains_table=False))

        if pieces and any(piece.word_count > self.chunk_size for piece in pieces):
            flattened: list[ContentBlock] = []
            for piece in pieces:
                if piece.word_count > self.chunk_size:
                    flattened.extend(self._split_by_words(piece.text, piece.kind))
                else:
                    flattened.append(piece)
            return flattened

        return pieces or [block]

    def _split_by_words(self, text: str, kind: str) -> list[ContentBlock]:
        """Split a block by words when no better boundary is available."""

        words = text.split()
        if len(words) <= self.chunk_size:
            return [ContentBlock(text=text.strip(), kind=kind, word_count=len(words), contains_table=False)]

        pieces: list[ContentBlock] = []
        for start in range(0, len(words), self.chunk_size):
            chunk_words = words[start : start + self.chunk_size]
            if not chunk_words:
                continue
            piece_text = " ".join(chunk_words).strip()
            pieces.append(ContentBlock(text=piece_text, kind=kind, word_count=len(chunk_words), contains_table=False))
        return pieces

    def _build_overlap(self, blocks: list[ContentBlock]) -> list[ContentBlock]:
        """Carry a small overlap of the trailing blocks into the next chunk."""

        if self.chunk_overlap <= 0 or not blocks:
            return []

        overlap: list[ContentBlock] = []
        total_words = 0
        for block in reversed(blocks):
            overlap.insert(0, block)
            total_words += block.word_count
            if total_words >= self.chunk_overlap:
                break
        return overlap

    def _build_chunk(self, section: StructuredSection, chunk_number: int, blocks: list[ContentBlock]) -> ChunkRecord:
        """Build a chunk record for a section."""

        text = "\n\n".join(block.text for block in blocks if block.text.strip()).strip()
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
            section_index=section.section_index,
            chunk_number=chunk_number,
            contains_table=any(block.contains_table for block in blocks) or self._contains_table_marker(text),
            heading_path=section.heading_path or build_heading_path(section.chapter, section.section, section.subsection),
        )

    def _section_slug(self, section: StructuredSection) -> str:
        """Build a stable slug for chunk IDs."""

        heading_path = section.heading_path or build_heading_path(section.chapter, section.section, section.subsection)
        return slugify(f"{section.source_file}_{heading_path}")

    def _classify_block(self, block: str) -> str:
        """Classify a chunking block for better preservation."""

        upper = block.upper()
        if self._contains_table_marker(block):
            return "table"
        if any(marker in upper for marker in TABLE_BEGIN_MARKERS | TABLE_END_MARKERS):
            return "table"
        if self._looks_like_list(block):
            return "list"
        if self._looks_like_heading(block):
            return "heading"
        return "paragraph"

    def _looks_like_list(self, block: str) -> bool:
        """Detect bullet or numbered list blocks."""

        lines = [line.strip() for line in block.splitlines() if line.strip()]
        if not lines:
            return False
        return all(re.match(r"^(?:[-*•‣▪◦]|\d+[.)]|\(?[A-Za-z]\)|[IVXLCDM]+[.)])\s+", line) for line in lines)

    def _looks_like_heading(self, block: str) -> bool:
        """Detect heading-like blocks."""

        lines = [line.strip() for line in block.splitlines() if line.strip()]
        if len(lines) != 1:
            return False
        line = lines[0]
        if len(line) > 90 or line.endswith((".", ":", ";", ",")):
            return False
        words = line.split()
        if not words or len(words) > 10:
            return False
        uppercase_ratio = sum(1 for word in words if word.isupper()) / len(words)
        title_case_ratio = sum(1 for word in words if word[:1].isupper() and word[1:].islower()) / len(words)
        return uppercase_ratio >= 0.75 or title_case_ratio >= 0.75

    def _contains_table_marker(self, text: str) -> bool:
        """Return True when a block contains explicit table markers."""

        upper = text.upper()
        return any(marker in upper for marker in TABLE_BEGIN_MARKERS | TABLE_END_MARKERS)

    def _word_count(self, text: str) -> int:
        """Count words for chunk sizing."""

        return len([word for word in text.split() if word])
