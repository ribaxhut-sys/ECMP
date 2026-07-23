"""Health check schemas and routes."""

from __future__ import annotations

from typing import Literal

from fastapi import APIRouter, status
from pydantic import BaseModel, Field
from sqlalchemy.exc import SQLAlchemyError

from app.core.config import get_settings
from app.core.logging import get_logger
from app.db.session import ping_database

logger = get_logger("app.api.health")

router = APIRouter(tags=["health"])


class HealthResponse(BaseModel):
    status: Literal["ok", "degraded"] = Field(description="Overall service status")
    service: str
    version: str
    environment: str
    database: Literal["up", "down"]


@router.get(
    "/health",
    response_model=HealthResponse,
    status_code=status.HTTP_200_OK,
    summary="Service health",
)
def health() -> HealthResponse:
    """Liveness/readiness-style health probe for the foundation API."""
    settings = get_settings()
    db_status: Literal["up", "down"] = "down"
    overall: Literal["ok", "degraded"] = "degraded"

    try:
        if ping_database():
            db_status = "up"
            overall = "ok"
    except SQLAlchemyError:
        logger.exception("database health check failed")
    except Exception:
        logger.exception("unexpected health check failure")

    return HealthResponse(
        status=overall,
        service=settings.app_name,
        version=settings.app_version,
        environment=settings.environment,
        database=db_status,
    )
