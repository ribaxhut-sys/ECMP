"""SLA breach / status evaluation unit tests (TASK-024 / DEC-013)."""

from __future__ import annotations

import uuid
from datetime import UTC, datetime, timedelta
from types import SimpleNamespace
from unittest.mock import MagicMock

from app.core.enums import SlaStatus
from app.modules.sla.evaluation import (
    SlaCompletionFacts,
    evaluate_stage_status,
    evaluate_statuses,
)
from app.modules.sla.service import SlaService


def test_assignment_completed_before_due() -> None:
    due = datetime(2026, 7, 23, 12, 0, tzinfo=UTC)
    completed = datetime(2026, 7, 23, 11, 30, tzinfo=UTC)
    now = datetime(2026, 7, 23, 13, 0, tzinfo=UTC)
    assert (
        evaluate_stage_status(due_at=due, completed_at=completed, now=now)
        == SlaStatus.COMPLETED
    )


def test_assignment_breached() -> None:
    due = datetime(2026, 7, 23, 12, 0, tzinfo=UTC)
    now = datetime(2026, 7, 23, 12, 1, tzinfo=UTC)
    assert (
        evaluate_stage_status(due_at=due, completed_at=None, now=now)
        == SlaStatus.BREACHED
    )


def test_assignment_late_completion_breached() -> None:
    due = datetime(2026, 7, 23, 12, 0, tzinfo=UTC)
    completed = datetime(2026, 7, 23, 12, 30, tzinfo=UTC)
    now = datetime(2026, 7, 23, 13, 0, tzinfo=UTC)
    assert (
        evaluate_stage_status(due_at=due, completed_at=completed, now=now)
        == SlaStatus.BREACHED
    )


def test_resolution_completed_before_due() -> None:
    due = datetime(2026, 7, 24, 0, 0, tzinfo=UTC)
    completed = datetime(2026, 7, 23, 18, 0, tzinfo=UTC)
    assert (
        evaluate_stage_status(
            due_at=due, completed_at=completed, now=datetime(2026, 7, 25, tzinfo=UTC)
        )
        == SlaStatus.COMPLETED
    )


def test_resolution_breached() -> None:
    due = datetime(2026, 7, 23, 12, 0, tzinfo=UTC)
    assert (
        evaluate_stage_status(
            due_at=due,
            completed_at=None,
            now=datetime(2026, 7, 23, 15, 0, tzinfo=UTC),
        )
        == SlaStatus.BREACHED
    )


def test_appointment_completed_before_due() -> None:
    due = datetime(2026, 7, 23, 18, 0, tzinfo=UTC)
    completed = datetime(2026, 7, 23, 17, 0, tzinfo=UTC)
    assert (
        evaluate_stage_status(
            due_at=due, completed_at=completed, now=datetime(2026, 7, 24, tzinfo=UTC)
        )
        == SlaStatus.COMPLETED
    )


def test_appointment_breached() -> None:
    due = datetime(2026, 7, 23, 10, 0, tzinfo=UTC)
    assert (
        evaluate_stage_status(
            due_at=due,
            completed_at=None,
            now=datetime(2026, 7, 23, 11, 0, tzinfo=UTC),
        )
        == SlaStatus.BREACHED
    )


def test_escalation_completed_before_due() -> None:
    due = datetime(2026, 7, 23, 20, 0, tzinfo=UTC)
    completed = datetime(2026, 7, 23, 19, 0, tzinfo=UTC)
    assert (
        evaluate_stage_status(
            due_at=due, completed_at=completed, now=datetime(2026, 7, 24, tzinfo=UTC)
        )
        == SlaStatus.COMPLETED
    )


def test_escalation_breached() -> None:
    due = datetime(2026, 7, 23, 9, 0, tzinfo=UTC)
    assert (
        evaluate_stage_status(
            due_at=due,
            completed_at=None,
            now=datetime(2026, 7, 23, 10, 0, tzinfo=UTC),
        )
        == SlaStatus.BREACHED
    )


