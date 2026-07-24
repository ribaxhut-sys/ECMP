"""Audit Log persistence repository (TASK-031)."""

from __future__ import annotations

import uuid
from datetime import datetime

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.modules.audit.models import SystemAuditLog


class AuditRepository:
    def __init__(self, session: Session) -> None:
        self._session = session

    def add(self, row: SystemAuditLog) -> SystemAuditLog:
        self._session.add(row)
        self._session.flush()
        return row

    def get_by_id(self, audit_id: uuid.UUID) -> SystemAuditLog | None:
        return self._session.scalar(
            select(SystemAuditLog).where(SystemAuditLog.id == audit_id)
        )

    def list(
        self,
        *,
        entity_type: str | None = None,
        entity_id: uuid.UUID | None = None,
        actor_id: uuid.UUID | None = None,
        action: str | None = None,
        date_from: datetime | None = None,
        date_to: datetime | None = None,
        limit: int = 100,
        offset: int = 0,
    ) -> list[SystemAuditLog]:
        stmt = select(SystemAuditLog).order_by(SystemAuditLog.created_at.desc())
        if entity_type is not None:
            stmt = stmt.where(SystemAuditLog.entity_type == entity_type)
        if entity_id is not None:
            stmt = stmt.where(SystemAuditLog.entity_id == entity_id)
        if actor_id is not None:
            stmt = stmt.where(SystemAuditLog.actor_id == actor_id)
        if action is not None:
            stmt = stmt.where(SystemAuditLog.action == action)
        if date_from is not None:
            stmt = stmt.where(SystemAuditLog.created_at >= date_from)
        if date_to is not None:
            stmt = stmt.where(SystemAuditLog.created_at <= date_to)
        stmt = stmt.offset(max(0, offset)).limit(max(1, min(limit, 500)))
        return list(self._session.scalars(stmt).all())

    def commit(self) -> None:
        self._session.commit()

    def flush(self) -> None:
        self._session.flush()
