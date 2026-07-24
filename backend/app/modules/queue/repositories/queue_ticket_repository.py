"""Async SQLAlchemy QueueTicketRepository (TASK-063)."""

from __future__ import annotations

import uuid

from sqlalchemy import delete, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.queue.interfaces.repositories import QueueTicketRepository
from app.modules.queue.mappers.queue_mapper import QueueTicketMapper
from app.modules.queue.models import QueueTicket
from app.modules.queue.orm.models import QueueTicketORM


class SqlAlchemyQueueTicketRepository(QueueTicketRepository):
    """Ticket persistence via AsyncSession. No business rules."""

    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def add(self, ticket: QueueTicket) -> QueueTicket:
        row = QueueTicketMapper.to_orm(ticket)
        self._session.add(row)
        await self._session.flush()
        await self._session.refresh(row)
        return QueueTicketMapper.to_domain(row)

    async def get_by_id(self, ticket_id: uuid.UUID) -> QueueTicket | None:
        row = await self._session.get(QueueTicketORM, ticket_id)
        if row is None:
            return None
        return QueueTicketMapper.to_domain(row)

    async def update(self, ticket: QueueTicket) -> QueueTicket:
        row = await self._session.get(QueueTicketORM, ticket.ticket_id)
        if row is None:
            raise KeyError(f"ticket not found: {ticket.ticket_id}")
        QueueTicketMapper.apply_to_orm(ticket, row)
        await self._session.flush()
        await self._session.refresh(row)
        return QueueTicketMapper.to_domain(row)

    async def list_by_queue(self, queue_id: uuid.UUID) -> tuple[QueueTicket, ...]:
        stmt = (
            select(QueueTicketORM)
            .where(QueueTicketORM.queue_id == queue_id)
            .order_by(
                QueueTicketORM.created_at.asc(),
                QueueTicketORM.ticket_id.asc(),
            )
        )
        result = await self._session.scalars(stmt)
        return tuple(QueueTicketMapper.to_domain(row) for row in result.all())

    async def list_by_queue_and_status(
        self, queue_id: uuid.UUID, status: str
    ) -> tuple[QueueTicket, ...]:
        stmt = (
            select(QueueTicketORM)
            .where(
                QueueTicketORM.queue_id == queue_id,
                QueueTicketORM.status == status,
            )
            .order_by(
                QueueTicketORM.created_at.asc(),
                QueueTicketORM.ticket_id.asc(),
            )
        )
        result = await self._session.scalars(stmt)
        return tuple(QueueTicketMapper.to_domain(row) for row in result.all())

    async def delete(self, ticket_id: uuid.UUID) -> bool:
        stmt = delete(QueueTicketORM).where(QueueTicketORM.ticket_id == ticket_id)
        result = await self._session.execute(stmt)
        await self._session.flush()
        return bool(result.rowcount)


__all__ = ["SqlAlchemyQueueTicketRepository"]
