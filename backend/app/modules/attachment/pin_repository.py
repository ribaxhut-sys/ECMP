"""Per-user attachment pin persistence (0103).

Every read is scoped to a single ``user_id`` — one user's pins are never
visible to another, and no query here may be called without one.
"""

from __future__ import annotations

import uuid
from datetime import UTC, datetime

from sqlalchemy import delete, func, select
from sqlalchemy.dialects.postgresql import insert as pg_insert
from sqlalchemy.orm import Session

from app.modules.attachment.models import AttachmentUserPinORM

#: Business rule — a user may pin at most this many files.
MAX_PINS_PER_USER = 10


class AttachmentPinRepository:
    def __init__(self, session: Session) -> None:
        self._session = session

    def pinned_ids(self, user_id: uuid.UUID) -> set[uuid.UUID]:
        rows = self._session.scalars(
            select(AttachmentUserPinORM.attachment_id).where(
                AttachmentUserPinORM.user_id == user_id
            )
        ).all()
        return set(rows)

    def count_for_user(self, user_id: uuid.UUID) -> int:
        return int(
            self._session.scalar(
                select(func.count())
                .select_from(AttachmentUserPinORM)
                .where(AttachmentUserPinORM.user_id == user_id)
            )
            or 0
        )

    def is_pinned(self, *, user_id: uuid.UUID, attachment_id: uuid.UUID) -> bool:
        return (
            self._session.scalar(
                select(AttachmentUserPinORM.id).where(
                    AttachmentUserPinORM.user_id == user_id,
                    AttachmentUserPinORM.attachment_id == attachment_id,
                )
            )
            is not None
        )

    def pin(
        self,
        *,
        user_id: uuid.UUID,
        attachment_id: uuid.UUID,
        now: datetime | None = None,
    ) -> None:
        """Idempotent — pinning twice leaves exactly one row (0103 unique pair)."""
        stmt = (
            pg_insert(AttachmentUserPinORM)
            .values(
                user_id=user_id,
                attachment_id=attachment_id,
                pinned_at=now or datetime.now(UTC),
            )
            .on_conflict_do_nothing(index_elements=["attachment_id", "user_id"])
        )
        self._session.execute(stmt)
        self._session.flush()

    def unpin(self, *, user_id: uuid.UUID, attachment_id: uuid.UUID) -> None:
        """Idempotent — unpinning what was never pinned is not an error."""
        self._session.execute(
            delete(AttachmentUserPinORM).where(
                AttachmentUserPinORM.user_id == user_id,
                AttachmentUserPinORM.attachment_id == attachment_id,
            )
        )
        self._session.flush()

    def commit(self) -> None:
        self._session.commit()
