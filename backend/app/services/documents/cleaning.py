"""Text cleaning utilities."""

from __future__ import annotations

from app.services.documents.utils import normalize_text


def clean_page_text(text: str) -> str:
    """Clean raw page text before structure detection."""

    return normalize_text(text)

