"""Status transition unit tests (TASK-009)."""

from __future__ import annotations

import uuid
from datetime import UTC, datetime
from types import SimpleNamespace
from unittest.mock import MagicMock

import pytest

from app.core.enums import ComplaintStatus
from app.core.errors import NotFoundError, ValidationAppError
from app.core.status_transitions import can_transition
from app.modules.complaints.schemas import ComplaintStatusChangeRequest
from app.modules.complaints.service import ComplaintService


def _complaint(**overrides: object) -> SimpleNamespace:
    now = datetime.now(UTC)
    actor_id = uuid.uuid4()
    base = {
        "id": uuid.uuid4(),
        "complaint_number": "CMP-TEST",
        "customer_id": uuid.uuid4(),
        "branch_id": None,
        "subject": "s",
        "description": "d",
        "status": "ASSIGNED",
        "priority": "MEDIUM",
        "channel": None,
        "category": None,
        "reported_at": now,
        "closed_at": None,
        "created_at": now,
        "created_by": actor_id,
        "updated_at": now,
        "updated_by": actor_id,
    }
    base.update(overrides)
    return SimpleNamespace(**base)


def test_matrix_allowed_and_blocked() -> None:
    assert can_transition(ComplaintStatus.ASSIGNED, ComplaintStatus.IN_PROGRESS)
    assert can_transition(ComplaintStatus.IN_PROGRESS, ComplaintStatus.PENDING)
    assert can_transition(ComplaintStatus.IN_PROGRESS, ComplaintStatus.RESOLVED)
    assert can_transition(ComplaintStatus.PENDING, ComplaintStatus.IN_PROGRESS)
    assert can_transition(ComplaintStatus.PENDING, ComplaintStatus.RESOLVED)
    assert can_transition(ComplaintStatus.RESOLVED, ComplaintStatus.CLOSED)
    assert can_transition(ComplaintStatus.RESOLVED, ComplaintStatus.IN_PROGRESS)
    assert not can_transition(ComplaintStatus.NEW, ComplaintStatus.RESOLVED)
    assert not can_transition(ComplaintStatus.NEW, ComplaintStatus.ASSIGNED)
    assert not can_transition(ComplaintStatus.CLOSED, ComplaintStatus.IN_PROGRESS)
    assert not can_transition(ComplaintStatus.ASSIGNED, ComplaintStatus.RESOLVED)


def test_change_status_success_writes_timeline() -> None:
    actor_id = uuid.uuid4()
    complaint = _complaint(status="ASSIGNED")
    repo = MagicMock()
    repo.get_by_id.return_value = complaint
    repo.refresh.side_effect = lambda c: c

    result = ComplaintService(repo).change_status(
        complaint.id,
        ComplaintStatusChangeRequest(status=ComplaintStatus.IN_PROGRESS),
        actor_user_id=actor_id,
    )

    assert result.status == ComplaintStatus.IN_PROGRESS
    assert complaint.status == ComplaintStatus.IN_PROGRESS
    repo.add_timeline.assert_called_once()
    assert repo.add_timeline.call_args.kwargs["from_status"] == "ASSIGNED"
    assert repo.add_timeline.call_args.kwargs["to_status"] == "IN_PROGRESS"
    assert (
        repo.add_timeline.call_args.kwargs["metadata"]["changeType"]
        == "STATUS_CHANGED"
    )
    repo.commit.assert_called_once()


def test_change_status_invalid_returns_400_validation() -> None:
    complaint = _complaint(status="NEW")
    repo = MagicMock()
    repo.get_by_id.return_value = complaint

    with pytest.raises(ValidationAppError) as exc:
        ComplaintService(repo).change_status(
            complaint.id,
            ComplaintStatusChangeRequest(status=ComplaintStatus.RESOLVED),
            actor_user_id=uuid.uuid4(),
        )
    assert "Invalid status transition" in exc.value.message
    assert exc.value.status_code == 400
    repo.add_timeline.assert_not_called()
    repo.commit.assert_not_called()


def test_change_status_not_found() -> None:
    repo = MagicMock()
    repo.get_by_id.return_value = None
    with pytest.raises(NotFoundError):
        ComplaintService(repo).change_status(
            uuid.uuid4(),
            ComplaintStatusChangeRequest(status=ComplaintStatus.IN_PROGRESS),
            actor_user_id=uuid.uuid4(),
        )


def test_close_sets_closed_at_and_reopen_clears() -> None:
    actor_id = uuid.uuid4()
    complaint = _complaint(status="RESOLVED", closed_at=None)
    repo = MagicMock()
    repo.get_by_id.return_value = complaint
    repo.refresh.side_effect = lambda c: c
    service = ComplaintService(repo)

    service.change_status(
        complaint.id,
        ComplaintStatusChangeRequest(status=ComplaintStatus.CLOSED),
        actor_user_id=actor_id,
    )
    assert complaint.status == ComplaintStatus.CLOSED
    assert complaint.closed_at is not None

    # Reset to RESOLVED to exercise reopen (CLOSED has no outbound transitions).
    complaint.status = ComplaintStatus.RESOLVED
    service.change_status(
        complaint.id,
        ComplaintStatusChangeRequest(status=ComplaintStatus.IN_PROGRESS),
        actor_user_id=actor_id,
    )
    assert complaint.status == ComplaintStatus.IN_PROGRESS
    assert complaint.closed_at is None
