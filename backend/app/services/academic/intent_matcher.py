"""Lightweight keyword-based intent detection for academic questions."""

from __future__ import annotations

import re
from dataclasses import dataclass
from enum import StrEnum


class AcademicIntent(StrEnum):
    """Supported academic query intents."""

    PROFILE = "profile"
    ATTENDANCE_SUMMARY = "attendance_summary"
    ATTENDANCE_COURSE = "attendance_course"
    ATTENDANCE_HIGHEST = "attendance_highest"
    ATTENDANCE_LOWEST = "attendance_lowest"
    ENROLLED_COURSES = "enrolled_courses"
    CREDIT_HOURS = "credit_hours"
    GRADES = "grades"
    TIMETABLE = "timetable"
    UNSUPPORTED = "unsupported"


@dataclass(slots=True)
class AcademicIntentMatch:
    """Intent result plus any extracted parameters."""

    intent: AcademicIntent
    course_reference: str | None = None


class AcademicIntentMatcher:
    """Map a user question to a predefined academic handler."""

    COURSE_CODE_PATTERN = re.compile(r"\b([A-Z]{2,4}\d{3})\b")

    def match(self, question: str) -> AcademicIntentMatch:
        """Detect the most likely academic intent."""

        normalized = question.lower().strip()
        normalized = re.sub(r"\s+", " ", normalized)

        if self._contains_any(normalized, ("highest attendance",)):
            return AcademicIntentMatch(intent=AcademicIntent.ATTENDANCE_HIGHEST)
        if self._contains_any(normalized, ("lowest attendance",)):
            return AcademicIntentMatch(intent=AcademicIntent.ATTENDANCE_LOWEST)
        if self._contains_any(normalized, ("timetable", "schedule")):
            return AcademicIntentMatch(intent=AcademicIntent.TIMETABLE)
        if self._contains_any(normalized, ("enrolled courses", "my courses", "registered courses")):
            return AcademicIntentMatch(intent=AcademicIntent.ENROLLED_COURSES)
        if self._contains_any(normalized, ("credit hours", "credit hour", "completed credits", "credits completed")):
            return AcademicIntentMatch(intent=AcademicIntent.CREDIT_HOURS)
        if self._contains_any(normalized, ("grades", "my grades")):
            return AcademicIntentMatch(intent=AcademicIntent.GRADES)

        if self._contains_any(normalized, ("my name", "my semester", "my program", "my cgpa", "cgpa", "my gpa", "gpa", "grade point average")):
            return AcademicIntentMatch(intent=AcademicIntent.PROFILE)

        attendance_course_reference = self._extract_course_reference(normalized)
        if self._contains_any(normalized, ("attendance in", "attendance for", "attendance of")) and attendance_course_reference:
            return AcademicIntentMatch(
                intent=AcademicIntent.ATTENDANCE_COURSE,
                course_reference=attendance_course_reference,
            )

        if self._contains_any(normalized, ("my attendance", "attendance")):
            return AcademicIntentMatch(intent=AcademicIntent.ATTENDANCE_SUMMARY)

        return AcademicIntentMatch(intent=AcademicIntent.UNSUPPORTED)

    def _contains_any(self, text: str, phrases: tuple[str, ...]) -> bool:
        """Return True if any phrase appears in the text."""

        return any(phrase in text for phrase in phrases)

    def _extract_course_reference(self, question: str) -> str | None:
        """Extract a course code or course-name hint from the question."""

        code_match = self.COURSE_CODE_PATTERN.search(question.upper())
        if code_match:
            return code_match.group(1)

        patterns = (
            r"attendance (?:in|for|of) ([a-z0-9 \-&]+)",
            r"attendance (?:in|for|of) the ([a-z0-9 \-&]+)",
        )
        for pattern in patterns:
            match = re.search(pattern, question, flags=re.IGNORECASE)
            if match:
                reference = match.group(1).strip(" ?.,")
                if reference:
                    return reference

        return None
