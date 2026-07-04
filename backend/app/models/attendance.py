"""Attendance ORM model."""

from __future__ import annotations

from sqlalchemy import Float, ForeignKey, String, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import Base


class Attendance(Base):
    """Student attendance record for a course."""

    __tablename__ = "attendance"
    __table_args__ = (
        UniqueConstraint("student_id", "course_id", name="uq_attendance_student_course"),
    )

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    student_id: Mapped[str] = mapped_column(
        String(20),
        ForeignKey("students.student_id"),
        nullable=False,
        index=True,
    )
    course_id: Mapped[int] = mapped_column(ForeignKey("courses.id"), nullable=False, index=True)
    attendance_percentage: Mapped[float] = mapped_column(Float, nullable=False)

