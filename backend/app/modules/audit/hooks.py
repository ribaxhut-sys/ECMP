"""Helpers for synchronous audit writes from HTTP routers (TASK-031)."""

from __future__ import annotations

import uuid
from typing import Any

from fastapi import Request
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.auth import Principal
from app.core.client_ip import resolve_client_ip
from app.core.enums import AuditAction
from app.models import User
from app.modules.audit.repository import AuditRepository
from app.modules.audit.service import AuditService


def client_ip(request: Request) -> str | None:
    """Resolve client IP via the shared SECMIG-P5-005 trust boundary."""
    return resolve_client_ip(request)


def client_user_agent(request: Request) -> str | None:
    ua = request.headers.get("user-agent")
    if ua is None:
        return None
    cleaned = ua.strip()
    return cleaned or None


def resolve_actor_name(session: Session, actor_id: uuid.UUID | None) -> str | None:
    if actor_id is None:
        return None
    user = session.scalar(
        select(User).where(User.id == actor_id, User.deleted_at.is_(None))
    )
    if user is None:
        return None
    return user.username or user.full_name


def write_audit(
    session: Session,
    *,
    request: Request,
    principal: Principal,
    event_type: str,
    entity_type: str,
    action: AuditAction | str,
    entity_id: uuid.UUID | None = None,
    old_values: dict[str, Any] | None = None,
    new_values: dict[str, Any] | None = None,
    metadata: dict[str, Any] | None = None,
) -> None:
    """Append one platform audit row (same DB session; no domain logic)."""
    service = AuditService(AuditRepository(session))
    service.log(
        event_type=event_type,
        entity_type=entity_type,
        action=action,
        entity_id=entity_id,
        actor_id=principal.user_id,
        actor_name=resolve_actor_name(session, principal.user_id),
        ip_address=client_ip(request),
        user_agent=client_user_agent(request),
        old_values=old_values,
        new_values=new_values,
        metadata=metadata,
        commit=True,
    )
