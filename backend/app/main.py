"""ECMP FastAPI application entrypoint."""

from __future__ import annotations

from contextlib import asynccontextmanager
from typing import Any

from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from starlette.exceptions import HTTPException as StarletteHTTPException
from starlette.middleware.trustedhost import TrustedHostMiddleware

from app import __version__
from app.api.router import api_router
from app.core.authorization.auth_strategy import configure_authentication
from app.core.config import get_settings, validate_runtime_config
from app.core.errors import ApiError
from app.core.keys import (
    build_registry_from_settings,
    clear_key_registry,
    configure_key_registry,
)
from app.core.logging import configure_logging, get_logger
from app.core.middleware import RequestLoggingMiddleware, SecurityHeadersMiddleware
from app.core.operational_security import retry_after_header_value
from app.core.runtime_state import mark_startup_complete, mark_startup_incomplete
from app.core.schemas import ErrorResponse
from app.core.secrets import (
    clear_runtime_secrets,
    redact_mapping,
    redact_text,
    register_runtime_secrets,
    safe_exception_text,
)
from app.core.user_messages import (
    code_message,
    field_errors_from_validation,
    localize_legacy,
    m,
)

logger = get_logger("app.main")

_CORS_METHODS = ["GET", "POST", "PUT", "PATCH", "DELETE", "OPTIONS"]
_CORS_HEADERS = [
    "Authorization",
    "Content-Type",
    "X-Request-ID",
    "Accept",
    "Idempotency-Key",
    "X-Channel-Message-Id",
]


@asynccontextmanager
async def lifespan(_: FastAPI):
    settings = get_settings()
    configure_logging(settings.log_level, log_format=settings.log_format)
    validate_runtime_config(settings)
    register_runtime_secrets(settings)
    configure_key_registry(build_registry_from_settings(settings))
    configure_authentication(settings)
    mark_startup_complete()
    logger.info(
        "application started name=%s version=%s env=%s auth_mode=%s ecmp_env=%s",
        settings.app_name,
        settings.app_version,
        settings.environment,
        settings.ecmp_auth_mode,
        settings.ecmp_env,
    )
    try:
        yield
    finally:
        mark_startup_incomplete()
        clear_key_registry()
        clear_runtime_secrets()
        logger.info("application stopped")


def _error_body(
    code: str,
    message: str,
    details: dict[str, Any] | None = None,
) -> dict[str, Any]:
    safe_message = redact_text(message)
    safe_details: dict[str, Any] | None = None
    if details is not None:
        scrubbed = redact_mapping(details)
        safe_details = scrubbed if isinstance(scrubbed, dict) else None
    return ErrorResponse(
        code=code,
        message=safe_message,
        details=safe_details,
    ).model_dump()


def create_app() -> FastAPI:
    settings = get_settings()
    docs_enabled = settings.docs_enabled

    application = FastAPI(
        title=settings.app_name,
        version=settings.app_version,
        description="Enterprise Complaint Management Platform — foundation API",
        lifespan=lifespan,
        docs_url="/docs" if docs_enabled else None,
        redoc_url="/redoc" if docs_enabled else None,
        openapi_url="/openapi.json" if docs_enabled else None,
    )

    # Middleware order: last added runs first on request.
    application.add_middleware(SecurityHeadersMiddleware)
    application.add_middleware(RequestLoggingMiddleware)
    application.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_origins,
        allow_credentials=True,
        allow_methods=_CORS_METHODS,
        allow_headers=_CORS_HEADERS,
    )
    if not settings.is_development:
        application.add_middleware(
            TrustedHostMiddleware,
            allowed_hosts=settings.trusted_hosts,
        )

    application.include_router(api_router, prefix=settings.api_prefix)

    @application.exception_handler(ApiError)
    async def api_error_handler(_: Request, exc: ApiError) -> JSONResponse:
        # SECMIG-P5-005: surface Retry-After when body already exposes
        # retryAfterSeconds (lockout / rate-limit). JSON envelope unchanged.
        headers: dict[str, str] = {}
        retry_after = retry_after_header_value(
            exc.details if isinstance(exc.details, dict) else None
        )
        if retry_after is not None:
            headers["Retry-After"] = retry_after
        return JSONResponse(
            status_code=exc.status_code,
            content=_error_body(exc.code, exc.message, exc.details),
            headers=headers,
        )

    @application.exception_handler(RequestValidationError)
    async def validation_error_handler(
        _: Request, exc: RequestValidationError
    ) -> JSONResponse:
        field_errors = field_errors_from_validation(exc.errors())
        return JSONResponse(
            status_code=400,
            content=_error_body(
                "VALIDATION_ERROR",
                m("common.validation_failed"),
                field_errors or None,
            ),
        )

    @application.exception_handler(StarletteHTTPException)
    async def http_exception_handler(
        _: Request, exc: StarletteHTTPException
    ) -> JSONResponse:
        code_map = {
            401: "UNAUTHENTICATED",
            403: "FORBIDDEN",
            404: "NOT_FOUND",
            405: "METHOD_NOT_ALLOWED",
        }
        code = code_map.get(exc.status_code, "HTTP_ERROR")
        if isinstance(exc.detail, str):
            message = localize_legacy(exc.detail, fallback_code=code)
        else:
            message = code_message(code)
        return JSONResponse(
            status_code=exc.status_code,
            content=_error_body(code, message),
        )

    @application.exception_handler(Exception)
    async def unhandled_error_handler(_: Request, exc: Exception) -> JSONResponse:
        logger.exception("unhandled error: %s", safe_exception_text(exc))
        return JSONResponse(
            status_code=500,
            content=_error_body("INTERNAL_ERROR", m("common.internal_error")),
        )

    @application.get("/", include_in_schema=False)
    def root() -> dict[str, str]:
        payload = {
            "name": settings.app_name,
            "version": __version__,
            "live": "/live",
            "ready": "/ready",
            "health": "/health",
            "version_info": "/version",
        }
        if docs_enabled:
            payload["docs"] = "/docs"
        return payload

    return application


app = create_app()
