"""Auth persistence (users + refresh tokens + audit)."""

from __future__ import annotations

import uuid
from datetime import datetime
from typing import Any

from sqlalchemy import or_, select
from sqlalchemy.orm import Session, joinedload

from app.models import AuditLog, RefreshToken, User


class AuthRepository:
    def __init__(self, session: Session) -> None:
        self._session = session

    @property
    def session(self) -> Session:
        return self._session

    def get_user_by_login(self, identifier: str) -> User | None:
        """Resolve active user by username or email (case-insensitive email)."""
        email_candidate = identifier.lower()
        stmt = (
            select(User)
            .options(joinedload(User.role))
            .where(
                User.deleted_at.is_(None),
                or_(
                    User.username == identifier,
                    User.email == email_candidate,
                ),
            )
        )
        return self._session.scalar(stmt)

    def get_user_by_id(self, user_id: uuid.UUID) -> User | None:
        stmt = (
            select(User)
            .options(joinedload(User.role))
            .where(User.id == user_id, User.deleted_at.is_(None))
        )
        return self._session.scalar(stmt)

    def get_refresh_by_hash(self, token_hash: str) -> RefreshToken | None:
        stmt = select(RefreshToken).where(RefreshToken.token_hash == token_hash)
        return self._session.scalar(stmt)

    def add_refresh_token(self, token: RefreshToken) -> RefreshToken:
        self._session.add(token)
        self._session.flush()
        return token

    def add_audit_log(
        self,
        *,
        actor_user_id: uuid.UUID | None,
        action: str,
        entity_id: uuid.UUID,
        new_value: dict[str, Any],
        old_value: dict[str, Any] | None = None,
        occurred_at: datetime | None = None,
    ) -> AuditLog:
        from datetime import UTC

        when = occurred_at or datetime.now(UTC)
        if when.tzinfo is None:
            when = when.replace(tzinfo=UTC)

        entry = AuditLog(
            actor_user_id=actor_user_id,
            action=action,
            entity_type="User",
            entity_id=entity_id,
            old_value=old_value,
            new_value=new_value,
            occurred_at=when,
        )
        self._session.add(entry)
        self._session.flush()
        return entry

    def commit(self) -> None:
        self._session.commit()

    def refresh(self, obj: Any) -> Any:
        self._session.refresh(obj)
        return obj

