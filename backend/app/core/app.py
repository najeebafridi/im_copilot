"""FastAPI application factory."""

from __future__ import annotations

import logging
from collections.abc import AsyncIterator
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from starlette.requests import Request

from app.api.router import api_router
from app.core.config import get_settings
from app.core.database import init_db
from app.core.logging import configure_logging
from app.services.llm.exceptions import LLMConfigurationError, LLMProviderError, LLMResponseValidationError
from app.services.router.exceptions import RouterConfigurationError
from app.services.router.router_service import get_router_service


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncIterator[None]:
    """Manage application startup and shutdown."""

    init_db()
    try:
        get_router_service()
    except RouterConfigurationError:
        logging.getLogger(__name__).exception("Router configuration failed to load during startup")
    logging.getLogger(__name__).info("Application startup complete")
    print("[APP] startup complete")
    yield


def create_app() -> FastAPI:
    """Create and configure the FastAPI application."""

    settings = get_settings()
    configure_logging(settings.DEBUG)

    app = FastAPI(title=settings.PROJECT_NAME, debug=settings.DEBUG, lifespan=lifespan)

    app.add_middleware(
        CORSMiddleware,
        allow_origins=[
            "http://localhost",
            "http://localhost:3000",
            "http://localhost:5173",
            "http://127.0.0.1",
            "http://127.0.0.1:3000",
            "http://127.0.0.1:5173",
        ],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    @app.exception_handler(LLMConfigurationError)
    async def _handle_llm_configuration_error(_: Request, exc: LLMConfigurationError) -> JSONResponse:
        return JSONResponse(status_code=500, content={"detail": str(exc)})

    @app.exception_handler(LLMProviderError)
    async def _handle_llm_provider_error(_: Request, exc: LLMProviderError) -> JSONResponse:
        return JSONResponse(status_code=exc.status_code, content={"detail": str(exc)})

    @app.exception_handler(LLMResponseValidationError)
    async def _handle_llm_validation_error(_: Request, exc: LLMResponseValidationError) -> JSONResponse:
        return JSONResponse(status_code=502, content={"detail": str(exc)})

    @app.exception_handler(RouterConfigurationError)
    async def _handle_router_configuration_error(_: Request, exc: RouterConfigurationError) -> JSONResponse:
        return JSONResponse(status_code=500, content={"detail": str(exc)})

    app.include_router(api_router, prefix=settings.API_V1_PREFIX)
    return app
