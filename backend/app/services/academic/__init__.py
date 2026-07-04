"""Academic query services for secure student data access."""

from app.services.academic.intent_matcher import AcademicIntent, AcademicIntentMatch, AcademicIntentMatcher
from app.services.academic.prompt_builder import AcademicPromptBuilder
from app.services.academic.service import AcademicQueryResult, AcademicQueryService, get_academic_query_service

__all__ = [
    "AcademicIntent",
    "AcademicIntentMatch",
    "AcademicIntentMatcher",
    "AcademicPromptBuilder",
    "AcademicQueryResult",
    "AcademicQueryService",
    "get_academic_query_service",
]
