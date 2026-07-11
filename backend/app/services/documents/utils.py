"""Utility helpers for document processing."""

from __future__ import annotations

import re
from pathlib import Path


SUPPORTED_EXTENSIONS = {".pdf", ".docx", ".txt", ".md"}


def slugify(value: str) -> str:
    """Convert a string into a stable file-safe slug."""

    value = value.lower()
    value = re.sub(r"[^a-z0-9]+", "_", value)
    value = re.sub(r"_+", "_", value).strip("_")
    return value or "document"


def infer_document_type(path: Path) -> str:
    """Map file suffixes to simple document type labels."""

    return path.suffix.lower().lstrip(".")


def is_supported_document(path: Path) -> bool:
    """Return True if the path has a supported document extension."""

    return path.suffix.lower() in SUPPORTED_EXTENSIONS


def normalize_text(text: str) -> str:
    """Normalize extracted text for downstream processing."""

    text = text.replace("\r\n", "\n").replace("\r", "\n")
    text = text.replace("\x0c", "\n")
    lines = [re.sub(r"[ \t]+", " ", line).strip() for line in text.split("\n")]

    normalized_lines: list[str] = []
    previous_blank = False
    for line in lines:
        if not line:
            if normalized_lines and not previous_blank:
                normalized_lines.append("")
            previous_blank = True
            continue
        normalized_lines.append(line)
        previous_blank = False

    while normalized_lines and normalized_lines[0] == "":
        normalized_lines.pop(0)
    while normalized_lines and normalized_lines[-1] == "":
        normalized_lines.pop()

    return "\n".join(normalized_lines).strip()


def strip_heading_noise(line: str) -> str:
    """Remove extra punctuation and whitespace from a heading line."""

    return re.sub(r"\s+", " ", line).strip(" :.-")
