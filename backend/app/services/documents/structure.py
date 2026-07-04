"""Pattern-based structure detection for document text."""

from __future__ import annotations

from dataclasses import dataclass
import re

from app.services.documents.cleaning import clean_page_text
from app.services.documents.types import ExtractedPage, StructuredSection


@dataclass(slots=True)
class SectionState:
    """Current heading state while scanning pages."""

    chapter: str = ""
    section: str = ""
    subsection: str = ""


class StructureDetector:
    """Detect chapters, sections, and subsections using patterns."""

    chapter_pattern = re.compile(r"^(CHAPTER\s+\d+|SECTION\s+\d+)$", re.IGNORECASE)
    numbered_pattern = re.compile(r"^(\d+(?:\.\d+){1,2})\b(?:\s+.*)?$")

    def detect(self, pages: list[ExtractedPage], source_file: str, document_type: str) -> list[StructuredSection]:
        """Turn extracted pages into logical sections."""

        sections: list[StructuredSection] = []
        state = SectionState()
        buffer: list[str] = []
        current_start_page = pages[0].page if pages else 1
        section_index = 0

        def flush(end_page: int) -> None:
            nonlocal buffer, section_index, current_start_page
            content = clean_page_text("\n".join(buffer))
            if content:
                section_index += 1
                sections.append(
                    StructuredSection(
                        source_file=source_file,
                        document_type=document_type,
                        section_index=section_index,
                        chapter=state.chapter,
                        section=state.section,
                        subsection=state.subsection,
                        content=content,
                        page_start=current_start_page,
                        page_end=end_page,
                    )
                )
            buffer = []

        for page in pages:
            lines = page.text.split("\n")
            for raw_line in lines:
                line = raw_line.strip()
                if not line:
                    continue
                heading = self._match_heading(line)
                if heading is not None:
                    flush(page.page)
                    state = self._update_state(state, heading)
                    current_start_page = page.page
                    continue
                buffer.append(line)

        if buffer:
            flush(pages[-1].page)

        return sections

    def _match_heading(self, line: str) -> dict[str, str] | None:
        """Recognize heading-like lines."""

        normalized = line.upper().strip()
        if self.chapter_pattern.match(normalized):
            return {"kind": "chapter", "value": normalized}

        numbered = self.numbered_pattern.match(line)
        if numbered:
            value = numbered.group(1)
            if value.count(".") == 1:
                return {"kind": "section", "value": value}
            return {"kind": "subsection", "value": value}

        return None

    def _update_state(self, state: SectionState, heading: dict[str, str]) -> SectionState:
        """Update the active heading hierarchy."""

        kind = heading["kind"]
        value = heading["value"]
        if kind == "chapter":
            return SectionState(chapter=value, section="", subsection="")
        if kind == "section":
            section = value
            return SectionState(chapter=state.chapter, section=section, subsection="")
        return SectionState(
            chapter=state.chapter,
            section=".".join(value.split(".")[:2]),
            subsection=value,
        )

