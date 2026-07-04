"""Normalize user questions before retrieval."""

from __future__ import annotations

import re


class QueryPreprocessor:
    """Apply lightweight, non-AI query cleanup."""

    def preprocess(self, message: str) -> str:
        """Normalize whitespace and trim the query."""

        cleaned = message.strip()
        cleaned = re.sub(r"\s+", " ", cleaned)
        return cleaned.lower()
