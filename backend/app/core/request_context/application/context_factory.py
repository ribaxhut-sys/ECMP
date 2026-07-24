"""Build RequestContext from plain values (no FastAPI / HTTP)."""

from __future__ import annotations

from collections.abc import Iterable
from uuid import UUID, uuid4

from app.core.request_context.domain.request_context import RequestContext


class RequestContextFactory:
    """Create immutable :class:`RequestContext` instances.

    Accepts simple data only. Does not read headers or know FastAPI.
    Generates ``request_id`` / ``correlation_id`` when callers omit them.
    """

    def create(
        self,
        *,
        organization_id: UUID | None = None,
        branch_id: UUID | None = None,
        user_id: UUID | None = None,
        correlation_id: str | None = None,
        request_id: str | None = None,
        roles: Iterable[str] | None = None,
        permissions: Iterable[str] | None = None,
        locale: str | None = None,
        timezone: str | None = None,
    ) -> RequestContext:
        """Assemble a :class:`RequestContext` from optional identity / tracing fields."""
        return RequestContext(
            request_id=request_id if request_id else str(uuid4()),
            correlation_id=correlation_id if correlation_id else str(uuid4()),
            organization_id=organization_id,
            branch_id=branch_id,
            user_id=user_id,
            roles=frozenset(roles) if roles is not None else frozenset(),
            permissions=(
                frozenset(permissions) if permissions is not None else frozenset()
            ),
            locale=locale,
            timezone=timezone,
        )


__all__ = ["RequestContextFactory"]
