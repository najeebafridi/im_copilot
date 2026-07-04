"""Timetable ORM model."""

from __future__ import annotations

from sqlalchemy import ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import Base


class Timetable(Base):
    """Timetable entry for a student."""

    __tablename__ = "timetable"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    student_id: Mapped[str] = mapped_column(
        String(20),
        ForeignKey("students.student_id"),
        nullable=False,
        index=True,
    )
    course_name: Mapped[str] = mapped_column(String(120), nullable=False)
    day: Mapped[str] = mapped_column(String(20), nullable=False)
    time: Mapped[str] = mapped_column(String(20), nullable=False)
    room: Mapped[str] = mapped_column(String(20), nullable=False)

