"""CAPABILITY-010 — ActivityTimelineService unit tests."""

from __future__ import annotations

import uuid
from unittest.mock import MagicMock

import pytest

from app.core.errors import NotFoundError
from app.modules.timeline.domain.entity import TimelineEntry
from app.modules.timeline.domain.enums import AggregateType, TimelineEventType
from app.modules.timeline.schemas import TimelineEntryCreateRequest
from app.modules.timeline.service import ActivityTimelineService


def _entry(**overrides) -> TimelineEntry:
    base = dict(
        aggregate_type=AggregateType.COMPLAINT.value,
        aggregate_id=uuid.uuid4(),
        event_type=TimelineEventType.COMPLAINT_CREATED.value,
        title="Complaint created",
        description="desc",
        actor_type="SYSTEM",
        actor_id=None,
        actor_name=None,
        metadata={"a": 1},
    )
    base.update(overrides)
    return TimelineEntry.create(**base)


def test_create_persists_and_commits() -> None:
    repo = MagicMock()
    created = _entry()
    repo.add.return_value = created
    service = ActivityTimelineService(repo)
    payload = TimelineEntryCreateRequest(
        aggregateType=AggregateType.COMPLAINT.value,
        aggregateId=created.aggregate_id,
        eventType=created.event_type,
        title=created.title,
        description=created.description,
        metadata={"a": 1},
    )
    result = service.create(payload)
    assert result.event_type == created.event_type
    repo.add.assert_called_once()
    repo.commit.assert_called_once()


def test_get_not_found() -> None:
    repo = MagicMock()
    repo.get.return_value = None
    service = ActivityTimelineService(repo)
    with pytest.raises(NotFoundError):
        service.get(uuid.uuid4())


def test_list_returns_meta() -> None:
    repo = MagicMock()
    e1 = _entry()
    e2 = _entry(
        event_type=TimelineEventType.COMPLAINT_ASSIGNED.value,
        title="Assigned",
        aggregate_id=e1.aggregate_id,
    )
    repo.list.return_value = ([e1, e2], 2)
    service = ActivityTimelineService(repo)
    data, meta = service.list(page=1, page_size=10)
    assert len(data) == 2
    assert meta.total_items == 2
    assert meta.page == 1


def test_list_for_complaint_filters_aggregate() -> None:
    repo = MagicMock()
    cid = uuid.uuid4()
    repo.list.return_value = ([], 0)
    service = ActivityTimelineService(repo)
    service.list_for_complaint(cid, page=2, page_size=25)
    repo.list.assert_called_once_with(
        aggregate_type=AggregateType.COMPLAINT.value,
        aggregate_id=cid,
        event_type=None,
        page=2,
        page_size=25,
    )


def test_record_internal_path() -> None:
    repo = MagicMock()
    entry = _entry()
    repo.add.return_value = entry
    service = ActivityTimelineService(repo)
    result = service.record(
        aggregate_type=entry.aggregate_type,
        aggregate_id=entry.aggregate_id,
        event_type=entry.event_type,
        title=entry.title,
        commit=False,
    )
    assert result.title == entry.title
    repo.commit.assert_not_called()
