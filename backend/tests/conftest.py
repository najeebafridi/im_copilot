"""Pytest configuration and database setup."""

from __future__ import annotations

import os
from pathlib import Path

import pytest

TEST_DB_PATH = Path(__file__).resolve().parents[1] / "test_im_copilot.db"

os.environ.setdefault("DATABASE_URL", f"sqlite:///{TEST_DB_PATH.as_posix()}")
os.environ.setdefault("JWT_SECRET_KEY", "test-secret-key")
os.environ.setdefault("JWT_ALGORITHM", "HS256")
os.environ.setdefault("ACCESS_TOKEN_EXPIRE_MINUTES", "30")

from app.core.database import engine
from app.services.conversation.service import get_conversation_service
from app.services.seed_service import seed_database


@pytest.fixture(scope="session", autouse=True)
def prepare_test_database() -> None:
    """Create a clean seeded database for the test session."""

    if TEST_DB_PATH.exists():
        TEST_DB_PATH.unlink()

    seed_database()
    yield

    engine.dispose()
    if TEST_DB_PATH.exists():
        TEST_DB_PATH.unlink()


@pytest.fixture(autouse=True)
def reset_conversation_memory() -> None:
    """Ensure in-memory conversations do not leak between tests."""

    service = get_conversation_service()
    service.reset()
    yield
    service.reset()
