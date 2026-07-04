"""Health check endpoint."""

from fastapi import APIRouter

from app.schemas.health import HealthResponse

router = APIRouter(prefix="/health", tags=["health"])


@router.get("", response_model=HealthResponse)
def get_health() -> HealthResponse:
    """Return the application health status."""

    return HealthResponse(status="ok", project="IM Copilot")

