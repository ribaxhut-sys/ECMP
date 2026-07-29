"""Side-effect recorder — consumes Domain Events into Audit + Timeline + Outbox."""

from __future__ import annotations

import uuid
from typing import Protocol

from sqlalchemy.orm import Session

from app.modules.audit.repository import AuditRepository
from app.modules.audit.service import AuditService
from app.modules.cm_batch1.domain_events import DomainEvent
from app.modules.cm_batch1.outbox_repository import OutboxRepository
from app.modules.timeline.domain.entity import TimelineEntry
from app.modules.timeline.domain.enums import ActorType, AggregateType
from app.modules.timeline.repository import TimelineRepository

# Durable dedupe marker for domain events that have no EVT-CM catalog outbox row.
_NO_PUBLISH_EVENT_ID = "NO-PUBLISH"


class SideEffectRecorder(Protocol):
    def record(self, event: DomainEvent) -> bool:
        """Persist side effects for one domain event. Return False if skipped (idempotent)."""

    def record_many(self, events: list[DomainEvent]) -> int:
        """Record all events; return count of newly persisted events."""


class NoOpSideEffectRecorder:
    """Unit-test / in-memory path — no CAP tables required."""

    def record(self, event: DomainEvent) -> bool:
        _ = event
        return True

    def record_many(self, events: list[DomainEvent]) -> int:
        return len(events)


class CmBatch1SideEffectRecorder:
    """Shared pipeline: DomainEvent → Audit + Timeline + Outbox (same session)."""

    def __init__(
        self,
        session: Session,
        *,
        audit: AuditService | None = None,
        timeline: TimelineRepository | None = None,
        outbox: OutboxRepository | None = None,
    ) -> None:
        self._session = session
        self._audit = audit or AuditService(AuditRepository(session))
        self._timeline = timeline or TimelineRepository(session)
        self._outbox = outbox or OutboxRepository(session)

    def record(self, event: DomainEvent) -> bool:
        # Claim durable idempotency first so replay never duplicates Audit/Timeline/Outbox.
        outbox_id = event.outbox_event_id or _NO_PUBLISH_EVENT_ID
        claimed = self._outbox.enqueue(
            event_id=outbox_id,
            event_name=event.name,
            aggregate_type=event.aggregate_type,
            aggregate_id=event.aggregate_id,
            idempotency_key=event.idempotency_key,
            payload=event.payload,
            occurred_at=event.occurred_at,
        )
        if claimed is None:
            return False

        entity_uuid: uuid.UUID | None = None
        if event.aggregate_id:
            try:
                entity_uuid = uuid.UUID(event.aggregate_id)
            except ValueError:
                entity_uuid = None

        actor_uuid: uuid.UUID | None = None
        if event.actor_id:
            try:
                actor_uuid = uuid.UUID(event.actor_id)
            except ValueError:
                actor_uuid = None

        self._audit.log(
            event_type=event.audit_operation,
            entity_type=event.aggregate_type,
            action=event.audit_action,
            entity_id=entity_uuid,
            actor_id=actor_uuid,
            actor_name=None,
            old_values=event.before,
            new_values=event.after if event.after is not None else event.payload,
            metadata={
                "domainEvent": event.name,
                "idempotencyKey": event.idempotency_key,
                "outboxEventId": event.outbox_event_id,
            },
            commit=False,
        )

        if event.timeline_event_type and event.timeline_title and entity_uuid is not None:
            agg = event.aggregate_type
            if agg not in {a.value for a in AggregateType}:
                agg = AggregateType.COMPLAINT.value
            entry = TimelineEntry.create(
                aggregate_type=agg,
                aggregate_id=entity_uuid,
                event_type=event.timeline_event_type,
                title=event.timeline_title,
                description=event.timeline_description,
                actor_type=ActorType.USER.value if actor_uuid else ActorType.SYSTEM.value,
                actor_id=event.actor_id,
                metadata=event.timeline_metadata,
                created_at=event.occurred_at,
            )
            self._timeline.add(entry)

        self._session.flush()
        return True

    def record_many(self, events: list[DomainEvent]) -> int:
        count = 0
        for event in events:
            if self.record(event):
                count += 1
        return count


__all__ = [
    "SideEffectRecorder",
    "NoOpSideEffectRecorder",
    "CmBatch1SideEffectRecorder",
]
