"""Seed the database with demo data."""

from app.services.seed_service import seed_database


def main() -> None:
    """Reset and populate the database with demo records."""

    print("[SEED] Starting database seed...")
    seed_database()
    print("[SEED] Database seed complete.")


if __name__ == "__main__":
    main()
