"""Liveness and readiness operational probes."""

from __future__ import annotations

from typing import Literal

from fastapi import APIRouter, Response, status
from pydantic import BaseModel, Field
from sqlalchemy.exc import SQLAlchemyError

from app.core.config import get_settings
from app.core.logging import get_logger
from app.core.runtime_state import is_startup_complete
from app.db.async_session import ping_database_async
from app.db.session import ping_database

logger = get_logger("app.api.health")

router = APIRouter(tags=["health"])


class HealthResponse(BaseModel):
    """Legacy combined health payload (informational; not an orchestration probe)."""

    status: Literal["ok", "degraded"] = Field(description="Overall service status")
    service: str
    version: str
    environment: str
    database: Literal["up", "down"]


class LiveResponse(BaseModel):
    status: Literal["ok"] = Field(description="Process is alive")
    service: str


class ReadyChecks(BaseModel):
    startup: Literal["ok", "fail"]
    database: Literal["ok", "fail"]


class ReadyResponse(BaseModel):
    status: Literal["ready", "not_ready"]
    service: str
    checks: ReadyChecks


@router.get(
    "/live",
    response_model=LiveResponse,
    status_code=status.HTTP_200_OK,
    summary="Liveness probe",
)
async def live() -> LiveResponse:
    """Process liveness — never checks database or external services."""
    settings = get_settings()
    return LiveResponse(status="ok", service=settings.app_name)


@router.get(
    "/ready",
    response_model=ReadyResponse,
    responses={
        200: {"description": "Service is ready to serve traffic"},
        503: {"description": "Service is not ready (startup or database)"},
    },
    summary="Readiness probe",
)
async def ready(response: Response) -> ReadyResponse:
    """Readiness — startup initialization + lightweight database query."""
    settings = get_settings()
    startup_ok = is_startup_complete()
    database_ok = False
    if startup_ok:
        database_ok = await ping_database_async()
        if not database_ok:
            logger.warning("readiness check failed: database unavailable")

    checks = ReadyChecks(
        startup="ok" if startup_ok else "fail",
        database="ok" if database_ok else "fail",
    )
    if startup_ok and database_ok:
        response.status_code = status.HTTP_200_OK
        return ReadyResponse(status="ready", service=settings.app_name, checks=checks)

    response.status_code = status.HTTP_503_SERVICE_UNAVAILABLE
    return ReadyResponse(status="not_ready", service=settings.app_name, checks=checks)


@router.get(
    "/health",
    response_model=HealthResponse,
    status_code=status.HTTP_200_OK,
    summary="Service health (legacy informational)",
    deprecated=True,
)
def health() -> HealthResponse:
    """Legacy informational probe. Orchestrators must use GET /ready."""
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
