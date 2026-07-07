"""Authentication endpoint tests."""

from __future__ import annotations

from jose import jwt
import pytest
from httpx import ASGITransport, AsyncClient
from sqlalchemy import func, select

from app.core.config import get_settings
from app.core.database import SessionLocal
from app.main import app
from app.models.user import User
from app.services.seed_service import seed_database


async def _get_client() -> AsyncClient:
    """Create an async client for the FastAPI application."""

    transport = ASGITransport(app=app)
    return AsyncClient(transport=transport, base_url="http://test")


async def _login(client: AsyncClient, student_id: str, password: str) -> dict[str, object]:
    """Authenticate a user and return the JSON payload."""

    response = await client.post(
        "/api/v1/auth/login",
        json={"student_id": student_id, "password": password},
    )
    assert response.status_code == 200
    return response.json()


def _count_users_by_role(role: str) -> int:
    """Count users with the given role in the seeded database."""

    db = SessionLocal()
    try:
        statement = select(func.count()).select_from(User).where(User.role == role)
        return int(db.execute(statement).scalar_one())
    finally:
        db.close()


def _count_user_by_student_id(student_id: str) -> int:
    """Count users with the given student ID in the seeded database."""

    db = SessionLocal()
    try:
        statement = select(func.count()).select_from(User).where(User.student_id == student_id)
        return int(db.execute(statement).scalar_one())
    finally:
        db.close()


@pytest.mark.anyio
async def test_student_login_succeeds() -> None:
    """Student login should return a bearer token for valid credentials."""

    async with await _get_client() as client:
        payload = await _login(client, "DS001", "password123")

    assert payload["token_type"] == "bearer"
    assert isinstance(payload["access_token"], str)
    assert payload["access_token"]


@pytest.mark.anyio
async def test_admin_login_succeeds() -> None:
    """Administrator login should use the same login endpoint."""

    async with await _get_client() as client:
        payload = await _login(client, "admin", "admin123")

    assert payload["token_type"] == "bearer"
    assert isinstance(payload["access_token"], str)
    assert payload["access_token"]


@pytest.mark.anyio
async def test_invalid_credentials_fail() -> None:
    """Login should fail for incorrect credentials."""

    async with await _get_client() as client:
        response = await client.post(
            "/api/v1/auth/login",
            json={"student_id": "DS001", "password": "wrong-password"},
        )

    assert response.status_code == 401


@pytest.mark.anyio
async def test_jwt_role_claim_matches_user_role() -> None:
    """JWT tokens should include the authenticated role claim."""

    settings = get_settings()
    async with await _get_client() as client:
        student_payload = await _login(client, "DS001", "password123")
        admin_payload = await _login(client, "admin", "admin123")

    student_claims = jwt.decode(
        student_payload["access_token"],
        settings.JWT_SECRET_KEY,
        algorithms=[settings.JWT_ALGORITHM],
    )
    admin_claims = jwt.decode(
        admin_payload["access_token"],
        settings.JWT_SECRET_KEY,
        algorithms=[settings.JWT_ALGORITHM],
    )

    assert student_claims["role"] == "student"
    assert admin_claims["role"] == "admin"


@pytest.mark.anyio
async def test_protected_endpoint_with_valid_token() -> None:
    """The protected endpoint should return the current user with a valid token."""

    async with await _get_client() as client:
        payload = await _login(client, "DS001", "password123")

        response = await client.get(
            "/api/v1/auth/me",
            headers={"Authorization": f"Bearer {payload['access_token']}"},
        )

    assert response.status_code == 200
    assert response.json() == {
        "student_id": "DS001",
        "name": "Ali Khan",
        "email": "ali.khan@example.edu",
        "role": "student",
    }


@pytest.mark.anyio
async def test_protected_endpoint_without_token() -> None:
    """The protected endpoint should reject missing tokens."""

    async with await _get_client() as client:
        response = await client.get("/api/v1/auth/me")

    assert response.status_code == 401


@pytest.mark.anyio
async def test_protected_endpoint_with_invalid_token() -> None:
    """The protected endpoint should reject invalid tokens."""

    async with await _get_client() as client:
        response = await client.get(
            "/api/v1/auth/me",
            headers={"Authorization": "Bearer invalid-token"},
        )

    assert response.status_code == 401


def test_seed_is_idempotent_and_includes_admin() -> None:
    """Running the seed process repeatedly should not create duplicates."""

    seed_database()
    first_student_count = _count_users_by_role("student")
    first_admin_count = _count_users_by_role("admin")
    first_admin_id_count = _count_user_by_student_id("admin")

    seed_database()
    second_student_count = _count_users_by_role("student")
    second_admin_count = _count_users_by_role("admin")
    second_admin_id_count = _count_user_by_student_id("admin")

    assert first_student_count == second_student_count
    assert first_admin_count == second_admin_count == 1
    assert first_admin_id_count == second_admin_id_count == 1
