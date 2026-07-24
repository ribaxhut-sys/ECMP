"""ComplaintEventFactory — standardized in-memory event creation (TASK-045).

No Kafka / RabbitMQ / Redis Streams / Pub-Sub.
No event store / database table.
"""

from __future__ import annotations

import uuid
from datetime import UTC, datetime
from types import MappingProxyType
from typing import Any, Mapping

from app.modules.complaint_events.models import (
    ComplaintEvent,
    ComplaintEventType,
    EventSourceRef,
    EventTargetRef,
)
from app.modules.routing import ComplaintRoute


def context_ref_for(complaint_id: uuid.UUID) -> str:
    """Stable reference key for future ComplaintContext consumers."""
    return f"complaint:{complaint_id}"


class ComplaintEventFactory:
    """Creates immutable ComplaintEvent instances for lifecycle transitions."""

    @staticmethod
    def _freeze_payload(payload: Mapping[str, Any] | None) -> Mapping[str, Any]:
        return MappingProxyType(dict(payload or {}))

    @classmethod
    def _build(
        cls,
        event_type: ComplaintEventType,
        *,
        complaint_id: uuid.UUID,
        complaint_number: str,
        current_status: str,
        priority: str,
        source: EventSourceRef,
        target: EventTargetRef,
        routing: ComplaintRoute | None = None,
        context_reference: str | None = None,
        payload: Mapping[str, Any] | None = None,
        occurred_at: datetime | None = None,
        event_id: uuid.UUID | None = None,
    ) -> ComplaintEvent:
        occurred = occurred_at or datetime.now(UTC)
        if occurred.tzinfo is None:
            occurred = occurred.replace(tzinfo=UTC)
        return ComplaintEvent(
            event_id=event_id or uuid.uuid4(),
            event_type=event_type,
            occurred_at=occurred,
            complaint_id=complaint_id,
            complaint_number=complaint_number,
            current_status=current_status,
            priority=priority,
            source=source,
            target=target,
            routing=routing,
            context_reference=context_reference
            if context_reference is not None
            else context_ref_for(complaint_id),
            payload=cls._freeze_payload(payload),
        )

    @classmethod
    def create_created(
        cls,
        *,
        complaint_id: uuid.UUID,
        complaint_number: str,
        current_status: str,
        priority: str,
        source: EventSourceRef,
        target: EventTargetRef,
        routing: ComplaintRoute | None = None,
        context_reference: str | None = None,
        payload: Mapping[str, Any] | None = None,
        occurred_at: datetime | None = None,
        event_id: uuid.UUID | None = None,
    ) -> ComplaintEvent:
        return cls._build(
            ComplaintEventType.CREATED,
            complaint_id=complaint_id,
            complaint_number=complaint_number,
            current_status=current_status,
            priority=priority,
            source=source,
            target=target,
            routing=routing,
            context_reference=context_reference,
            payload=payload,
            occurred_at=occurred_at,
            event_id=event_id,
        )

    @classmethod
    def create_assigned(
        cls,
        *,
        complaint_id: uuid.UUID,
        complaint_number: str,
        current_status: str,
        priority: str,
        source: EventSourceRef,
        target: EventTargetRef,
        routing: ComplaintRoute | None = None,
        context_reference: str | None = None,
        payload: Mapping[str, Any] | None = None,
        occurred_at: datetime | None = None,
        event_id: uuid.UUID | None = None,
    ) -> ComplaintEvent:
        return cls._build(
            ComplaintEventType.ASSIGNED,
            complaint_id=complaint_id,
            complaint_number=complaint_number,
            current_status=current_status,
            priority=priority,
            source=source,
            target=target,
            routing=routing,
            context_reference=context_reference,
            payload=payload,
            occurred_at=occurred_at,
            event_id=event_id,
        )

    @classmethod
    def create_accepted(
        cls,
        *,
        complaint_id: uuid.UUID,
        complaint_number: str,
        current_status: str,
        priority: str,
        source: EventSourceRef,
        target: EventTargetRef,
        routing: ComplaintRoute | None = None,
        context_reference: str | None = None,
        payload: Mapping[str, Any] | None = None,
        occurred_at: datetime | None = None,
        event_id: uuid.UUID | None = None,
    ) -> ComplaintEvent:
        return cls._build(
            ComplaintEventType.ACCEPTED,
            complaint_id=complaint_id,
            complaint_number=complaint_number,
            current_status=current_status,
            priority=priority,
            source=source,
            target=target,
            routing=routing,
            context_reference=context_reference,
            payload=payload,
            occurred_at=occurred_at,
            event_id=event_id,
        )

    @classmethod
    def create_in_progress(
        cls,
        *,
        complaint_id: uuid.UUID,
        complaint_number: str,
        current_status: str,
        priority: str,
        source: EventSourceRef,
        target: EventTargetRef,
        routing: ComplaintRoute | None = None,
        context_reference: str | None = None,
        payload: Mapping[str, Any] | None = None,
        occurred_at: datetime | None = None,
        event_id: uuid.UUID | None = None,
    ) -> ComplaintEvent:
        return cls._build(
            ComplaintEventType.IN_PROGRESS,
            complaint_id=complaint_id,
            complaint_number=complaint_number,
            current_status=current_status,
            priority=priority,
            source=source,
            target=target,
            routing=routing,
            context_reference=context_reference,
            payload=payload,
            occurred_at=occurred_at,
            event_id=event_id,
        )

    @classmethod
    def create_resolved(
        cls,
        *,
        complaint_id: uuid.UUID,
        complaint_number: str,
        current_status: str,
        priority: str,
        source: EventSourceRef,
        target: EventTargetRef,
        routing: ComplaintRoute | None = None,
        context_reference: str | None = None,
        payload: Mapping[str, Any] | None = None,
        occurred_at: datetime | None = None,
        event_id: uuid.UUID | None = None,
    ) -> ComplaintEvent:
        return cls._build(
            ComplaintEventType.RESOLVED,
            complaint_id=complaint_id,
            complaint_number=complaint_number,
            current_status=current_status,
            priority=priority,
            source=source,
            target=target,
            routing=routing,
            context_reference=context_reference,
            payload=payload,
            occurred_at=occurred_at,
            event_id=event_id,
        )

    @classmethod
    def create_closed(
        cls,
        *,
        complaint_id: uuid.UUID,
        complaint_number: str,
        current_status: str,
        priority: str,
        source: EventSourceRef,
        target: EventTargetRef,
        routing: ComplaintRoute | None = None,
        context_reference: str | None = None,
        payload: Mapping[str, Any] | None = None,
        occurred_at: datetime | None = None,
        event_id: uuid.UUID | None = None,
    ) -> ComplaintEvent:
        return cls._build(
            ComplaintEventType.CLOSED,
            complaint_id=complaint_id,
            complaint_number=complaint_number,
            current_status=current_status,
            priority=priority,
            source=source,
            target=target,
            routing=routing,
            context_reference=context_reference,
            payload=payload,
            occurred_at=occurred_at,
            event_id=event_id,
        )

    @classmethod
    def create_escalated(
        cls,
        *,
        complaint_id: uuid.UUID,
        complaint_number: str,
        current_status: str,
        priority: str,
        source: EventSourceRef,
        target: EventTargetRef,
        routing: ComplaintRoute | None = None,
        context_reference: str | None = None,
        payload: Mapping[str, Any] | None = None,
        occurred_at: datetime | None = None,
        event_id: uuid.UUID | None = None,
    ) -> ComplaintEvent:
        return cls._build(
            ComplaintEventType.ESCALATED,
            complaint_id=complaint_id,
            complaint_number=complaint_number,
            current_status=current_status,
            priority=priority,
            source=source,
            target=target,
            routing=routing,
            context_reference=context_reference,
            payload=payload,
            occurred_at=occurred_at,
            event_id=event_id,
        )
