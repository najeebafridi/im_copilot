"""Text cleaning utilities."""

from __future__ import annotations

import re


TABLE_BEGIN_MARKERS = {"[TABLE BEGIN]", "<<TABLE BEGIN>>", "TABLE BEGIN"}
TABLE_END_MARKERS = {"[TABLE END]", "<<TABLE END>>", "TABLE END"}

_PAGE_NUMBER_RE = re.compile(r"^(?:page\s*)?\d+(?:\s*[/\-]\s*\d+)?$", re.IGNORECASE)
_DECORATED_PAGE_NUMBER_RE = re.compile(r"^-+\s*\d+\s*-+$")
_BULLET_RE = re.compile(r"^(?:[-*•‣▪◦]|\d+[.)]|\(?[A-Za-z]\)|[A-Za-z][.)]|[IVXLCDM]+[.)])\s+")
_HEADING_HINT_RE = re.compile(
    r"^(?:CHAPTER|SECTION)\s+[IVXLCDM\d]+(?:\b.*)?$|^\d+(?:\.\d+){0,4}(?:\b.*)?$|^\(?[A-Za-z]\)?[.)]\s+.*$",
    re.IGNORECASE,
)
_LOWERCASE_CONTINUATION_RE = re.compile(r"^[a-z(]")


def clean_page_text(text: str) -> str:
    """Clean raw page text before structure detection."""

    if not text:
        return ""

    normalized = text.replace("\r\n", "\n").replace("\r", "\n").replace("\x0c", "\n")
    cleaned_lines: list[str] = []
    pending: str | None = None
    in_table = False

    for raw_line in normalized.split("\n"):
        line = _normalize_line(raw_line)
        if not line:
            if in_table:
                continue
            if pending is not None:
                cleaned_lines.append(pending)
                pending = None
            if cleaned_lines and cleaned_lines[-1] != "":
                cleaned_lines.append("")
            continue

        if _is_page_artifact(line):
            continue

        if _is_table_begin(line):
            if pending is not None:
                cleaned_lines.append(pending)
                pending = None
            if cleaned_lines and cleaned_lines[-1] != "":
                cleaned_lines.append("")
            cleaned_lines.append(_normalize_table_marker(line))
            in_table = True
            continue

        if _is_table_end(line):
            if pending is not None:
                cleaned_lines.append(pending)
                pending = None
            cleaned_lines.append(_normalize_table_marker(line))
            cleaned_lines.append("")
            in_table = False
            continue

        if in_table:
            cleaned_lines.append(line)
            continue

        if pending is None:
            pending = line
            continue

        if _should_merge(pending, line):
            pending = _merge_lines(pending, line)
        else:
            cleaned_lines.append(pending)
            pending = line

    if pending is not None:
        cleaned_lines.append(pending)

    return _collapse_blank_lines(cleaned_lines)


def _normalize_line(line: str) -> str:
    """Strip duplicate whitespace without flattening useful structure."""

    return re.sub(r"[ \t]+", " ", line).strip()


def _collapse_blank_lines(lines: list[str]) -> str:
    """Collapse repeated blank separators while preserving paragraph breaks."""

    output: list[str] = []
    previous_blank = False
    for line in lines:
        if not line:
            if output and not previous_blank:
                output.append("")
            previous_blank = True
            continue
        output.append(line)
        previous_blank = False

    while output and output[-1] == "":
        output.pop()
    while output and output[0] == "":
        output.pop(0)

    return "\n".join(output).strip()


def _is_page_artifact(line: str) -> bool:
    """Return True for common page numbers and footer-only artifacts."""

    if _PAGE_NUMBER_RE.match(line) or _DECORATED_PAGE_NUMBER_RE.match(line):
        return True
    return False


def _is_table_begin(line: str) -> bool:
    """Detect a lightweight table start marker."""

    return line.upper() in TABLE_BEGIN_MARKERS


def _is_table_end(line: str) -> bool:
    """Detect a lightweight table end marker."""

    return line.upper() in TABLE_END_MARKERS


def _normalize_table_marker(line: str) -> str:
    """Normalize table boundary markers to a stable representation."""

    upper = line.upper()
    if _is_table_begin(upper):
        return "[TABLE BEGIN]"
    if _is_table_end(upper):
        return "[TABLE END]"
    return line


def _looks_like_heading(line: str) -> bool:
    """Heuristically decide whether a line is a heading."""

    if _HEADING_HINT_RE.match(line):
        return True

    words = line.split()
    if len(words) > 10 or len(line) > 90:
        return False
    if line.endswith((".", ":", ";", ",")):
        return False

    alpha_words = [word for word in words if word.strip("()[]{}.,:;-")]
    if not alpha_words:
        return False

    uppercase_ratio = sum(1 for word in alpha_words if word.isupper()) / len(alpha_words)
    title_case_ratio = sum(1 for word in alpha_words if word[:1].isupper() and word[1:].islower()) / len(alpha_words)
    policy_terms = {"policy", "regulations", "rules", "attendance", "definitions", "responsibilities", "scope"}

    if uppercase_ratio >= 0.75:
        return True
    if title_case_ratio >= 0.75 and len(words) <= 8:
        return True
    if any(term in line.lower() for term in policy_terms) and len(words) <= 8:
        return True
    return False


def _should_merge(previous: str, current: str) -> bool:
    """Decide whether the current line is a wrapped continuation."""

    if _is_bullet(previous) or _is_bullet(current):
        return False
    if _looks_like_heading(previous) or _looks_like_heading(current):
        return False
    if previous.endswith("-") and _LOWERCASE_CONTINUATION_RE.match(current):
        return True
    if previous.endswith((":", "/", "(", "[", "—", "–")):
        return True
    if current.startswith(("-", "*", "•")):
        return False
    if _LOWERCASE_CONTINUATION_RE.match(current) and not previous.endswith((".", "!", "?", ":", ";")):
        return True
    return False


def _is_bullet(line: str) -> bool:
    """Return True for bullet or list-item lines."""

    return bool(_BULLET_RE.match(line))


def _merge_lines(previous: str, current: str) -> str:
    """Join a wrapped line with its predecessor."""

    if previous.endswith("-") and _LOWERCASE_CONTINUATION_RE.match(current):
        return previous[:-1] + current
    return f"{previous} {current}".strip()
