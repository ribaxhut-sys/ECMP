"""Escalation Request unit/service tests (TASK-011)."""

from __future__ import annotations

import uuid
from datetime import UTC, datetime
from types import SimpleNamespace
from unittest.mock import MagicMock

import pytest

from app.core.errors import NotFoundError, ValidationAppError
from app.modules.escalations.schemas import EscalationRequestCreate
from app.modules.escalations.service import (
    HAS_ACTIVE_ESCALATION_MESSAGE,
    HAS_RESOLUTION_MESSAGE,
    NOT_IN_PROGRESS_MESSAGE,
    EscalationService,
)


def _complaint(**overrides: object) -> SimpleNamespace:
    now = datetime.now(UTC)
    base = {
        "id": uuid.uuid4(),
        "status": "IN_PROGRESS",
        "updated_at": now,
        "updated_by": None,
    }
    base.update(overrides)
    return SimpleNamespace(**base)


def test_request_escalation_success() -> None:
    actor = uuid.uuid4()
    complaint = _complaint(status="IN_PROGRESS")
    repo = MagicMock()
    repo.get_complaint.return_value = complaint
    repo.has_current_resolution.return_value = False
    repo.get_active_escalation.return_value = None
    repo.next_level.return_value = 1
    repo.add_escalation.side_effect = lambda e: setattr(e, "id", uuid.uuid4()) or e

    result = EscalationService(repo).request_escalation(
        complaint.id,
        EscalationRequestCreate(
            reasonCode="SPECIALIST_REQUIRED",
            reasonDescription="Requires Head Office specialist.",
            diagnosis="Branch troubleshooting completed.",
            notes="Customer visited branch twice.",
        ),
        actor_user_id=actor,
    )

    assert result.status == "REQUESTED"
    assert result.requested_by == actor
    assert complaint.status == "IN_PROGRESS"  # unchanged
    repo.add_timeline.assert_called_once()
    assert (
        repo.add_timeline.call_args.kwargs["event_type"]
        == "complaint.escalation_requested"
    )
    assert repo.add_timeline.call_args.kwargs["summary"] == "Escalation requested"
    repo.commit.assert_called_once()


def test_request_rejects_non_in_progress() -> None:
    complaint = _complaint(status="ASSIGNED")
    repo = MagicMock()
    repo.get_complaint.return_value = complaint

    with pytest.raises(ValidationAppError) as exc:
        EscalationService(repo).request_escalation(
            complaint.id,
            EscalationRequestCreate(
                reasonCode="SPECIALIST_REQUIRED",
                reasonDescription="x",
                diagnosis="y",
            ),
            actor_user_id=uuid.uuid4(),
        )
    assert exc.value.message == NOT_IN_PROGRESS_MESSAGE
    repo.commit.assert_not_called()


def test_request_rejects_when_resolution_exists() -> None:
    complaint = _complaint(status="IN_PROGRESS")
    repo = MagicMock()
    repo.get_complaint.return_value = complaint
    repo.has_current_resolution.return_value = True

    with pytest.raises(ValidationAppError) as exc:
        EscalationService(repo).request_escalation(
            complaint.id,
            EscalationRequestCreate(
                reasonCode="COMPLEX_CASE",
                reasonDescription="x",
                diagnosis="y",
            ),
            actor_user_id=uuid.uuid4(),
        )
    assert exc.value.message == HAS_RESOLUTION_MESSAGE
    repo.commit.assert_not_called()


def test_request_rejects_when_active_escalation_exists() -> None:
    complaint = _complaint(status="IN_PROGRESS")
    repo = MagicMock()
    repo.get_complaint.return_value = complaint
    repo.has_current_resolution.return_value = False
    repo.get_active_escalation.return_value = SimpleNamespace(
        id=uuid.uuid4(), status="REQUESTED"
    )

    with pytest.raises(ValidationAppError) as exc:
        EscalationService(repo).request_escalation(
            complaint.id,
            EscalationRequestCreate(
                reasonCode="OTHER",
                reasonDescription="x",
                diagnosis="y",
            ),
            actor_user_id=uuid.uuid4(),
        )
    assert exc.value.message == HAS_ACTIVE_ESCALATION_MESSAGE
    repo.commit.assert_not_called()


def test_get_escalation_not_found() -> None:
    repo = MagicMock()
    repo.get_by_id.return_value = None
    with pytest.raises(NotFoundError):
        EscalationService(repo).get_escalation(uuid.uuid4())
