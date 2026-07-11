"""Authentication endpoints."""

from __future__ import annotations

from urllib.parse import parse_qs

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi import Request
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.security import authenticate_user, create_access_token, get_current_user
from app.models.attendance import Attendance
from app.models.course import Course
from app.models.enrollment import Enrollment
from app.models.student import Student
from app.models.timetable import Timetable
from app.models.user import User
from app.schemas.auth import LoginRequest, TokenResponse, UserProfileResponse

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/login", response_model=TokenResponse)
async def login(request: Request, db: Session = Depends(get_db)) -> TokenResponse:
    """Authenticate a student and return a JWT access token."""

    content_type = request.headers.get("content-type", "")
    student_id: str | None = None
    password: str | None = None

    if content_type.startswith("application/json"):
        payload = LoginRequest.model_validate(await request.json())
        student_id = payload.student_id
        password = payload.password
    else:
        raw_body = (await request.body()).decode("utf-8")
        form_data = parse_qs(raw_body)
        student_id = (
            form_data.get("username", [None])[0] or form_data.get("student_id", [None])[0]
        )
        password = form_data.get("password", [None])[0]

    if not student_id or not password:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="student_id and password are required",
        )

    user = authenticate_user(db, student_id, password)
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect student ID or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    access_token = create_access_token({"sub": user.student_id, "role": user.role})
    return TokenResponse(access_token=access_token)


@router.get("/me", response_model=UserProfileResponse)
def read_current_user(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> UserProfileResponse:
    """Return the currently authenticated user profile."""

    student = db.execute(select(Student).where(Student.student_id == current_user.student_id)).scalar_one_or_none()
    attendance_average = None
    registered_courses = None
    credit_hours = None
    timetable_rows = []
    attendance_rows = []

    if current_user.role == "student":
        attendance_average = db.execute(
            select(func.round(func.avg(Attendance.attendance_percentage), 2))
            .where(Attendance.student_id == current_user.student_id)
        ).scalar_one_or_none()

        attendance_rows = db.execute(
            select(Course.course_name, Attendance.attendance_percentage)
            .join(Course, Course.id == Attendance.course_id)
            .where(Attendance.student_id == current_user.student_id)
            .order_by(Course.course_code)
        ).all()

        registered_courses = db.execute(
            select(func.count(Enrollment.id)).where(Enrollment.student_id == current_user.student_id)
        ).scalar_one()

        credit_hours = db.execute(
            select(func.coalesce(func.sum(Course.credit_hours), 0))
            .join(Enrollment, Enrollment.course_id == Course.id)
            .where(Enrollment.student_id == current_user.student_id)
        ).scalar_one()

        timetable_rows = db.execute(
            select(Timetable.course_name, Timetable.day, Timetable.time, Timetable.room)
            .where(Timetable.student_id == current_user.student_id)
            .order_by(Timetable.day, Timetable.time)
        ).all()

    return UserProfileResponse(
        student_id=current_user.student_id,
        name=current_user.name,
        email=current_user.email,
        role=current_user.role,
        program=student.program if student else None,
        semester=student.semester if student else None,
        cgpa=student.cgpa if student else None,
        attendance_percentage=float(attendance_average) if attendance_average is not None else None,
        credit_hours=int(credit_hours) if credit_hours is not None else None,
        registered_courses=int(registered_courses) if registered_courses is not None else None,
        timetable=[
            {
                "course_name": row.course_name,
                "day": row.day,
                "time": row.time,
                "room": row.room,
            }
            for row in timetable_rows
        ],
        attendance_records=[
            {
                "course_name": row.course_name,
                "attendance_percentage": float(row.attendance_percentage),
            }
            for row in attendance_rows
        ],
    )
