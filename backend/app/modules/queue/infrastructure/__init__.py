"""Queue persistence infrastructure wiring (TASK-063).

DI factories for SQLAlchemy repositories. No UnitOfWork.
No REST. No Redis. Session is supplied by the caller.
"""

from __future__ import annotations

from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.queue.interfaces.repositories import (
    QueueCounterRepository,
    QueueRepository,
    QueueTicketRepository,
)
from app.modules.queue.repositories.queue_counter_repository import (
    SqlAlchemyQueueCounterRepository,
)
from app.modules.queue.repositories.queue_repository import SqlAlchemyQueueRepository
from app.modules.queue.repositories.queue_ticket_repository import (
    SqlAlchemyQueueTicketRepository,
)


def get_queue_repository(session: AsyncSession) -> QueueRepository:
    """DI factory — QueueRepository bound to the given AsyncSession."""
    return SqlAlchemyQueueRepository(session)


def get_queue_ticket_repository(session: AsyncSession) -> QueueTicketRepository:
    """DI factory — QueueTicketRepository bound to the given AsyncSession."""
    return SqlAlchemyQueueTicketRepository(session)


def get_queue_counter_repository(session: AsyncSession) -> QueueCounterRepository:
    """DI factory — QueueCounterRepository bound to the given AsyncSession."""
    return SqlAlchemyQueueCounterRepository(session)


__all__ = [
    "get_queue_counter_repository",
    "get_queue_repository",
    "get_queue_ticket_repository",
]
