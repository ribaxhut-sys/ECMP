"""Immutable execution context for a single request (CAPABILITY-002).

Framework-independent: no FastAPI, HTTP, JWT, or header knowledge.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from uuid import UUID


@dataclass(frozen=True, slots=True)
class RequestContext:
    """Platform execution context passed from HTTP → Application → Domain.

    Authentication / Authorization populate identity fields later.
    Missing optional values remain ``None`` or empty collections — never raise.
    """

    request_id: str
    correlation_id: str
    organization_id: UUID | None = None
    branch_id: UUID | None = None
    user_id: UUID | None = None
    roles: frozenset[str] = field(default_factory=frozenset)
    permissions: frozenset[str] = field(default_factory=frozenset)
    locale: str | None = None
    timezone: str | None = None


__all__ = ["RequestContext"]
