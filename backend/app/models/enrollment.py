"""Enrollment ORM model."""

from __future__ import annotations

from sqlalchemy import ForeignKey, String, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import Base


class Enrollment(Base):
    """Student course enrollment."""

    __tablename__ = "enrollments"
    __table_args__ = (
        UniqueConstraint("student_id", "course_id", name="uq_enrollment_student_course"),
    )

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    student_id: Mapped[str] = mapped_column(
        String(20),
        ForeignKey("students.student_id"),
        nullable=False,
        index=True,
    )
    course_id: Mapped[int] = mapped_column(ForeignKey("courses.id"), nullable=False, index=True)
    grade: Mapped[str] = mapped_column(String(5), nullable=False)

