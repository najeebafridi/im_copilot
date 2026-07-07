"""Automatic conversation title generation."""

from __future__ import annotations

FILLER_WORDS = {
    "a",
    "an",
    "and",
    "are",
    "can",
    "could",
    "do",
    "for",
    "give",
    "how",
    "i",
    "is",
    "me",
    "my",
    "of",
    "please",
    "show",
    "tell",
    "the",
    "to",
    "what",
    "when",
    "where",
    "which",
    "with",
    "would",
    "you",
}


def generate_title(message: str, max_length: int) -> str:
    """Generate a short title from the first user message."""

    words = [
        word.strip(".,!?;:()[]{}\"'").lower()
        for word in message.split()
        if word.strip(".,!?;:()[]{}\"'").lower() not in FILLER_WORDS
    ]
    if not words:
        return "New Conversation"

    title = " ".join(word.capitalize() for word in words[:6])
    if len(title) > max_length:
        title = title[:max_length].rstrip()
    return title or "New Conversation"
