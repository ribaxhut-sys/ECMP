"""Escalation Review unit/service tests (TASK-012)."""

from __future__ import annotations

import uuid
from datetime import UTC, datetime
from types import SimpleNamespace
from unittest.mock import MagicMock

import pytest

from app.core.errors import NotFoundError, ValidationAppError
from app.modules.escalations.schemas import EscalationReviewRequest
from app.modules.escalations.service import (
    ALREADY_REVIEWED_MESSAGE,
    NOT_REQUESTED_MESSAGE,
    EscalationService,
)


def _escalation(**overrides: object) -> SimpleNamespace:
    now = datetime.now(UTC)
    base = {
        "id": uuid.uuid4(),
        "complaint_id": uuid.uuid4(),
        "status": "REQUESTED",
        "reviewed_by": None,
        "reviewed_at": None,
        "review_notes": None,
        "updated_at": now,
        "updated_by": None,
    }
    base.update(overrides)
    return SimpleNamespace(**base)


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


def test_approve_requested_escalation() -> None:
    actor = uuid.uuid4()
    complaint = _complaint(status="IN_PROGRESS")
    row = _escalation(complaint_id=complaint.id, status="REQUESTED")
    repo = MagicMock()
    repo.get_by_id.return_value = row
    repo.get_complaint.return_value = complaint

    result = EscalationService(repo).approve(
        row.id,
        EscalationReviewRequest(reviewNotes="Approved for Head Office handling."),
        actor_user_id=actor,
    )

    assert result.status == "APPROVED"
    assert result.reviewed_by == actor
    assert row.status == "APPROVED"
    assert row.reviewed_by == actor
    assert row.review_notes == "Approved for Head Office handling."
    assert complaint.status == "IN_PROGRESS"
    repo.add_timeline.assert_called_once()
    assert (
        repo.add_timeline.call_args.kwargs["event_type"]
        == "complaint.escalation_approved"
    )
    assert repo.add_timeline.call_args.kwargs["summary"] == "Escalation approved"
    repo.commit.assert_called_once()


def test_reject_requested_escalation() -> None:
    actor = uuid.uuid4()
    complaint = _complaint(status="IN_PROGRESS")
    row = _escalation(complaint_id=complaint.id, status="REQUESTED")
    repo = MagicMock()
    repo.get_by_id.return_value = row
    repo.get_complaint.return_value = complaint

    result = EscalationService(repo).reject(
        row.id,
        EscalationReviewRequest(reviewNotes="Issue can be resolved by Branch."),
        actor_user_id=actor,
    )

    assert result.status == "REJECTED"
    assert result.reviewed_by == actor
    assert row.status == "REJECTED"
    assert complaint.status == "IN_PROGRESS"
    assert (
        repo.add_timeline.call_args.kwargs["event_type"]
        == "complaint.escalation_rejected"
    )
    assert repo.add_timeline.call_args.kwargs["summary"] == "Escalation rejected"


def test_reject_second_review_attempt() -> None:
    row = _escalation(status="APPROVED")
    repo = MagicMock()
    repo.get_by_id.return_value = row

    with pytest.raises(ValidationAppError) as exc:
        EscalationService(repo).approve(
            row.id,
            EscalationReviewRequest(reviewNotes="Second try"),
            actor_user_id=uuid.uuid4(),
        )
    assert exc.value.message == ALREADY_REVIEWED_MESSAGE
    repo.commit.assert_not_called()


def test_reject_review_of_rejected_escalation() -> None:
    row = _escalation(status="REJECTED")
    repo = MagicMock()
    repo.get_by_id.return_value = row

    with pytest.raises(ValidationAppError) as exc:
        EscalationService(repo).reject(
            row.id,
            EscalationReviewRequest(reviewNotes="Again"),
            actor_user_id=uuid.uuid4(),
        )
    assert exc.value.message == ALREADY_REVIEWED_MESSAGE
    repo.commit.assert_not_called()


def test_reject_review_of_open_legacy_escalation() -> None:
    row = _escalation(status="OPEN")
    repo = MagicMock()
    repo.get_by_id.return_value = row

    with pytest.raises(ValidationAppError) as exc:
        EscalationService(repo).approve(
            row.id,
            EscalationReviewRequest(reviewNotes="Legacy"),
            actor_user_id=uuid.uuid4(),
        )
    assert exc.value.message == NOT_REQUESTED_MESSAGE
    repo.commit.assert_not_called()


def test_approve_not_found() -> None:
    repo = MagicMock()
    repo.get_by_id.return_value = None

    with pytest.raises(NotFoundError):
        EscalationService(repo).approve(
            uuid.uuid4(),
            EscalationReviewRequest(reviewNotes="Missing"),
            actor_user_id=uuid.uuid4(),
        )
