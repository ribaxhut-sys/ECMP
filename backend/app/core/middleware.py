"""HTTP middleware: request logging + security headers (no PII / no tokens)."""

from __future__ import annotations

import time
import uuid
from collections.abc import Callable

from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import Response

from app.core.logging import get_logger

logger = get_logger("app.http")

REQUEST_ID_HEADER = "X-Request-ID"

SECURITY_HEADERS = {
    "X-Content-Type-Options": "nosniff",
    "X-Frame-Options": "DENY",
    "Referrer-Policy": "no-referrer",
    "Permissions-Policy": "geolocation=(), microphone=(), camera=()",
    # JSON API — minimal CSP (defense-in-depth; no HTML assets served here).
    "Content-Security-Policy": "default-src 'none'; frame-ancestors 'none'; base-uri 'none'",
}


def _sanitize_id(raw: str | None) -> str | None:
    if not raw:
        return None
    value = raw.strip()
    if not value or len(value) > 128:
        return None
    if any(ord(ch) < 32 for ch in value):
        return None
    return value


class RequestLoggingMiddleware(BaseHTTPMiddleware):
    """Emit structured access logs; echo X-Request-ID. Never log Authorization."""

    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        request_id = _sanitize_id(request.headers.get(REQUEST_ID_HEADER)) or str(
            uuid.uuid4()
        )
        request.state.request_id = request_id
        started = time.perf_counter()
        status_code = 500

        try:
            response = await call_next(request)
            status_code = response.status_code
            response.headers[REQUEST_ID_HEADER] = request_id
            return response
        except Exception:
            logger.exception(
                "request failed method=%s path=%s request_id=%s",
                request.method,
                request.url.path,
                request_id,
            )
            raise
        finally:
            duration_ms = round((time.perf_counter() - started) * 1000, 2)
            logger.info(
                "request method=%s path=%s status=%s duration_ms=%s request_id=%s",
                request.method,
                request.url.path,
                status_code,
                duration_ms,
                request_id,
            )


class SecurityHeadersMiddleware(BaseHTTPMiddleware):
    """Attach baseline security headers to every response."""

    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        response = await call_next(request)
        for key, value in SECURITY_HEADERS.items():
            response.headers.setdefault(key, value)
        return response
