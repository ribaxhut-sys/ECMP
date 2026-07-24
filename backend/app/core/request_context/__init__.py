"""Core Request Context (CAPABILITY-002).

HTTP → FastAPI Provider → RequestContextFactory → RequestContext → Application.

Import from this package only — do not redefine RequestContext in domain modules.
"""

from app.core.request_context.application.context_factory import RequestContextFactory
from app.core.request_context.domain.request_context import RequestContext
from app.core.request_context.infrastructure.fastapi_provider import get_request_context
from app.core.request_context.infrastructure.headers import (
    HEADER_BRANCH_ID,
    HEADER_CORRELATION_ID,
    HEADER_LOCALE,
    HEADER_ORGANIZATION_ID,
    HEADER_REQUEST_ID,
    HEADER_TIMEZONE,
    HEADER_USER_ID,
)

__all__ = [
    "HEADER_BRANCH_ID",
    "HEADER_CORRELATION_ID",
    "HEADER_LOCALE",
    "HEADER_ORGANIZATION_ID",
    "HEADER_REQUEST_ID",
    "HEADER_TIMEZONE",
    "HEADER_USER_ID",
    "RequestContext",
    "RequestContextFactory",
    "get_request_context",
]
