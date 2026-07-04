"""Database seed helpers for demo data."""

from __future__ import annotations

from dataclasses import dataclass
from itertools import cycle

from sqlalchemy.orm import Session

from app.core.database import SessionLocal, reset_db
from app.core.security import hash_password
from app.models.attendance import Attendance
from app.models.course import Course
from app.models.enrollment import Enrollment
from app.models.student import Student
from app.models.timetable import Timetable
from app.models.user import User

DEFAULT_PASSWORD = "password123"


@dataclass(frozen=True)
class StudentSeed:
    """Seed data for a single student."""

    student_id: str
    name: str
    email: str
    program: str
    semester: int
    cgpa: float


STUDENTS: list[StudentSeed] = [
    StudentSeed("DS001", "Ali Khan", "ali.khan@example.edu", "BS Data Science", 5, 3.72),
    StudentSeed("DS002", "Ayesha Malik", "ayesha.malik@example.edu", "BS Data Science", 5, 3.85),
    StudentSeed("DS003", "Hassan Ali", "hassan.ali@example.edu", "BS Software Engineering", 6, 3.44),
    StudentSeed("DS004", "Sara Ahmed", "sara.ahmed@example.edu", "BS Information Technology", 4, 3.61),
    StudentSeed("DS005", "Bilal Hussain", "bilal.hussain@example.edu", "BS Computer Science", 6, 3.29),
    StudentSeed("DS006", "Mariam Noor", "mariam.noor@example.edu", "BS Data Science", 5, 3.94),
    StudentSeed("DS007", "Umar Farooq", "umar.farooq@example.edu", "BS Artificial Intelligence", 7, 3.52),
    StudentSeed("DS008", "Hira Shah", "hira.shah@example.edu", "BS Data Science", 4, 3.67),
    StudentSeed("DS009", "Zain Abbas", "zain.abbas@example.edu", "BS Computer Science", 6, 3.13),
    StudentSeed("DS010", "Fatima Raza", "fatima.raza@example.edu", "BS Information Technology", 5, 3.88),
    StudentSeed("DS011", "Ahmed Saeed", "ahmed.saeed@example.edu", "BS Data Science", 7, 3.24),
    StudentSeed("DS012", "Noor Jahan", "noor.jahan@example.edu", "BS Software Engineering", 6, 3.56),
    StudentSeed("DS013", "Hamza Tariq", "hamza.tariq@example.edu", "BS Artificial Intelligence", 5, 3.47),
    StudentSeed("DS014", "Inaya Iqbal", "inaya.iqbal@example.edu", "BS Data Science", 4, 3.79),
    StudentSeed("DS015", "Osman Javed", "osman.javed@example.edu", "BS Computer Science", 6, 3.02),
    StudentSeed("DS016", "Laiba Khan", "laiba.khan@example.edu", "BS Information Technology", 5, 3.91),
    StudentSeed("DS017", "Saad Mehmood", "saad.mehmood@example.edu", "BS Data Science", 7, 3.38),
    StudentSeed("DS018", "Anaya Rehman", "anaya.rehman@example.edu", "BS Software Engineering", 4, 3.74),
    StudentSeed("DS019", "Daniyal Sheikh", "daniyal.sheikh@example.edu", "BS Artificial Intelligence", 6, 3.19),
    StudentSeed("DS020", "Maha Zubair", "maha.zubair@example.edu", "BS Data Science", 5, 3.83),
]

COURSES = [
    ("DS301", "Data Mining", 3),
    ("DS302", "Machine Learning", 3),
    ("DS303", "Big Data Analytics", 3),
    ("DS304", "Data Visualization", 2),
    ("DS305", "Deep Learning", 3),
    ("DS306", "Database Systems", 3),
    ("DS307", "Statistics", 2),
    ("DS308", "Final Year Project", 4),
]

GRADES = ["A", "A-", "B+", "B", "B-", "C+"]
ATTENDANCE_VALUES = [96.0, 93.5, 91.0, 88.0, 85.5, 82.0, 79.5, 97.0]
DAY_TIME_ROOM = [
    ("Monday", "09:00 AM", "R101"),
    ("Tuesday", "11:00 AM", "R202"),
    ("Wednesday", "01:00 PM", "R303"),
    ("Thursday", "03:00 PM", "R404"),
]


def seed_database() -> None:
    """Populate the database with demo university data."""

    reset_db()
    db = SessionLocal()
    try:
        _seed_courses(db)
        _seed_students_and_users(db)
        db.commit()
        print("[SEED] database rows committed")
    finally:
        db.close()


def _seed_courses(db: Session) -> list[Course]:
    """Insert the locked course list."""

    courses: list[Course] = []
    for course_code, course_name, credit_hours in COURSES:
        course = Course(
            course_code=course_code,
            course_name=course_name,
            credit_hours=credit_hours,
        )
        db.add(course)
        courses.append(course)
    db.flush()
    return courses


def _seed_students_and_users(db: Session) -> None:
    """Insert users, students, enrollments, attendance, and timetable rows."""

    courses = db.query(Course).order_by(Course.id).all()
    grade_cycle = cycle(GRADES)
    attendance_cycle = cycle(ATTENDANCE_VALUES)
    timetable_cycle = cycle(DAY_TIME_ROOM)

    for index, student_seed in enumerate(STUDENTS):
        user = User(
            student_id=student_seed.student_id,
            name=student_seed.name,
            email=student_seed.email,
            password_hash=hash_password(DEFAULT_PASSWORD),
            role="student",
        )
        student = Student(
            student_id=student_seed.student_id,
            program=student_seed.program,
            semester=student_seed.semester,
            cgpa=student_seed.cgpa,
        )
        db.add(user)
        db.add(student)
        db.flush()

        selected_courses = [courses[(index + offset) % len(courses)] for offset in range(4)]
        for course in selected_courses:
            db.add(
                Enrollment(
                    student_id=student_seed.student_id,
                    course_id=course.id,
                    grade=next(grade_cycle),
                )
            )
            db.add(
                Attendance(
                    student_id=student_seed.student_id,
                    course_id=course.id,
                    attendance_percentage=next(attendance_cycle),
                )
            )
            day, time, room = next(timetable_cycle)
            db.add(
                Timetable(
                    student_id=student_seed.student_id,
                    course_name=course.course_name,
                    day=day,
                    time=time,
                    room=room,
                )
            )
