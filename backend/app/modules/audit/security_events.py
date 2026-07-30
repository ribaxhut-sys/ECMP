"""Security-event taxonomy and durable platform audit writers (SECMIG-P5-004).

Append-only rows go to platform ``audit_logs`` via AuditService.
Legacy ``audit_logs_legacy`` writers are unchanged.

Audit flood policy (SECMIG-P5-005): synchronous best-effort writes with no
sampling and no async workers — see ``app.core.operational_security``.
"""

from __future__ import annotations

import uuid
from enum import StrEnum
from typing import Any

from fastapi import Request
from sqlalchemy.orm import Session

from app.core.enums import AuditAction
from app.core.logging import get_logger
from app.modules.audit.repository import AuditRepository
from app.modules.audit.service import AuditService

logger = get_logger("app.audit.security")

REQUEST_ID_HEADERS = ("X-Request-ID", "X-Request-Id")
CORRELATION_ID_HEADERS = ("X-Correlation-Id", "X-Correlation-ID")


class SecurityEventType(StrEnum):
    """Centralized platform security-event taxonomy."""

    LOGIN_FAILED = "security.login_failed"
    TOKEN_REJECTED = "security.token_rejected"
    PERMISSION_DENIED = "security.permission_denied"
    LOCKOUT = "security.lockout"


SECURITY_EVENT_ACTIONS: dict[SecurityEventType, AuditAction] = {
    SecurityEventType.LOGIN_FAILED: AuditAction.LOGIN,
    SecurityEventType.TOKEN_REJECTED: AuditAction.LOGIN,
    SecurityEventType.PERMISSION_DENIED: AuditAction.UPDATE,
    SecurityEventType.LOCKOUT: AuditAction.LOGIN,
}

ENTITY_TYPE_SECURITY = "Security"


def _sanitize_id(raw: str | None) -> str | None:
    if not raw:
        return None
    value = raw.strip()
    if not value or len(value) > 128:
        return None
    if any(ord(ch) < 32 for ch in value):
        return None
    return value


def resolve_request_trace_ids(request: Request | None) -> tuple[str, str]:
    """Return ``(request_id, correlation_id)``.

    ``request_id`` is required (generated when absent).
    ``correlation_id`` defaults to ``request_id`` when unavailable.
    """
    request_id: str | None = None
    correlation_id: str | None = None

    if request is not None:
        request_id = _sanitize_id(getattr(request.state, "request_id", None))
        correlation_id = _sanitize_id(getattr(request.state, "correlation_id", None))
        if request_id is None:
            for header in REQUEST_ID_HEADERS:
                request_id = _sanitize_id(request.headers.get(header))
                if request_id:
                    break
        if correlation_id is None:
            for header in CORRELATION_ID_HEADERS:
                correlation_id = _sanitize_id(request.headers.get(header))
                if correlation_id:
                    break

    if not request_id:
        request_id = str(uuid.uuid4())
    if not correlation_id:
        correlation_id = request_id
    return request_id, correlation_id


def build_trace_metadata(
    request: Request | None,
    *,
    extra: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """Build audit metadata with required ``requestId`` + ``correlationId``."""
    request_id, correlation_id = resolve_request_trace_ids(request)
    metadata: dict[str, Any] = {
        "requestId": request_id,
        "correlationId": correlation_id,
    }
    if extra:
        metadata.update(extra)
    return metadata


def write_security_event(
    session: Session,
    *,
    request: Request | None,
    event_type: SecurityEventType | str,
    actor_id: uuid.UUID | None = None,
    entity_id: uuid.UUID | None = None,
    new_values: dict[str, Any] | None = None,
    metadata_extra: dict[str, Any] | None = None,
    commit: bool = True,
) -> None:
    """Persist one platform security audit row. Never raises to callers."""
    try:
        # Late import avoids circular auth ↔ audit import at module load.
        from app.modules.audit.hooks import (
            client_ip,
            client_user_agent,
            resolve_actor_name,
        )

        event = (
            event_type
            if isinstance(event_type, SecurityEventType)
            else SecurityEventType(str(event_type))
        )
        action = SECURITY_EVENT_ACTIONS[event]
        metadata = build_trace_metadata(request, extra=metadata_extra)
        if request is not None and "path" not in metadata:
            metadata["path"] = request.url.path

        service = AuditService(AuditRepository(session))
        service.log(
            event_type=event.value,
            entity_type=ENTITY_TYPE_SECURITY,
            action=action,
            entity_id=entity_id,
            actor_id=actor_id,
            actor_name=resolve_actor_name(session, actor_id) if actor_id else None,
            ip_address=client_ip(request) if request is not None else None,
            user_agent=client_user_agent(request) if request is not None else None,
            new_values=new_values,
            metadata=metadata,
            commit=commit,
        )
    except Exception:  # noqa: BLE001 — security audit must not break request path
        logger.exception("failed to persist security audit event")
