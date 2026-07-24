"""Notification Foundation persistence repository (TASK-030)."""

from __future__ import annotations

import uuid
from datetime import UTC, datetime

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.modules.notification.models import NotificationQueue, NotificationTemplate


class NotificationRepository:
    def __init__(self, session: Session) -> None:
        self._session = session

    # --- templates ---------------------------------------------------------

    def get_template_by_id(
        self, template_id: uuid.UUID
    ) -> NotificationTemplate | None:
        return self._session.scalar(
            select(NotificationTemplate).where(NotificationTemplate.id == template_id)
        )

    def get_template_by_code(self, code: str) -> NotificationTemplate | None:
        return self._session.scalar(
            select(NotificationTemplate).where(NotificationTemplate.code == code)
        )

    def list_templates(
        self, *, active_only: bool = False
    ) -> list[NotificationTemplate]:
        stmt = select(NotificationTemplate).order_by(NotificationTemplate.code.asc())
        if active_only:
            stmt = stmt.where(NotificationTemplate.is_active.is_(True))
        return list(self._session.scalars(stmt).all())

    def add_template(self, row: NotificationTemplate) -> NotificationTemplate:
        self._session.add(row)
        self._session.flush()
        return row

    def soft_delete_template(
        self, row: NotificationTemplate
    ) -> NotificationTemplate:
        """Soft-delete via is_active=False (no deleted_at on this table)."""
        row.is_active = False
        row.updated_at = datetime.now(UTC)
        self._session.flush()
        return row

    # --- queue -------------------------------------------------------------

    def get_queue_by_id(self, queue_id: uuid.UUID) -> NotificationQueue | None:
        return self._session.scalar(
            select(NotificationQueue).where(NotificationQueue.id == queue_id)
        )

    def list_queue(
        self, *, status: str | None = None, limit: int = 100
    ) -> list[NotificationQueue]:
        stmt = select(NotificationQueue).order_by(
            NotificationQueue.created_at.desc()
        )
        if status is not None:
            stmt = stmt.where(NotificationQueue.status == status)
        stmt = stmt.limit(max(1, min(limit, 500)))
        return list(self._session.scalars(stmt).all())

    def add_queue(self, row: NotificationQueue) -> NotificationQueue:
        self._session.add(row)
        self._session.flush()
        return row

    def commit(self) -> None:
        self._session.commit()

    def rollback(self) -> None:
        self._session.rollback()
