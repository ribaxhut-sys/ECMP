"""HTTP header name constants for RequestContext (stub reader).

Controllers must not hardcode these strings — use the FastAPI provider.
"""

from __future__ import annotations

HEADER_REQUEST_ID = "X-Request-Id"
HEADER_CORRELATION_ID = "X-Correlation-Id"
HEADER_ORGANIZATION_ID = "X-Organization-Id"
HEADER_BRANCH_ID = "X-Branch-Id"
HEADER_USER_ID = "X-User-Id"
HEADER_LOCALE = "X-Locale"
HEADER_TIMEZONE = "X-Timezone"

__all__ = [
    "HEADER_BRANCH_ID",
    "HEADER_CORRELATION_ID",
    "HEADER_LOCALE",
    "HEADER_ORGANIZATION_ID",
    "HEADER_REQUEST_ID",
    "HEADER_TIMEZONE",
    "HEADER_USER_ID",
]
