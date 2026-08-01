"""CM Batch 1 Domain Events — business services emit these; SideEffectRecorder consumes."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import UTC, datetime
from typing import Any


@dataclass(frozen=True)
class DomainEvent:
    """Neutral domain event — no direct Audit/Timeline/Outbox dependency."""

    name: str
    aggregate_type: str
    aggregate_id: str | None
    actor_id: str | None
    payload: dict[str, Any]
    idempotency_key: str
    audit_operation: str
    audit_action: str = "CREATE"
    before: dict[str, Any] | None = None
    after: dict[str, Any] | None = None
    timeline_event_type: str | None = None
    timeline_title: str | None = None
    timeline_description: str | None = None
    outbox_event_id: str | None = None
    occurred_at: datetime = field(default_factory=lambda: datetime.now(UTC))
    # Justification / secrets stay out of timeline metadata.
    timeline_metadata: dict[str, Any] = field(default_factory=dict)
