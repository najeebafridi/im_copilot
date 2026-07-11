"""Authentication request and response schemas."""

from __future__ import annotations

from pydantic import BaseModel, Field


class LoginRequest(BaseModel):
    """Login payload."""

    student_id: str
    password: str


class TokenResponse(BaseModel):
    """JWT token response payload."""

    access_token: str
    token_type: str = "bearer"


class UserProfileResponse(BaseModel):
    """Public user profile payload."""

    student_id: str
    name: str
    email: str
    role: str
    program: str | None = None
    semester: int | None = None
    cgpa: float | None = None
    attendance_percentage: float | None = None
    credit_hours: int | None = None
    registered_courses: int | None = None
    timetable: list[TimetableEntryResponse] = Field(default_factory=list)
    attendance_records: list[AttendanceEntryResponse] = Field(default_factory=list)


class TimetableEntryResponse(BaseModel):
    """Timetable entry returned as part of the logged-in student profile."""

    course_name: str
    day: str
    time: str
    room: str


class AttendanceEntryResponse(BaseModel):
    """Attendance entry returned as part of the logged-in student profile."""

    course_name: str
    attendance_percentage: float


class StudentDashboardResponse(BaseModel):
    """Extended profile payload used by the dashboard."""

    student_id: str
    name: str
    email: str
    role: str
    program: str | None = None
    semester: int | None = None
    cgpa: float | None = None
    attendance_percentage: float | None = None
    credit_hours: int | None = None
    registered_courses: int | None = None
    timetable: list[TimetableEntryResponse] = Field(default_factory=list)
    attendance_records: list[AttendanceEntryResponse] = Field(default_factory=list)
