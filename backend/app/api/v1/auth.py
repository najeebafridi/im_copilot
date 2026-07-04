"""Authentication endpoints."""

from __future__ import annotations

from urllib.parse import parse_qs

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi import Request
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.security import authenticate_user, create_access_token, get_current_user
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
def read_current_user(current_user: User = Depends(get_current_user)) -> UserProfileResponse:
    """Return the currently authenticated user profile."""

    return UserProfileResponse(
        student_id=current_user.student_id,
        name=current_user.name,
        email=current_user.email,
        role=current_user.role,
    )
