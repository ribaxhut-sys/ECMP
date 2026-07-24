"""Bidirectional Queue domain ↔ ORM mapping (TASK-063)."""

from __future__ import annotations

import uuid

from app.modules.queue.models import (
    Queue,
    QueueCounter,
    QueuePolicy,
    QueuePriority,
    QueueStatus,
    QueueTicket,
    QueueTicketStatus,
)
from app.modules.queue.orm.models import QueueCounterORM, QueueORM, QueueTicketORM


class QueueMapper:
    """Map Queue domain ↔ QueueORM."""

    @staticmethod
    def to_domain(row: QueueORM) -> Queue:
        return Queue(
            queue_id=row.queue_id,
            organization_id=row.organization_id,
            name=row.name,
            description=row.description or "",
            status=QueueStatus(row.status),
            policy=QueuePolicy(row.policy),
        )

    @staticmethod
    def to_orm(domain: Queue) -> QueueORM:
        return QueueORM(
            queue_id=domain.queue_id,
            organization_id=domain.organization_id,
            name=domain.name,
            description=domain.description,
            status=domain.status.value,
            policy=domain.policy.value,
        )

    @staticmethod
    def apply_to_orm(domain: Queue, row: QueueORM) -> QueueORM:
        """Copy domain fields onto an existing ORM row (no identity change)."""
        row.organization_id = domain.organization_id
        row.name = domain.name
        row.description = domain.description
        row.status = domain.status.value
        row.policy = domain.policy.value
        return row


class QueueTicketMapper:
    """Map QueueTicket domain ↔ QueueTicketORM."""

    @staticmethod
    def to_domain(row: QueueTicketORM) -> QueueTicket:
        return QueueTicket(
            ticket_id=row.ticket_id,
            queue_id=row.queue_id,
            ticket_number=row.ticket_number,
            priority=QueuePriority(row.priority),
            status=QueueTicketStatus(row.status),
            created_at=row.created_at,
        )

    @staticmethod
    def to_orm(domain: QueueTicket) -> QueueTicketORM:
        return QueueTicketORM(
            ticket_id=domain.ticket_id,
            queue_id=domain.queue_id,
            ticket_number=domain.ticket_number,
            priority=domain.priority.value,
            status=domain.status.value,
            created_at=domain.created_at,
        )

    @staticmethod
    def apply_to_orm(domain: QueueTicket, row: QueueTicketORM) -> QueueTicketORM:
        row.queue_id = domain.queue_id
        row.ticket_number = domain.ticket_number
        row.priority = domain.priority.value
        row.status = domain.status.value
        row.created_at = domain.created_at
        return row


class QueueCounterMapper:
    """Map QueueCounter domain ↔ QueueCounterORM.

    ``queue_id`` is a persistence association not present on the domain VO.
    """

    @staticmethod
    def to_domain(row: QueueCounterORM) -> QueueCounter:
        return QueueCounter(
            counter_id=row.counter_id,
            name=row.name,
            status=QueueStatus(row.status),
        )

    @staticmethod
    def to_orm(queue_id: uuid.UUID, domain: QueueCounter) -> QueueCounterORM:
        return QueueCounterORM(
            counter_id=domain.counter_id,
            queue_id=queue_id,
            name=domain.name,
            status=domain.status.value,
        )

    @staticmethod
    def apply_to_orm(
        queue_id: uuid.UUID, domain: QueueCounter, row: QueueCounterORM
    ) -> QueueCounterORM:
        row.queue_id = queue_id
        row.name = domain.name
        row.status = domain.status.value
        return row


__all__ = [
    "QueueCounterMapper",
    "QueueMapper",
    "QueueTicketMapper",
]
