"""Timeline service unit tests."""

from __future__ import annotations

import uuid
from datetime import UTC, datetime, timedelta
from types import SimpleNamespace
from unittest.mock import MagicMock

import pytest

from app.core.enums import TimelineEvent
from app.core.errors import NotFoundError
from app.modules.timelines.service import TimelineService


def test_list_timeline_complaint_not_found() -> None:
    repo = MagicMock()
    repo.get_complaint.return_value = None
    service = TimelineService(repo)

    with pytest.raises(NotFoundError):
        service.list_timeline(uuid.uuid4())
    repo.list_by_complaint.assert_not_called()


def test_list_timeline_empty() -> None:
    complaint_id = uuid.uuid4()
    repo = MagicMock()
    repo.get_complaint.return_value = SimpleNamespace(id=complaint_id)
    repo.list_by_complaint.return_value = []

    result = TimelineService(repo).list_timeline(complaint_id)

    assert result == []
    repo.list_by_complaint.assert_called_once_with(complaint_id)


def test_list_timeline_maps_entries_created_at_order() -> None:
    complaint_id = uuid.uuid4()
    actor_id = uuid.uuid4()
    t0 = datetime(2026, 7, 23, 1, 0, tzinfo=UTC)
    t1 = t0 + timedelta(minutes=5)

    rows = [
        SimpleNamespace(
            id=uuid.uuid4(),
            complaint_id=complaint_id,
            actor_user_id=actor_id,
            event_type=TimelineEvent.ASSIGNED,
            event_at=t0,
            from_status="NEW",
            to_status="ASSIGNED",
            summary="Assigned",
            metadata_json={"assigneeId": str(actor_id)},
            created_at=t0,
        ),
        SimpleNamespace(
            id=uuid.uuid4(),
            complaint_id=complaint_id,
            actor_user_id=actor_id,
            event_type=TimelineEvent.ESCALATED,
            event_at=t1,
            from_status="ASSIGNED",
            to_status="ESCALATED",
            summary="Escalated",
            metadata_json=None,
            created_at=t1,
        ),
    ]

    repo = MagicMock()
    repo.get_complaint.return_value = SimpleNamespace(id=complaint_id)
    repo.list_by_complaint.return_value = rows

    result = TimelineService(repo).list_timeline(complaint_id)

    assert len(result) == 2
    assert result[0].event_type == TimelineEvent.ASSIGNED
    assert result[0].created_at == t0
    assert result[0].metadata == {"assigneeId": str(actor_id)}
    assert result[1].event_type == TimelineEvent.ESCALATED
    assert result[1].metadata is None
