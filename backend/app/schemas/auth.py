"""Authentication request and response schemas."""

from __future__ import annotations

from pydantic import BaseModel


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

