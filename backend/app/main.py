"""Application entry point."""

from __future__ import annotations

import uvicorn

from app.core.app import create_app
from app.core.config import get_settings

app = create_app()


def main() -> None:
    """Run the application with Uvicorn."""

    settings = get_settings()
    uvicorn.run(
        "app.main:app",
        host="127.0.0.1",
        port=8000,
        reload=settings.DEBUG,
    )


if __name__ == "__main__":
    main()
