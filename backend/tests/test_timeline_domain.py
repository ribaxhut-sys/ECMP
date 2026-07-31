"""CAPABILITY-010 — TimelineEntry domain entity tests."""

from __future__ import annotations

import uuid

import pytest

from app.core.errors import ValidationAppError
from app.modules.timeline.domain.entity import TimelineEntry
from app.modules.timeline.domain.enums import ActorType, AggregateType, TimelineEventType


def test_create_immutable_entry() -> None:
    entry = TimelineEntry.create(
        aggregate_type=AggregateType.COMPLAINT.value,
        aggregate_id=uuid.uuid4(),
        event_type=TimelineEventType.COMPLAINT_CREATED.value,
        title="Complaint created",
        description="CMP-1 opened",
        actor_type=ActorType.SYSTEM.value,
        metadata={"k": "v"},
    )
    assert entry.aggregate_type == "Complaint"
    assert entry.metadata["k"] == "v"
    assert entry.created_at.tzinfo is not None


def test_rejects_unknown_aggregate() -> None:
    with pytest.raises(ValidationAppError):
        TimelineEntry.create(
            aggregate_type="Invoice",
            aggregate_id=uuid.uuid4(),
            event_type="X",
            title="t",
        )


def test_rejects_blank_title_or_event() -> None:
    aid = uuid.uuid4()
    with pytest.raises(ValidationAppError):
        TimelineEntry.create(
            aggregate_type=AggregateType.QUEUE.value,
            aggregate_id=aid,
            event_type="  ",
            title="ok",
        )
    with pytest.raises(ValidationAppError):
        TimelineEntry.create(
            aggregate_type=AggregateType.NOTIFICATION.value,
            aggregate_id=aid,
            event_type="NotificationSent",
            title="   ",
        )


def test_frozen_dataclass_rejects_mutation() -> None:
    entry = TimelineEntry.create(
        aggregate_type=AggregateType.COMPLAINT.value,
        aggregate_id=uuid.uuid4(),
        event_type=TimelineEventType.COMPLAINT_ASSIGNED.value,
        title="Assigned",
    )
    with pytest.raises(Exception):
        entry.title = "changed"  # type: ignore[misc]
