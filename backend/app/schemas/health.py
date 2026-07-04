"""Schemas for health endpoints."""

from pydantic import BaseModel


class HealthResponse(BaseModel):
    """Response payload for the health endpoint."""

    status: str
    project: str

