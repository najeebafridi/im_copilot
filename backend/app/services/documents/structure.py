"""Pattern-based structure detection for document text."""

from __future__ import annotations

from dataclasses import dataclass
import re

from app.services.documents.cleaning import clean_page_text
from app.services.documents.types import ExtractedPage, StructuredSection, build_heading_path
from app.services.documents.utils import strip_heading_noise


@dataclass(slots=True)
class SectionState:
    """Current heading state while scanning pages."""

    chapter: str = ""
    section: str = ""
    subsection: str = ""


class StructureDetector:
    """Detect chapters, sections, and subsections using heuristics."""

    chapter_pattern = re.compile(r"^(?:CHAPTER|SECTION)\s+([IVXLCM]+|\d+)(?:\b.*)?$", re.IGNORECASE)
    numbered_pattern = re.compile(r"^(\d+(?:\.\d+){0,4})\b(?:\s+.*)?$")
    alpha_pattern = re.compile(r"^([A-Z])(?:[.)]|:)?(?:\s+.*)?$", re.IGNORECASE)
    roman_pattern = re.compile(r"^([IVXLCM]+)(?:[.)]|:)?(?:\s+.*)?$", re.IGNORECASE)

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
                        heading_path=build_heading_path(state.chapter, state.section, state.subsection),
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
                heading = self._match_heading(line, state)
                if heading is not None:
                    flush(page.page)
                    state = self._update_state(state, heading)
                    current_start_page = page.page
                    continue
                buffer.append(line)

        if buffer:
            flush(pages[-1].page)

        return sections

    def _match_heading(self, line: str, state: SectionState) -> dict[str, str] | None:
        """Recognize heading-like lines."""

        normalized = strip_heading_noise(line)
        if not normalized or len(normalized) > 120:
            return None

        explicit = self._match_explicit_heading(normalized, state)
        if explicit is not None:
            return explicit

        if self._looks_like_generic_heading(normalized):
            return {"kind": "generic", "value": normalized}

        return None

    def _match_explicit_heading(self, line: str, state: SectionState) -> dict[str, str] | None:
        """Match numbered or labeled headings."""

        chapter_match = self.chapter_pattern.match(line)
        if chapter_match:
            prefix = line.upper().split()[0]
            value = self._normalize_heading_text(line)
            if prefix == "CHAPTER":
                return {"kind": "chapter", "value": value}
            if prefix == "SECTION":
                if not state.chapter:
                    return {"kind": "chapter", "value": value}
                return {"kind": "section", "value": value}

        numbered_match = self.numbered_pattern.match(line)
        if numbered_match:
            value = numbered_match.group(1)
            if value.count(".") == 0:
                if not state.chapter:
                    return {"kind": "chapter", "value": self._normalize_heading_text(line)}
                if not state.section:
                    return {"kind": "section", "value": self._normalize_heading_text(line)}
                return {"kind": "subsection", "value": self._normalize_heading_text(line)}
            if value.count(".") == 1:
                return {"kind": "section", "value": self._normalize_heading_text(line)}
            return {"kind": "subsection", "value": self._normalize_heading_text(line)}

        alpha_match = self.alpha_pattern.match(line)
        if alpha_match and len(line.split()) <= 6:
            value = self._normalize_heading_text(line)
            if not state.chapter:
                return {"kind": "chapter", "value": value}
            if not state.section:
                return {"kind": "section", "value": value}
            return {"kind": "subsection", "value": value}

        roman_match = self.roman_pattern.match(line)
        if roman_match and len(line.split()) <= 6:
            value = self._normalize_heading_text(line)
            if not state.chapter:
                return {"kind": "chapter", "value": value}
            if not state.section:
                return {"kind": "section", "value": value}
            return {"kind": "subsection", "value": value}

        return None

    def _looks_like_generic_heading(self, line: str) -> bool:
        """Recognize policy-style title case and all-caps headings."""

        words = line.split()
        if not words or len(words) > 10 or len(line) > 90:
            return False
        if line.endswith((".", ":", ";", ",")):
            return False

        uppercase_ratio = sum(1 for word in words if word.isupper()) / len(words)
        title_case_ratio = sum(1 for word in words if word[:1].isupper() and word[1:].islower()) / len(words)
        policy_terms = {"policy", "policies", "regulations", "rules", "attendance", "definitions", "responsibilities", "scope"}
        if uppercase_ratio >= 0.75:
            return True
        if title_case_ratio >= 0.75:
            return True
        if any(term in line.lower() for term in policy_terms) and len(words) <= 8:
            return True
        return False

    def _update_state(self, state: SectionState, heading: dict[str, str]) -> SectionState:
        """Update the active heading hierarchy."""

        kind = heading["kind"]
        value = heading["value"]
        if kind == "chapter":
            return SectionState(chapter=value, section="", subsection="")
        if kind == "section":
            if not state.chapter:
                return SectionState(chapter=value, section="", subsection="")
            return SectionState(chapter=state.chapter, section=value, subsection="")
        if kind == "subsection":
            if not state.chapter:
                return SectionState(chapter=value, section="", subsection="")
            if not state.section:
                return SectionState(chapter=state.chapter, section=value, subsection="")
            if re.match(r"^\d+(?:\.\d+){2,}$", value):
                return SectionState(
                    chapter=state.chapter,
                    section=".".join(value.split(".")[:2]),
                    subsection=value,
                )
            return SectionState(chapter=state.chapter, section=state.section, subsection=value)

        if not state.chapter:
            return SectionState(chapter=value, section="", subsection="")
        if not state.section:
            return SectionState(chapter=state.chapter, section=value, subsection="")
        return SectionState(chapter=state.chapter, section=state.section, subsection=value)

    def _normalize_heading_text(self, line: str) -> str:
        """Normalize a heading without destroying capitalization."""

        return re.sub(r"\s+", " ", line).strip(" :.-")