def test_overall_completed() -> None:
    due = datetime(2026, 7, 25, 0, 0, tzinfo=UTC)
    closed = datetime(2026, 7, 24, 12, 0, tzinfo=UTC)
    assert (
        evaluate_stage_status(
            due_at=due, completed_at=closed, now=datetime(2026, 7, 26, tzinfo=UTC)
        )
        == SlaStatus.COMPLETED
    )


def test_pending_before_due() -> None:
    due = datetime(2026, 7, 23, 12, 0, tzinfo=UTC)
    now = datetime(2026, 7, 23, 11, 59, tzinfo=UTC)
    assert (
        evaluate_stage_status(due_at=due, completed_at=None, now=now)
        == SlaStatus.PENDING
    )


def test_idempotent_evaluation() -> None:
    due = datetime(2026, 7, 23, 12, 0, tzinfo=UTC)
    facts = SlaCompletionFacts(
        assignment_completed_at=datetime(2026, 7, 23, 11, 0, tzinfo=UTC),
        overall_completed_at=None,
    )
    now = datetime(2026, 7, 23, 13, 0, tzinfo=UTC)
    first = evaluate_statuses(
        assignment_due_at=due,
        appointment_due_at=due + timedelta(hours=2),
        resolution_due_at=due + timedelta(hours=4),
        escalation_due_at=due + timedelta(hours=1),
        overall_due_at=due + timedelta(hours=8),
        facts=facts,
        now=now,
    )
    second = evaluate_statuses(
        assignment_due_at=due,
        appointment_due_at=due + timedelta(hours=2),
        resolution_due_at=due + timedelta(hours=4),
        escalation_due_at=due + timedelta(hours=1),
        overall_due_at=due + timedelta(hours=8),
        facts=facts,
        now=now,
    )
    assert first == second
    assert first.assignment_status == SlaStatus.COMPLETED
    # now = due+1h; appointment due = due+2h → still PENDING
    assert first.appointment_status == SlaStatus.PENDING
    # escalation due = due+1h and now <= due → PENDING (inclusive)
    assert first.escalation_status == SlaStatus.PENDING
    assert first.overall_status == SlaStatus.PENDING


def test_evaluate_for_complaint_updates_statuses_not_dues() -> None:
    complaint_id = uuid.uuid4()
    created = datetime(2026, 7, 23, 10, 0, tzinfo=UTC)
    due = created + timedelta(minutes=60)
    row = SimpleNamespace(
        id=uuid.uuid4(),
        complaint_id=complaint_id,
        assignment_due_at=due,
        appointment_due_at=due,
        resolution_due_at=due,
        escalation_due_at=due,
        overall_due_at=due,
        assignment_status=SlaStatus.PENDING,
        appointment_status=SlaStatus.PENDING,
        resolution_status=SlaStatus.PENDING,
        escalation_status=SlaStatus.PENDING,
        overall_status=SlaStatus.PENDING,
        created_at=created,
        updated_at=created,
    )
    repo = MagicMock()
    repo.get_by_complaint_id.return_value = row
    repo.load_completion_facts.return_value = SlaCompletionFacts(
        assignment_completed_at=created + timedelta(minutes=30),
    )

    def _update(r, **kwargs):
        for key, value in kwargs.items():
            if key != "now":
                setattr(r, key, value)
        return r

    repo.update_statuses.side_effect = _update

    now = created + timedelta(minutes=90)
    result = SlaService(repo).evaluate_for_complaint(complaint_id, now=now)

    assert result is not None
    assert result.assignment_status == SlaStatus.COMPLETED
    assert result.appointment_status == SlaStatus.BREACHED
    assert row.assignment_due_at == due
    assert row.overall_due_at == due
    repo.update_statuses.assert_called_once()
    # Policy must never be consulted during evaluation.
    repo.get_active_policy.assert_not_called()
    repo.get_policy.assert_not_called()
