"""Async SQLAlchemy QueueRepository (TASK-063)."""

from __future__ import annotations

import uuid

from sqlalchemy import delete, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.queue.interfaces.repositories import QueueRepository
from app.modules.queue.mappers.queue_mapper import QueueMapper
from app.modules.queue.models import Queue
from app.modules.queue.orm.models import QueueORM


class SqlAlchemyQueueRepository(QueueRepository):
    """Queue persistence via AsyncSession. No business rules."""

    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def add(self, queue: Queue) -> Queue:
        row = QueueMapper.to_orm(queue)
        self._session.add(row)
        await self._session.flush()
        await self._session.refresh(row)
        return QueueMapper.to_domain(row)

    async def get_by_id(self, queue_id: uuid.UUID) -> Queue | None:
        row = await self._session.get(QueueORM, queue_id)
        if row is None:
            return None
        return QueueMapper.to_domain(row)

    async def update(self, queue: Queue) -> Queue:
        row = await self._session.get(QueueORM, queue.queue_id)
        if row is None:
            raise KeyError(f"queue not found: {queue.queue_id}")
        QueueMapper.apply_to_orm(queue, row)
        await self._session.flush()
        await self._session.refresh(row)
        return QueueMapper.to_domain(row)

    async def list_by_organization(
        self, organization_id: uuid.UUID
    ) -> tuple[Queue, ...]:
        stmt = (
            select(QueueORM)
            .where(QueueORM.organization_id == organization_id)
            .order_by(QueueORM.name.asc(), QueueORM.queue_id.asc())
        )
        result = await self._session.scalars(stmt)
        return tuple(QueueMapper.to_domain(row) for row in result.all())

    async def delete(self, queue_id: uuid.UUID) -> bool:
        stmt = delete(QueueORM).where(QueueORM.queue_id == queue_id)
        result = await self._session.execute(stmt)
        await self._session.flush()
        return bool(result.rowcount)


__all__ = ["SqlAlchemyQueueRepository"]
