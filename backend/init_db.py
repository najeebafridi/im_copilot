"""Create the database tables for IM Copilot."""

from app.core.database import init_db


def main() -> None:
    """Initialize the SQLite database schema."""

    print("[DB] Creating database tables...")
    init_db()
    print("[DB] Database tables ready.")


if __name__ == "__main__":
    main()
