"""Attachment persistence repository (TASK-029)."""

from __future__ import annotations

import uuid
from datetime import UTC, datetime

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.modules.attachment.models import Attachment


class AttachmentRepository:
    def __init__(self, session: Session) -> None:
        self._session = session

    def get_by_id(self, attachment_id: uuid.UUID) -> Attachment | None:
        stmt = select(Attachment).where(
            Attachment.id == attachment_id,
            Attachment.deleted_at.is_(None),
        )
        return self._session.scalar(stmt)

    def add(self, attachment: Attachment) -> Attachment:
        self._session.add(attachment)
        self._session.flush()
        return attachment

    def soft_delete(self, attachment: Attachment) -> Attachment:
        attachment.deleted_at = datetime.now(UTC)
        self._session.flush()
        return attachment

    def commit(self) -> None:
        self._session.commit()

    def rollback(self) -> None:
        self._session.rollback()
