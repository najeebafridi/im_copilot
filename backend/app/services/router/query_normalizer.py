"""Offline query normalization and typo correction for router preprocessing."""

from __future__ import annotations

import logging
import re
from functools import lru_cache

from rapidfuzz import fuzz, process

from app.core.config import get_settings

logger = logging.getLogger(__name__)

COMMON_MISSPELLINGS: dict[str, str] = {
    "gpaa": "gpa",
    "cgpaa": "cgpa",
    "attandance": "attendance",
    "attendence": "attendance",
    "hostle": "hostel",
    "semster": "semester",
    "scholership": "scholarship",
    "tranfer": "transfer",
    "credt": "credit",
    "libary": "library",
    "examintion": "examination",
    "probabtion": "probation",
    "regestration": "registration",
    "faculity": "faculty",
    "universty": "university",
    "studnt": "student",
    "wat": "what",
    "ruls": "rules",
    "percantage": "percentage",
}

ACADEMIC_VOCABULARY: tuple[str, ...] = (
    "admission",
    "attendance",
    "ba",
    "bsc",
    "cgpa",
    "cms",
    "course",
    "courses",
    "credit",
    "credit hours",
    "degree",
    "department",
    "erp",
    "evaluation",
    "examination",
    "examination hall",
    "faculty",
    "fee",
    "finance",
    "gpa",
    "grading",
    "grades",
    "handbook",
    "hostel",
    "institute",
    "library",
    "library card",
    "policy",
    "probation",
    "promotion",
    "registration",
    "result",
    "rules",
    "scholarship",
    "semester",
    "student",
    "timetable",
    "transcript",
    "transfer",
    "transport",
    "university",
    "withdrawal",
    "percentage",
    "what",
)

PROTECTED_TOKEN_PATTERNS: tuple[re.Pattern[str], ...] = (
    re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$"),
    re.compile(r"^(?:https?://|www\.)\S+$", re.IGNORECASE),
    re.compile(r"^\d+$"),
    re.compile(r"^[A-Za-z]{2,4}\d{2,5}$"),
    re.compile(r"^\d{2,4}[A-Za-z]-?\d{2,5}$"),
    re.compile(r"^[A-Za-z]{2,5}-\d{2,5}$"),
    re.compile(r"^[A-Za-z0-9]+(?:[-/][A-Za-z0-9]+)+$"),
)

WORD_TOKEN_PATTERN = re.compile(r"^([^A-Za-z0-9]*)([A-Za-z0-9][A-Za-z0-9'-]*)([^A-Za-z0-9]*)$")


def normalize_query(query: str) -> str:
    """Normalize and lightly correct a user query before routing."""

    settings = get_settings()
    original_query = query
    text = _normalize_whitespace_and_punctuation(query)
    normalized_text = _normalize_tokens(text)

    if settings.DEBUG:
        logger.info("Original Query: %s", original_query)
        logger.info("Normalized Query: %s", normalized_text)

    return normalized_text


def _normalize_whitespace_and_punctuation(query: str) -> str:
    """Normalize casing, apostrophes, spacing, and repeated punctuation."""

    text = query.lower().strip()
    text = text.replace("’", "'").replace("‘", "'").replace("`", "'")
    text = re.sub(r"([!?.,;:])\1+", r"\1", text)
    text = re.sub(r"\s+", " ", text)
    return text


def _normalize_tokens(text: str) -> str:
    """Correct tokens deterministically while preserving protected values."""

    tokens = text.split(" ")
    normalized_tokens = [_normalize_token(token) for token in tokens if token]
    return " ".join(normalized_tokens).strip()


def _normalize_token(token: str) -> str:
    """Normalize one token without touching protected identifiers."""

    if _is_protected_token(token):
        return token

    match = WORD_TOKEN_PATTERN.match(token)
    if match is None:
        return token

    prefix, core, suffix = match.groups()
    replacement = _correct_core(core)
    return f"{prefix}{replacement}{suffix}"


def _is_protected_token(token: str) -> bool:
    """Return True for identifiers that must never be spell-corrected."""

    return any(pattern.match(token) for pattern in PROTECTED_TOKEN_PATTERNS)


@lru_cache(maxsize=1)
def _vocabulary_choices() -> tuple[str, ...]:
    """Return the reusable RapidFuzz lookup vocabulary."""

    return ACADEMIC_VOCABULARY


def _correct_core(core: str) -> str:
    """Correct a core word token if it is a known typo or a high-confidence match."""

    if not core or any(character.isdigit() for character in core):
        return core

    if core in COMMON_MISSPELLINGS:
        return COMMON_MISSPELLINGS[core]

    if core in _vocabulary_choices():
        return core

    if len(core) < 4:
        return core

    match = process.extractOne(core, _vocabulary_choices(), scorer=fuzz.ratio, score_cutoff=90)
    if match is None:
        return core

    replacement, _, _ = match
    return replacement if replacement in _vocabulary_choices() else core
