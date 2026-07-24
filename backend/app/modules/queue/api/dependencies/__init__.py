"""FastAPI dependencies for Queue REST (TASK-064 / CAPABILITY-002 / CAPABILITY-003).

RequestContext comes from Core — Queue does not own execution context.
"""

from __future__ import annotations

from collections.abc import AsyncGenerator
from typing import Annotated

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.request_context import RequestContext, get_request_context
from app.db.async_session import get_async_session_factory
from app.modules.queue.application.services import (
    QueueCrudApplicationService,
    QueueDomainService,
    QueueOperationsApplicationService,
    get_queue_domain_service,
)
from app.modules.queue.infrastructure import (
    get_queue_counter_repository,
    get_queue_repository,
    get_queue_ticket_repository,
)


async def get_queue_db_session() -> AsyncGenerator[AsyncSession, None]:
    """Yield AsyncSession; commit on success, rollback on failure."""
    session = get_async_session_factory()()
    try:
        yield session
        await session.commit()
    except Exception:
        await session.rollback()
        raise
    finally:
        await session.close()


def get_queue_crud_service(
    session: Annotated[AsyncSession, Depends(get_queue_db_session)],
    domain: Annotated[QueueDomainService, Depends(get_queue_domain_service)],
) -> QueueCrudApplicationService:
    """Wire Controllers → Application → Repository Interface → SQLAlchemy."""
    return QueueCrudApplicationService(
        queues=get_queue_repository(session),
        tickets=get_queue_ticket_repository(session),
        counters=get_queue_counter_repository(session),
        domain=domain,
    )


def get_queue_operations_service(
    session: Annotated[AsyncSession, Depends(get_queue_db_session)],
    domain: Annotated[QueueDomainService, Depends(get_queue_domain_service)],
) -> QueueOperationsApplicationService:
    """Wire operational Controllers → Operations Application → Repository ports."""
    return QueueOperationsApplicationService(
        queues=get_queue_repository(session),
        tickets=get_queue_ticket_repository(session),
        domain=domain,
    )


__all__ = [
    "RequestContext",
    "get_queue_crud_service",
    "get_queue_db_session",
    "get_queue_operations_service",
    "get_request_context",
]
