"""Keyword-based conversation type classifier."""

from __future__ import annotations

from app.services.conversation.models import ConversationType

ACADEMIC_KEYWORDS = {
    "cgpa",
    "grade",
    "grades",
    "attendance",
    "timetable",
    "course",
    "semester",
    "marks",
    "result",
    "subject",
    "academic",
}

POLICY_KEYWORDS = {
    "policy",
    "rule",
    "rules",
    "handbook",
    "regulation",
    "regulations",
    "attendance policy",
    "code of conduct",
}

ADMIN_KEYWORDS = {
    "admin",
    "administration",
    "administrator",
    "manage",
    "management",
    "upload",
    "report",
    "reports",
    "settings",
    "approval",
}


def classify_conversation_type(message: str) -> ConversationType:
    """Return a lightweight keyword-based conversation type."""

    normalized = message.lower()

    if any(keyword in normalized for keyword in ADMIN_KEYWORDS):
        return ConversationType.ADMIN
    if any(keyword in normalized for keyword in POLICY_KEYWORDS):
        return ConversationType.POLICY
    if any(keyword in normalized for keyword in ACADEMIC_KEYWORDS):
        return ConversationType.ACADEMIC
    return ConversationType.GENERAL
