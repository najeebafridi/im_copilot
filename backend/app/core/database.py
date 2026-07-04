"""Database configuration and session management."""

from __future__ import annotations

from collections.abc import Generator

from sqlalchemy import create_engine, event
from sqlalchemy.orm import DeclarativeBase, Session, sessionmaker

from app.core.config import get_settings


class Base(DeclarativeBase):
    """Base class for all SQLAlchemy ORM models."""


def _build_engine():
    """Create the SQLAlchemy engine for the configured database."""

    settings = get_settings()
    connect_args = {"check_same_thread": False} if settings.DATABASE_URL.startswith("sqlite") else {}
    engine = create_engine(settings.DATABASE_URL, connect_args=connect_args)

    if settings.DATABASE_URL.startswith("sqlite"):

        @event.listens_for(engine, "connect")
        def _set_sqlite_pragma(dbapi_connection, connection_record):  # type: ignore[no-redef]
            """Enable foreign key support for SQLite."""

            cursor = dbapi_connection.cursor()
            cursor.execute("PRAGMA foreign_keys=ON")
            cursor.close()

    return engine


engine = _build_engine()
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def get_db() -> Generator[Session, None, None]:
    """Yield a database session for request handling."""

    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def init_db() -> None:
    """Create database tables if they do not already exist."""

    from app import models  # noqa: F401

    Base.metadata.create_all(bind=engine)


def reset_db() -> None:
    """Drop and recreate all database tables."""

    from app import models  # noqa: F401

    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)

