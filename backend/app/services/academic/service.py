"""Secure academic data retrieval and explanation service."""

from __future__ import annotations

import logging
import time
from dataclasses import dataclass
from typing import Any

from fastapi import Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.models.attendance import Attendance
from app.models.course import Course
from app.models.enrollment import Enrollment
from app.models.student import Student
from app.models.timetable import Timetable
from app.models.user import User
from app.schemas.copilot import CopilotChatResponse, CopilotMetadata, CopilotSource
from app.services.academic.intent_matcher import AcademicIntent, AcademicIntentMatch, AcademicIntentMatcher
from app.services.academic.prompt_builder import AcademicPromptBuilder
from app.services.copilot.answer_validator import AnswerValidator
from app.services.copilot.query_preprocessor import QueryPreprocessor
from app.services.llm.exceptions import LLMConfigurationError, LLMProviderError, LLMResponseValidationError
from app.services.llm.llm_service import LLMService, get_llm_service

logger = logging.getLogger(__name__)


@dataclass(slots=True)
class AcademicQueryResult:
    """Structured data returned by a safe academic query."""

    intent: AcademicIntent
    data: dict[str, Any]
    sources: list[CopilotSource]
    handler_name: str


@dataclass(slots=True)
class AcademicQueryService:
    """Answer academic questions using safe, parameterized SQL queries."""

    db: Session
    llm_service: LLMService
    preprocessor: QueryPreprocessor
    intent_matcher: AcademicIntentMatcher
    prompt_builder: AcademicPromptBuilder
    validator: AnswerValidator

    @classmethod
    def from_dependencies(cls, db: Session, llm_service: LLMService) -> "AcademicQueryService":
        """Build the service from request-scoped dependencies."""

        return cls(
            db=db,
            llm_service=llm_service,
            preprocessor=QueryPreprocessor(),
            intent_matcher=AcademicIntentMatcher(),
            prompt_builder=AcademicPromptBuilder(),
            validator=AnswerValidator(),
        )

    def answer(self, message: str, current_user: User, conversation_id: str | None = None) -> CopilotChatResponse:
        """Return a grounded explanation for an authenticated student."""

        if current_user.role != "student":
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Student access is required")

        logger.info("Academic question received student_id=%s", current_user.student_id)
        print(f"[ACADEMIC] question received student_id={current_user.student_id}")

        total_start = time.perf_counter()
        query = self.preprocessor.preprocess(message)
        match = self.intent_matcher.match(query)
        logger.info("Academic intent detected student_id=%s intent=%s", current_user.student_id, match.intent)
        print(f"[ACADEMIC] intent={match.intent} student_id={current_user.student_id}")

        if match.intent == AcademicIntent.UNSUPPORTED:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Unsupported academic question.",
            )

        db_start = time.perf_counter()
        try:
            result = self._execute_intent(match, current_user)
        except SQLAlchemyError as exc:
            logger.exception("Academic database error student_id=%s intent=%s", current_user.student_id, match.intent)
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Database query failed.") from exc
        db_latency_ms = int((time.perf_counter() - db_start) * 1000)
        logger.info(
            "Academic handler executed student_id=%s handler=%s db_latency_ms=%s",
            current_user.student_id,
            result.handler_name,
            db_latency_ms,
        )
        print(
            f"[ACADEMIC] handler={result.handler_name} student_id={current_user.student_id} db_latency_ms={db_latency_ms}"
        )

        prompt = self.prompt_builder.build(question=message, data=result.data)

        try:
            generation = self.llm_service.generate_with_metadata(message=message, system_prompt=prompt)
        except (LLMConfigurationError, LLMProviderError):
            raise

        logger.info(
            "Academic llm latency_ms=%s provider=%s model=%s",
            generation.latency_ms,
            generation.response.provider,
            generation.response.model,
        )
        print(
            f"[ACADEMIC] llm latency_ms={generation.latency_ms} provider={generation.response.provider} model={generation.response.model}"
        )

        try:
            answer = self.validator.validate(generation.response.response)
        except LLMResponseValidationError as exc:
            raise HTTPException(status_code=status.HTTP_502_BAD_GATEWAY, detail=str(exc)) from exc

        total_latency_ms = int((time.perf_counter() - total_start) * 1000)
        logger.info(
            "Academic total latency_ms=%s student_id=%s intent=%s",
            total_latency_ms,
            current_user.student_id,
            match.intent,
        )
        print(
            f"[ACADEMIC] total latency_ms={total_latency_ms} student_id={current_user.student_id} intent={match.intent}"
        )

        return CopilotChatResponse(
            answer=answer,
            sources=result.sources,
            metadata=CopilotMetadata(
                provider=generation.response.provider,
                model=generation.response.model,
                cached=generation.cached,
                latency_ms=total_latency_ms,
                retrieved_chunks=self._count_retrieved_items(result.data),
            ),
        )

    def _execute_intent(self, match: AcademicIntentMatch, current_user: User) -> AcademicQueryResult:
        """Execute a safe handler for the detected intent."""

        handlers = {
            AcademicIntent.PROFILE: self._handle_profile,
            AcademicIntent.ATTENDANCE_SUMMARY: self._handle_attendance_summary,
            AcademicIntent.ATTENDANCE_COURSE: self._handle_attendance_course,
            AcademicIntent.ATTENDANCE_HIGHEST: self._handle_highest_attendance,
            AcademicIntent.ATTENDANCE_LOWEST: self._handle_lowest_attendance,
            AcademicIntent.ENROLLED_COURSES: self._handle_enrolled_courses,
            AcademicIntent.GRADES: self._handle_grades,
            AcademicIntent.TIMETABLE: self._handle_timetable,
        }
        handler = handlers.get(match.intent)
        if handler is None:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Unsupported academic question.")
        return handler(current_user, match.course_reference)

    def _handle_profile(self, current_user: User, _: str | None) -> AcademicQueryResult:
        """Return the authenticated student's profile data."""

        student = self.db.execute(
            select(Student).where(Student.student_id == current_user.student_id)
        ).scalar_one_or_none()
        if student is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Student profile not found.")

        data = {
            "student_id": current_user.student_id,
            "name": current_user.name,
            "program": student.program,
            "semester": student.semester,
            "cgpa": student.cgpa,
        }
        return self._result(
            intent=AcademicIntent.PROFILE,
            handler_name="profile",
            data=data,
            sources=[
                CopilotSource(type="database", table="users", document="users"),
                CopilotSource(type="database", table="students", document="students"),
            ],
        )

    def _handle_attendance_summary(self, current_user: User, _: str | None) -> AcademicQueryResult:
        """Return the authenticated student's attendance summary."""

        rows = self._attendance_rows(current_user.student_id)
        if not rows:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Attendance records not found.")

        attendance_values = [row[0].attendance_percentage for row in rows]
        average = round(sum(attendance_values) / len(attendance_values), 2)
        data = {
            "student_id": current_user.student_id,
            "average_attendance": average,
            "records": [self._attendance_row_to_dict(row) for row in rows],
        }
        return self._result(
            intent=AcademicIntent.ATTENDANCE_SUMMARY,
            handler_name="attendance_summary",
            data=data,
            sources=[self._database_source("attendance"), self._database_source("courses")],
        )

    def _handle_attendance_course(self, current_user: User, course_reference: str | None) -> AcademicQueryResult:
        """Return attendance for one specific course."""

        if not course_reference:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Please mention the course code or course name.",
            )

        course = self._resolve_course(course_reference)
        row = self.db.execute(
            select(Attendance, Course.course_code, Course.course_name)
            .join(Course, Course.id == Attendance.course_id)
            .where(Attendance.student_id == current_user.student_id)
            .where(Attendance.course_id == course.id)
        ).first()
        if row is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Attendance record not found for that course.")

        attendance, course_code, course_name = row
        data = {
            "student_id": current_user.student_id,
            "course": {
                "course_code": course_code,
                "course_name": course_name,
            },
            "attendance_percentage": attendance.attendance_percentage,
        }
        return self._result(
            intent=AcademicIntent.ATTENDANCE_COURSE,
            handler_name="attendance_course",
            data=data,
            sources=[self._database_source("attendance"), self._database_source("courses")],
        )

    def _handle_highest_attendance(self, current_user: User, _: str | None) -> AcademicQueryResult:
        """Return the highest attendance record for the student."""

        row = self._attendance_extreme(current_user.student_id, descending=True)
        if row is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Attendance records not found.")
        return self._attendance_extreme_result(row, current_user.student_id, "highest_attendance")

    def _handle_lowest_attendance(self, current_user: User, _: str | None) -> AcademicQueryResult:
        """Return the lowest attendance record for the student."""

        row = self._attendance_extreme(current_user.student_id, descending=False)
        if row is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Attendance records not found.")
        return self._attendance_extreme_result(row, current_user.student_id, "lowest_attendance")

    def _handle_enrolled_courses(self, current_user: User, _: str | None) -> AcademicQueryResult:
        """Return the student's enrolled courses."""

        rows = self.db.execute(
            select(Course.course_code, Course.course_name, Course.credit_hours)
            .join(Enrollment, Enrollment.course_id == Course.id)
            .where(Enrollment.student_id == current_user.student_id)
            .order_by(Course.course_code)
        ).all()
        if not rows:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="No enrolled courses found.")

        data = {
            "student_id": current_user.student_id,
            "courses": [
                {
                    "course_code": row.course_code,
                    "course_name": row.course_name,
                    "credit_hours": row.credit_hours,
                }
                for row in rows
            ],
        }
        return self._result(
            intent=AcademicIntent.ENROLLED_COURSES,
            handler_name="enrolled_courses",
            data=data,
            sources=[self._database_source("enrollments"), self._database_source("courses")],
        )

    def _handle_grades(self, current_user: User, _: str | None) -> AcademicQueryResult:
        """Return the student's enrolled courses and grades."""

        rows = self.db.execute(
            select(Course.course_code, Course.course_name, Course.credit_hours, Enrollment.grade)
            .join(Enrollment, Enrollment.course_id == Course.id)
            .where(Enrollment.student_id == current_user.student_id)
            .order_by(Course.course_code)
        ).all()
        if not rows:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="No grade records found.")

        data = {
            "student_id": current_user.student_id,
            "grades": [
                {
                    "course_code": row.course_code,
                    "course_name": row.course_name,
                    "credit_hours": row.credit_hours,
                    "grade": row.grade,
                }
                for row in rows
            ],
        }
        return self._result(
            intent=AcademicIntent.GRADES,
            handler_name="grades",
            data=data,
            sources=[self._database_source("enrollments"), self._database_source("courses")],
        )

    def _handle_timetable(self, current_user: User, _: str | None) -> AcademicQueryResult:
        """Return the student's timetable entries."""

        rows = self.db.execute(
            select(Timetable.course_name, Timetable.day, Timetable.time, Timetable.room)
            .where(Timetable.student_id == current_user.student_id)
            .order_by(Timetable.day, Timetable.time)
        ).all()
        if not rows:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Timetable records not found.")

        data = {
            "student_id": current_user.student_id,
            "timetable": [
                {
                    "course_name": row.course_name,
                    "day": row.day,
                    "time": row.time,
                    "room": row.room,
                }
                for row in rows
            ],
        }
        return self._result(
            intent=AcademicIntent.TIMETABLE,
            handler_name="timetable",
            data=data,
            sources=[self._database_source("timetable")],
        )

    def _attendance_rows(self, student_id: str):
        """Return attendance rows joined with course data."""

        return self.db.execute(
            select(Attendance, Course.course_code, Course.course_name)
            .join(Course, Course.id == Attendance.course_id)
            .where(Attendance.student_id == student_id)
            .order_by(Course.course_code)
        ).all()

    def _attendance_row_to_dict(self, row: Any) -> dict[str, Any]:
        """Normalize an attendance row for prompt construction."""

        attendance, course_code, course_name = row
        return {
            "course_code": course_code,
            "course_name": course_name,
            "attendance_percentage": attendance.attendance_percentage,
        }

    def _attendance_extreme(self, student_id: str, descending: bool):
        """Return the highest or lowest attendance row."""

        order_column = Attendance.attendance_percentage.desc() if descending else Attendance.attendance_percentage.asc()
        return self.db.execute(
            select(Attendance, Course.course_code, Course.course_name)
            .join(Course, Course.id == Attendance.course_id)
            .where(Attendance.student_id == student_id)
            .order_by(order_column)
            .limit(1)
        ).first()

    def _attendance_extreme_result(self, row: Any, student_id: str, handler_name: str) -> AcademicQueryResult:
        """Convert an attendance extreme row into the common result shape."""

        attendance, course_code, course_name = row
        data = {
            "student_id": student_id,
            "course": {
                "course_code": course_code,
                "course_name": course_name,
            },
            "attendance_percentage": attendance.attendance_percentage,
        }
        return self._result(
            intent=AcademicIntent.ATTENDANCE_HIGHEST if handler_name == "highest_attendance" else AcademicIntent.ATTENDANCE_LOWEST,
            handler_name=handler_name,
            data=data,
            sources=[self._database_source("attendance"), self._database_source("courses")],
        )

    def _resolve_course(self, reference: str) -> Course:
        """Find a course by code or name using a parameterized query."""

        normalized = reference.strip()
        course = self.db.execute(
            select(Course).where(Course.course_code.ilike(normalized))
        ).scalar_one_or_none()
        if course is None:
            course = self.db.execute(
                select(Course).where(Course.course_name.ilike(f"%{normalized}%"))
            ).scalar_one_or_none()
        if course is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Course not found.")
        return course

    def _database_source(self, table: str) -> CopilotSource:
        """Create a database source descriptor."""

        return CopilotSource(type="database", table=table, document=table)

    def _result(
        self,
        intent: AcademicIntent,
        handler_name: str,
        data: dict[str, Any],
        sources: list[CopilotSource],
    ) -> AcademicQueryResult:
        """Create a standardized query result object."""

        return AcademicQueryResult(intent=intent, data=data, sources=sources, handler_name=handler_name)

    def _count_retrieved_items(self, data: dict[str, Any]) -> int:
        """Count the main structured records returned to the prompt."""

        for key in ("records", "courses", "grades", "timetable"):
            value = data.get(key)
            if isinstance(value, list):
                return len(value)
        return 1


def get_academic_query_service(
    db: Session = Depends(get_db),
    llm_service: LLMService = Depends(get_llm_service),
) -> AcademicQueryService:
    """FastAPI dependency for academic question answering."""

    return AcademicQueryService.from_dependencies(db=db, llm_service=llm_service)
