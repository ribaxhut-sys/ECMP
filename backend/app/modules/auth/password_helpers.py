"""Password management helpers shared by auth + users modules."""

from __future__ import annotations

import uuid
from datetime import UTC, datetime
from typing import Any

from fastapi import Request
from sqlalchemy import update
from sqlalchemy.orm import Session

from app.core.enums import AuditAction
from app.models import RefreshToken, User
from app.modules.audit.hooks import client_ip, client_user_agent, resolve_actor_name
from app.modules.audit.repository import AuditRepository
from app.modules.audit.service import AuditService


def revoke_all_refresh_tokens(session: Session, user_id: uuid.UUID) -> int:
    """Revoke every active refresh token for a user. Returns rows affected."""
    now = datetime.now(UTC)
    result = session.execute(
        update(RefreshToken)
        .where(
            RefreshToken.user_id == user_id,
            RefreshToken.revoked_at.is_(None),
        )
        .values(revoked_at=now)
    )
    return int(result.rowcount or 0)


def write_password_audit(
    session: Session,
    *,
    request: Request | None,
    event_type: str,
    entity_id: uuid.UUID | None,
    actor_id: uuid.UUID | None = None,
    action: AuditAction = AuditAction.UPDATE,
    new_values: dict[str, Any] | None = None,
    metadata: dict[str, Any] | None = None,
    commit: bool = False,
) -> None:
    """Platform audit for password events (supports unauthenticated callers)."""
    ip = client_ip(request) if request is not None else None
    ua = client_user_agent(request) if request is not None else None
    actor_name = resolve_actor_name(session, actor_id) if actor_id else None
    service = AuditService(AuditRepository(session))
    service.log(
        event_type=event_type,
        entity_type="User",
        action=action,
        entity_id=entity_id,
        actor_id=actor_id,
        actor_name=actor_name,
        ip_address=ip,
        user_agent=ua,
        new_values=new_values,
        metadata=metadata,
        commit=commit,
    )


def set_user_password(
    user: User,
    *,
    password_hash: str,
    actor_user_id: uuid.UUID | None,
    force_password_change: bool,
) -> None:
    """Apply a new password hash and audit timestamps (caller commits)."""
    now = datetime.now(UTC)
    user.password_hash = password_hash
    user.force_password_change = force_password_change
    user.updated_at = now
    if actor_user_id is not None:
        user.updated_by = actor_user_id
