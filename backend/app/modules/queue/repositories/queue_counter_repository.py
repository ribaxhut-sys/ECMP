"""Async SQLAlchemy QueueCounterRepository (TASK-063)."""

from __future__ import annotations

import uuid

from sqlalchemy import delete, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.queue.interfaces.repositories import QueueCounterRepository
from app.modules.queue.mappers.queue_mapper import QueueCounterMapper
from app.modules.queue.models import QueueCounter
from app.modules.queue.orm.models import QueueCounterORM


class SqlAlchemyQueueCounterRepository(QueueCounterRepository):
    """Counter persistence via AsyncSession. No business rules."""

    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def add(self, queue_id: uuid.UUID, counter: QueueCounter) -> QueueCounter:
        row = QueueCounterMapper.to_orm(queue_id, counter)
        self._session.add(row)
        await self._session.flush()
        await self._session.refresh(row)
        return QueueCounterMapper.to_domain(row)

    async def get_by_id(self, counter_id: uuid.UUID) -> QueueCounter | None:
        row = await self._session.get(QueueCounterORM, counter_id)
        if row is None:
            return None
        return QueueCounterMapper.to_domain(row)

    async def get_queue_id(self, counter_id: uuid.UUID) -> uuid.UUID | None:
        row = await self._session.get(QueueCounterORM, counter_id)
        if row is None:
            return None
        return row.queue_id

    async def update(
        self, queue_id: uuid.UUID, counter: QueueCounter
    ) -> QueueCounter:
        row = await self._session.get(QueueCounterORM, counter.counter_id)
        if row is None:
            raise KeyError(f"counter not found: {counter.counter_id}")
        QueueCounterMapper.apply_to_orm(queue_id, counter, row)
        await self._session.flush()
        await self._session.refresh(row)
        return QueueCounterMapper.to_domain(row)

    async def list_by_queue(self, queue_id: uuid.UUID) -> tuple[QueueCounter, ...]:
        stmt = (
            select(QueueCounterORM)
            .where(QueueCounterORM.queue_id == queue_id)
            .order_by(QueueCounterORM.name.asc(), QueueCounterORM.counter_id.asc())
        )
        result = await self._session.scalars(stmt)
        return tuple(QueueCounterMapper.to_domain(row) for row in result.all())

    async def delete(self, counter_id: uuid.UUID) -> bool:
        stmt = delete(QueueCounterORM).where(
            QueueCounterORM.counter_id == counter_id
        )
        result = await self._session.execute(stmt)
        await self._session.flush()
        return bool(result.rowcount)


__all__ = ["SqlAlchemyQueueCounterRepository"]
