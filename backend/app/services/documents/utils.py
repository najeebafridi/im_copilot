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
    normalized_lines = [line for line in lines if line]
    return "\n".join(normalized_lines).strip()


def strip_heading_noise(line: str) -> str:
    """Remove extra punctuation and whitespace from a heading line."""

    return re.sub(r"\s+", " ", line).strip(" :.-")

