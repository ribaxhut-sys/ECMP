"""CAPABILITY-010 Timeline persistence repository (append + read only)."""

from __future__ import annotations

import uuid

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.modules.timeline.domain.entity import TimelineEntry
from app.modules.timeline.models import TimelineEntryORM


def _to_orm(entry: TimelineEntry) -> TimelineEntryORM:
    return TimelineEntryORM(
        id=entry.id,
        aggregate_type=entry.aggregate_type,
        aggregate_id=entry.aggregate_id,
        event_type=entry.event_type,
        title=entry.title,
        description=entry.description,
        actor_type=entry.actor_type,
        actor_id=entry.actor_id,
        actor_name=entry.actor_name,
        metadata_json=dict(entry.metadata) if entry.metadata else None,
        created_at=entry.created_at,
    )


def _to_entity(row: TimelineEntryORM) -> TimelineEntry:
    return TimelineEntry(
        id=row.id,
        aggregate_type=row.aggregate_type,
        aggregate_id=row.aggregate_id,
        event_type=row.event_type,
        title=row.title,
        description=row.description,
        actor_type=row.actor_type,
        actor_id=row.actor_id,
        actor_name=row.actor_name,
        metadata=dict(row.metadata_json or {}),
        created_at=row.created_at,
    )


class TimelineRepository:
    """Append-only repository — no update / delete methods."""

    def __init__(self, session: Session) -> None:
        self._session = session

    def add(self, entry: TimelineEntry) -> TimelineEntry:
        row = _to_orm(entry)
        self._session.add(row)
        self._session.flush()
        return _to_entity(row)

    def get(self, entry_id: uuid.UUID) -> TimelineEntry | None:
        row = self._session.scalar(
            select(TimelineEntryORM).where(TimelineEntryORM.id == entry_id)
        )
        return _to_entity(row) if row is not None else None

    def list(
        self,
        *,
        aggregate_type: str | None = None,
        aggregate_id: uuid.UUID | None = None,
        event_type: str | None = None,
        page: int = 1,
        page_size: int = 50,
    ) -> tuple[list[TimelineEntry], int]:
        page = max(1, page)
        page_size = max(1, min(page_size, 100))
        filters = []
        if aggregate_type is not None:
            filters.append(TimelineEntryORM.aggregate_type == aggregate_type)
        if aggregate_id is not None:
            filters.append(TimelineEntryORM.aggregate_id == aggregate_id)
        if event_type is not None:
            filters.append(TimelineEntryORM.event_type == event_type)

        count_stmt = select(func.count()).select_from(TimelineEntryORM)
        list_stmt = select(TimelineEntryORM).order_by(
            TimelineEntryORM.created_at.asc(),
            TimelineEntryORM.id.asc(),
        )
        for f in filters:
            count_stmt = count_stmt.where(f)
            list_stmt = list_stmt.where(f)

        total = int(self._session.scalar(count_stmt) or 0)
        list_stmt = list_stmt.offset((page - 1) * page_size).limit(page_size)
        rows = list(self._session.scalars(list_stmt).all())
        return [_to_entity(r) for r in rows], total

    def list_by_aggregate(
        self,
        *,
        aggregate_type: str,
        aggregate_id: uuid.UUID,
        page: int = 1,
        page_size: int = 100,
    ) -> tuple[list[TimelineEntry], int]:
        return self.list(
            aggregate_type=aggregate_type,
            aggregate_id=aggregate_id,
            page=page,
            page_size=page_size,
        )

    def commit(self) -> None:
        self._session.commit()

    def rollback(self) -> None:
        self._session.rollback()
