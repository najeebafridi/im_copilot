"""Course ORM model."""

from __future__ import annotations

from sqlalchemy import Integer, String
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import Base


class Course(Base):
    """Academic course information."""

    __tablename__ = "courses"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    course_code: Mapped[str] = mapped_column(String(20), unique=True, index=True, nullable=False)
    course_name: Mapped[str] = mapped_column(String(120), nullable=False)
    credit_hours: Mapped[int] = mapped_column(Integer, nullable=False)

