"""Per-user Knowledge pin persistence (0104).

Every read is scoped to a single ``user_id`` — one user's pins are never
visible to another, and no query here may be called without one.
"""

from __future__ import annotations

import uuid
from datetime import UTC, datetime

from sqlalchemy import delete, func, select
from sqlalchemy.dialects.postgresql import insert as pg_insert
from sqlalchemy.orm import Session

from app.modules.knowledge.models import KnowledgeUserPinORM

#: Business rule — a user may pin at most this many Knowledge records.
MAX_PINS_PER_USER = 10


class KnowledgePinRepository:
    def __init__(self, session: Session) -> None:
        self._session = session

    def pinned_ids(self, user_id: uuid.UUID) -> set[uuid.UUID]:
        rows = self._session.scalars(
            select(KnowledgeUserPinORM.knowledge_id).where(
                KnowledgeUserPinORM.user_id == user_id
            )
        ).all()
        return set(rows)

    def count_for_user(self, user_id: uuid.UUID) -> int:
        return int(
            self._session.scalar(
                select(func.count())
                .select_from(KnowledgeUserPinORM)
                .where(KnowledgeUserPinORM.user_id == user_id)
            )
            or 0
        )

    def is_pinned(self, *, user_id: uuid.UUID, knowledge_id: uuid.UUID) -> bool:
        return (
            self._session.scalar(
                select(KnowledgeUserPinORM.id).where(
                    KnowledgeUserPinORM.user_id == user_id,
                    KnowledgeUserPinORM.knowledge_id == knowledge_id,
                )
            )
            is not None
        )

    def pin(
        self,
        *,
        user_id: uuid.UUID,
        knowledge_id: uuid.UUID,
        now: datetime | None = None,
    ) -> None:
        """Idempotent — pinning twice leaves exactly one row (0104 unique pair)."""
        stmt = (
            pg_insert(KnowledgeUserPinORM)
            .values(
                user_id=user_id,
                knowledge_id=knowledge_id,
                pinned_at=now or datetime.now(UTC),
            )
            .on_conflict_do_nothing(index_elements=["knowledge_id", "user_id"])
        )
        self._session.execute(stmt)
        self._session.flush()

    def unpin(self, *, user_id: uuid.UUID, knowledge_id: uuid.UUID) -> None:
        """Idempotent — unpinning what was never pinned is not an error."""
        self._session.execute(
            delete(KnowledgeUserPinORM).where(
                KnowledgeUserPinORM.user_id == user_id,
                KnowledgeUserPinORM.knowledge_id == knowledge_id,
            )
        )
        self._session.flush()

    def commit(self) -> None:
        self._session.commit()
