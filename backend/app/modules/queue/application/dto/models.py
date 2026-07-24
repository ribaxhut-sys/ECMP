"""Immutable Queue DTOs — application read/write contracts (TASK-062).

Not HTTP schemas. Not persistence entities.
"""

from __future__ import annotations

import uuid
from dataclasses import dataclass
from datetime import datetime
from types import MappingProxyType
from typing import Mapping

from app.modules.queue.models import (
    Queue,
    QueueCounter,
    QueuePolicy,
    QueuePriority,
    QueueStatus,
    QueueTicket,
    QueueTicketStatus,
)


@dataclass(frozen=True, slots=True)
class QueueDto:
    """Immutable queue snapshot for application consumers."""

    queue_id: uuid.UUID
    organization_id: uuid.UUID
    name: str
    description: str
    status: QueueStatus
    policy: QueuePolicy

    @classmethod
    def from_domain(cls, queue: Queue) -> QueueDto:
        return cls(
            queue_id=queue.queue_id,
            organization_id=queue.organization_id,
            name=queue.name,
            description=queue.description,
            status=queue.status,
            policy=queue.policy,
        )

    def as_dict(self) -> Mapping[str, object]:
        return MappingProxyType(
            {
                "queueId": str(self.queue_id),
                "organizationId": str(self.organization_id),
                "name": self.name,
                "description": self.description,
                "status": self.status.value,
                "policy": self.policy.value,
            }
        )


@dataclass(frozen=True, slots=True)
class QueueTicketDto:
    """Immutable ticket snapshot for application consumers."""

    ticket_id: uuid.UUID
    queue_id: uuid.UUID
    ticket_number: str
    priority: QueuePriority
    status: QueueTicketStatus
    created_at: datetime

    @classmethod
    def from_domain(cls, ticket: QueueTicket) -> QueueTicketDto:
        return cls(
            ticket_id=ticket.ticket_id,
            queue_id=ticket.queue_id,
            ticket_number=ticket.ticket_number,
            priority=ticket.priority,
            status=ticket.status,
            created_at=ticket.created_at,
        )

    def as_dict(self) -> Mapping[str, object]:
        return MappingProxyType(
            {
                "ticketId": str(self.ticket_id),
                "queueId": str(self.queue_id),
                "ticketNumber": self.ticket_number,
                "priority": self.priority.value,
                "status": self.status.value,
                "createdAt": self.created_at.isoformat(),
            }
        )


@dataclass(frozen=True, slots=True)
class QueueCounterDto:
    """Immutable counter snapshot for application consumers."""

    counter_id: uuid.UUID
    name: str
    status: QueueStatus

    @classmethod
    def from_domain(cls, counter: QueueCounter) -> QueueCounterDto:
        return cls(
            counter_id=counter.counter_id,
            name=counter.name,
            status=counter.status,
        )

    def as_dict(self) -> Mapping[str, object]:
        return MappingProxyType(
            {
                "counterId": str(self.counter_id),
                "name": self.name,
                "status": self.status.value,
            }
        )


__all__ = [
    "QueueCounterDto",
    "QueueDto",
    "QueueTicketDto",
]
