"""Student ORM model."""

from __future__ import annotations

from sqlalchemy import Float, Integer, String
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import Base


class Student(Base):
    """Student profile data."""

    __tablename__ = "students"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    student_id: Mapped[str] = mapped_column(String(20), unique=True, index=True, nullable=False)
    program: Mapped[str] = mapped_column(String(120), nullable=False)
    semester: Mapped[int] = mapped_column(Integer, nullable=False)
    cgpa: Mapped[float] = mapped_column(Float, nullable=False)

