"""HTTP middleware: request/correlation IDs + security headers (Sprint-08)."""

from __future__ import annotations

import time
import uuid
from collections.abc import Callable

from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import Response

from app.logging_config import (
    correlation_id_ctx,
    get_logger,
    request_id_ctx,
)

logger = get_logger("app.http")

REQUEST_ID_HEADER = "X-Request-ID"
CORRELATION_ID_HEADER = "X-Correlation-ID"

SECURITY_HEADERS = {
    "X-Content-Type-Options": "nosniff",
    "X-Frame-Options": "DENY",
    "Referrer-Policy": "no-referrer",
    # JSON API — minimal CSP (defense-in-depth; no HTML assets served here).
    "Content-Security-Policy": "default-src 'none'; frame-ancestors 'none'; base-uri 'none'",
}


def _sanitize_id(raw: str | None) -> str | None:
    if not raw:
        return None
    value = raw.strip()
    if not value or len(value) > 128:
        return None
    # Reject control characters / whitespace-only noise.
    if any(ord(ch) < 32 for ch in value):
        return None
    return value


class RequestContextMiddleware(BaseHTTPMiddleware):
    """Attach request_id + correlation_id; echo headers; structured access log."""

    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        request_id = _sanitize_id(request.headers.get(REQUEST_ID_HEADER)) or str(
            uuid.uuid4()
        )
        correlation_id = (
            _sanitize_id(request.headers.get(CORRELATION_ID_HEADER)) or request_id
        )

        req_token = request_id_ctx.set(request_id)
        corr_token = correlation_id_ctx.set(correlation_id)
        request.state.request_id = request_id
        request.state.correlation_id = correlation_id

        started = time.perf_counter()
        try:
            response = await call_next(request)
        except Exception:
            logger.exception(
                "request failed",
                extra={
                    "extra_fields": {
                        "method": request.method,
                        "path": request.url.path,
                    }
                },
            )
            raise
        finally:
            request_id_ctx.reset(req_token)
            correlation_id_ctx.reset(corr_token)

        duration_ms = round((time.perf_counter() - started) * 1000, 2)
        response.headers[REQUEST_ID_HEADER] = request_id
        response.headers[CORRELATION_ID_HEADER] = correlation_id

        # Re-bind for the access log line after reset (record attributes).
        logger.info(
            "request completed",
            extra={
                "correlation_id": correlation_id,
                "request_id": request_id,
                "extra_fields": {
                    "method": request.method,
                    "path": request.url.path,
                    "status_code": response.status_code,
                    "duration_ms": duration_ms,
                },
            },
        )
        return response


class SecurityHeadersMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        response = await call_next(request)
        for key, value in SECURITY_HEADERS.items():
            response.headers.setdefault(key, value)
        return response
