"""Repository abstractions for Queue persistence (TASK-063).

Domain-facing contracts. Implementations live under ``repositories/``.
No SQLAlchemy imports. Returns domain models only.
"""

from __future__ import annotations

import uuid
from abc import ABC, abstractmethod

from app.modules.queue.models import Queue, QueueCounter, QueueTicket


class QueueRepository(ABC):
    """Persistence port for the Queue aggregate root."""

    @abstractmethod
    async def add(self, queue: Queue) -> Queue:
        """Insert a new queue. Returns the persisted domain model."""

    @abstractmethod
    async def get_by_id(self, queue_id: uuid.UUID) -> Queue | None:
        """Load a queue by identity, or None if missing."""

    @abstractmethod
    async def update(self, queue: Queue) -> Queue:
        """Replace an existing queue snapshot. Returns the persisted model."""

    @abstractmethod
    async def list_by_organization(
        self, organization_id: uuid.UUID
    ) -> tuple[Queue, ...]:
        """List queues owned by an organization (stable order by name)."""

    @abstractmethod
    async def delete(self, queue_id: uuid.UUID) -> bool:
        """Hard-delete a queue. Returns True when a row was removed."""


class QueueTicketRepository(ABC):
    """Persistence port for immutable QueueTicket value objects."""

    @abstractmethod
    async def add(self, ticket: QueueTicket) -> QueueTicket:
        """Insert a new ticket. Returns the persisted domain model."""

    @abstractmethod
    async def get_by_id(self, ticket_id: uuid.UUID) -> QueueTicket | None:
        """Load a ticket by identity, or None if missing."""

    @abstractmethod
    async def update(self, ticket: QueueTicket) -> QueueTicket:
        """Replace an existing ticket snapshot (whole VO). Returns persisted model."""

    @abstractmethod
    async def list_by_queue(self, queue_id: uuid.UUID) -> tuple[QueueTicket, ...]:
        """List tickets for a queue (order: created_at ASC, ticket_id ASC)."""

    @abstractmethod
    async def list_by_queue_and_status(
        self, queue_id: uuid.UUID, status: str
    ) -> tuple[QueueTicket, ...]:
        """List tickets for a queue filtered by status value string."""

    @abstractmethod
    async def delete(self, ticket_id: uuid.UUID) -> bool:
        """Hard-delete a ticket. Returns True when a row was removed."""


class QueueCounterRepository(ABC):
    """Persistence port for QueueCounter.

    Domain ``QueueCounter`` has no ``queue_id``; association is a persistence
    concern passed explicitly on write / list operations.
    """

    @abstractmethod
    async def add(self, queue_id: uuid.UUID, counter: QueueCounter) -> QueueCounter:
        """Insert a counter bound to ``queue_id``. Returns domain model."""

    @abstractmethod
    async def get_by_id(self, counter_id: uuid.UUID) -> QueueCounter | None:
        """Load a counter by identity, or None if missing."""

    @abstractmethod
    async def get_queue_id(self, counter_id: uuid.UUID) -> uuid.UUID | None:
        """Return the owning queue_id for a counter, or None if missing."""

    @abstractmethod
    async def update(
        self, queue_id: uuid.UUID, counter: QueueCounter
    ) -> QueueCounter:
        """Replace an existing counter snapshot. Returns persisted model."""

    @abstractmethod
    async def list_by_queue(self, queue_id: uuid.UUID) -> tuple[QueueCounter, ...]:
        """List counters for a queue (stable order by name)."""

    @abstractmethod
    async def delete(self, counter_id: uuid.UUID) -> bool:
        """Hard-delete a counter. Returns True when a row was removed."""


__all__ = [
    "QueueCounterRepository",
    "QueueRepository",
    "QueueTicketRepository",
]
