"""Complaint resolution unit/service tests (TASK-010)."""

from __future__ import annotations

import uuid
from datetime import UTC, datetime
from types import SimpleNamespace
from unittest.mock import MagicMock

import pytest

from app.core.enums import ComplaintStatus
from app.core.errors import NotFoundError, ValidationAppError
from app.core.status_transitions import can_transition
from app.modules.resolutions.schemas import ResolveComplaintRequest
from app.modules.resolutions.service import (
    NOT_IN_PROGRESS_MESSAGE,
    ResolutionService,
)


def _complaint(**overrides: object) -> SimpleNamespace:
    now = datetime.now(UTC)
    actor_id = uuid.uuid4()
    base = {
        "id": uuid.uuid4(),
        "complaint_number": "CMP-TEST",
        "status": "IN_PROGRESS",
        "updated_at": now,
        "updated_by": actor_id,
    }
    base.update(overrides)
    return SimpleNamespace(**base)


def test_matrix_blocks_direct_resolved_via_status() -> None:
    assert can_transition(ComplaintStatus.IN_PROGRESS, ComplaintStatus.PENDING)
    assert not can_transition(ComplaintStatus.IN_PROGRESS, ComplaintStatus.RESOLVED)
    assert not can_transition(ComplaintStatus.PENDING, ComplaintStatus.RESOLVED)
    assert can_transition(ComplaintStatus.RESOLVED, ComplaintStatus.CLOSED)


def test_resolve_success_sets_resolved_and_timeline(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    actor_id = uuid.uuid4()
    complaint = _complaint(status="IN_PROGRESS")
    resolver = SimpleNamespace(id=actor_id, full_name="Agent One")

    repo = MagicMock()
    repo.get_complaint.return_value = complaint
    repo.get_user.return_value = resolver
    repo.get_current_resolution.return_value = None
    repo.add_resolution.side_effect = lambda r: setattr(r, "id", uuid.uuid4()) or r
    monkeypatch.setattr(
        "app.modules.sla.hooks.evaluate_sla_for_complaint",
        lambda *args, **kwargs: None,
    )

    result = ResolutionService(repo).resolve(
        complaint.id,
        ResolveComplaintRequest(
            resolutionCategory="SOLVED",
            rootCause="Configuration Error",
            resolutionNotes="Restarted service and updated configuration.",
            resolvedBy=actor_id,
        ),
        actor_user_id=actor_id,
    )

    assert result.status == ComplaintStatus.RESOLVED
    assert complaint.status == ComplaintStatus.RESOLVED
    assert result.resolution.resolution_category == "SOLVED"
    assert result.resolution.resolved_by_name == "Agent One"
    repo.add_timeline.assert_called_once()
    assert repo.add_timeline.call_args.kwargs["event_type"] == "complaint.resolved"
    assert repo.add_timeline.call_args.kwargs["summary"] == "Complaint resolved"
    assert repo.add_timeline.call_args.kwargs["from_status"] == "IN_PROGRESS"
    assert repo.add_timeline.call_args.kwargs["to_status"] == "RESOLVED"
    repo.commit.assert_called_once()


def test_resolve_rejects_non_in_progress() -> None:
    complaint = _complaint(status="ASSIGNED")
    repo = MagicMock()
    repo.get_complaint.return_value = complaint

    with pytest.raises(ValidationAppError) as exc:
        ResolutionService(repo).resolve(
            complaint.id,
            ResolveComplaintRequest(
                resolutionCategory="SOLVED",
                rootCause="x",
                resolutionNotes="y",
            ),
            actor_user_id=uuid.uuid4(),
        )
    assert exc.value.message == NOT_IN_PROGRESS_MESSAGE
    assert exc.value.status_code == 400
    repo.add_timeline.assert_not_called()
    repo.commit.assert_not_called()


def test_resolve_not_found() -> None:
    repo = MagicMock()
    repo.get_complaint.return_value = None
    with pytest.raises(NotFoundError):
        ResolutionService(repo).resolve(
            uuid.uuid4(),
            ResolveComplaintRequest(
                resolutionCategory="WORKAROUND",
                rootCause="x",
                resolutionNotes="y",
            ),
            actor_user_id=uuid.uuid4(),
        )


def test_resolve_rejects_mismatched_resolved_by() -> None:
    actor_id = uuid.uuid4()
    other_id = uuid.uuid4()
    complaint = _complaint(status="IN_PROGRESS")
    repo = MagicMock()
    repo.get_complaint.return_value = complaint

    with pytest.raises(ValidationAppError) as exc:
        ResolutionService(repo).resolve(
            complaint.id,
            ResolveComplaintRequest(
                resolutionCategory="SOLVED",
                rootCause="x",
                resolutionNotes="y",
                resolvedBy=other_id,
            ),
            actor_user_id=actor_id,
        )
    assert "resolvedBy harus sesuai" in exc.value.message
    repo.commit.assert_not_called()


def test_get_current_returns_none_when_missing() -> None:
    complaint = _complaint()
    repo = MagicMock()
    repo.get_complaint.return_value = complaint
    repo.get_current_resolution.return_value = None
    assert ResolutionService(repo).get_current(complaint.id) is None
