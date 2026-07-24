"""Queue Domain Foundation value objects (TASK-061 / TASK-062 / TASK-063).

Core queue model + ticket lifecycle status.
Persistence-independent — no SQLAlchemy, no ORM, no repository imports.
No REST. No display/kiosk.
"""

from __future__ import annotations

import uuid
from dataclasses import dataclass
from datetime import datetime, timezone
from enum import StrEnum
from types import MappingProxyType
from typing import Mapping


class QueueStatus(StrEnum):
    """Operational status for Queue and QueueCounter."""

    OPEN = "OPEN"
    PAUSED = "PAUSED"
    CLOSED = "CLOSED"


class QueueTicketStatus(StrEnum):
    """Ticket lifecycle status (dedicated; not QueueStatus)."""

    WAITING = "WAITING"
    CALLED = "CALLED"
    SERVING = "SERVING"
    COMPLETED = "COMPLETED"
    CANCELLED = "CANCELLED"
    SKIPPED = "SKIPPED"


class QueuePriority(StrEnum):
    """Ticket priority classes."""

    NORMAL = "NORMAL"
    PRIORITY = "PRIORITY"
    VIP = "VIP"


class QueuePolicy(StrEnum):
    """Queue ordering policy. Foundation supports FIFO and Priority Queue only."""

    FIFO = "FIFO"
    PRIORITY_QUEUE = "PRIORITY_QUEUE"


def _require_non_empty(value: str, field_name: str) -> str:
    token = (value or "").strip()
    if not token:
        raise ValueError(f"{field_name} must be a non-empty string")
    return token


def _require_uuid(value: uuid.UUID, field_name: str) -> uuid.UUID:
    if not isinstance(value, uuid.UUID):
        raise TypeError(f"{field_name} must be uuid.UUID, got {type(value).__name__}")
    return value


def _ensure_utc(value: datetime) -> datetime:
    if not isinstance(value, datetime):
        raise TypeError(f"created_at must be datetime, got {type(value).__name__}")
    if value.tzinfo is None:
        return value.replace(tzinfo=timezone.utc)
    return value.astimezone(timezone.utc)


@dataclass(frozen=True, slots=True)
class Queue:
    """Queue aggregate root (foundation snapshot). No persistence / calling infra."""

    queue_id: uuid.UUID
    organization_id: uuid.UUID
    name: str
    description: str
    status: QueueStatus
    policy: QueuePolicy

    def __post_init__(self) -> None:
        _require_uuid(self.queue_id, "queue_id")
        _require_uuid(self.organization_id, "organization_id")
        object.__setattr__(self, "name", _require_non_empty(self.name, "name"))
        description = (self.description or "").strip()
        object.__setattr__(self, "description", description)
        if not isinstance(self.status, QueueStatus):
            raise TypeError(
                f"status must be QueueStatus, got {type(self.status).__name__}"
            )
        if not isinstance(self.policy, QueuePolicy):
            raise TypeError(
                f"policy must be QueuePolicy, got {type(self.policy).__name__}"
            )

    def as_dict(self) -> Mapping[str, object]:
        """Diagnostic serialization (not an HTTP / persistence contract)."""
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
class QueueTicket:
    """Immutable queue ticket. No calling / display integration."""

    ticket_id: uuid.UUID
    queue_id: uuid.UUID
    ticket_number: str
    priority: QueuePriority
    status: QueueTicketStatus
    created_at: datetime

    def __post_init__(self) -> None:
        _require_uuid(self.ticket_id, "ticket_id")
        _require_uuid(self.queue_id, "queue_id")
        object.__setattr__(
            self, "ticket_number", _require_non_empty(self.ticket_number, "ticket_number")
        )
        if not isinstance(self.priority, QueuePriority):
            raise TypeError(
                f"priority must be QueuePriority, got {type(self.priority).__name__}"
            )
        if not isinstance(self.status, QueueTicketStatus):
            raise TypeError(
                f"status must be QueueTicketStatus, got {type(self.status).__name__}"
            )
        object.__setattr__(self, "created_at", _ensure_utc(self.created_at))

    def as_dict(self) -> Mapping[str, object]:
        """Diagnostic serialization (not an HTTP / persistence contract)."""
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
class QueueCounter:
    """Service counter representation. No kiosk / display integration."""

    counter_id: uuid.UUID
    name: str
    status: QueueStatus

    def __post_init__(self) -> None:
        _require_uuid(self.counter_id, "counter_id")
        object.__setattr__(self, "name", _require_non_empty(self.name, "name"))
        if not isinstance(self.status, QueueStatus):
            raise TypeError(
                f"status must be QueueStatus, got {type(self.status).__name__}"
            )

    def as_dict(self) -> Mapping[str, object]:
        """Diagnostic serialization (not an HTTP / persistence contract)."""
        return MappingProxyType(
            {
                "counterId": str(self.counter_id),
                "name": self.name,
                "status": self.status.value,
            }
        )


__all__ = [
    "Queue",
    "QueueCounter",
    "QueuePolicy",
    "QueuePriority",
    "QueueStatus",
    "QueueTicket",
    "QueueTicketStatus",
]
