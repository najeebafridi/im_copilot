"""Authentication endpoint tests."""

from __future__ import annotations

import pytest
from httpx import ASGITransport, AsyncClient

from app.main import app


async def _get_client() -> AsyncClient:
    """Create an async client for the FastAPI application."""

    transport = ASGITransport(app=app)
    return AsyncClient(transport=transport, base_url="http://test")


@pytest.mark.anyio
async def test_successful_login() -> None:
    """Login should return a bearer token for valid credentials."""

    async with await _get_client() as client:
        response = await client.post(
            "/api/v1/auth/login",
            json={"student_id": "DS001", "password": "password123"},
        )

    assert response.status_code == 200
    data = response.json()
    assert data["token_type"] == "bearer"
    assert isinstance(data["access_token"], str)
    assert data["access_token"]


@pytest.mark.anyio
async def test_failed_login() -> None:
    """Login should fail for incorrect credentials."""

    async with await _get_client() as client:
        response = await client.post(
            "/api/v1/auth/login",
            json={"student_id": "DS001", "password": "wrong-password"},
        )

    assert response.status_code == 401


@pytest.mark.anyio
async def test_protected_endpoint_with_valid_token() -> None:
    """The protected endpoint should return the current user with a valid token."""

    async with await _get_client() as client:
        login_response = await client.post(
            "/api/v1/auth/login",
            json={"student_id": "DS001", "password": "password123"},
        )
        token = login_response.json()["access_token"]

        response = await client.get(
            "/api/v1/auth/me",
            headers={"Authorization": f"Bearer {token}"},
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
