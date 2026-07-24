"""SLA timeline integration unit tests (TASK-025 / DEC-014)."""

from __future__ import annotations

import uuid
from datetime import UTC, datetime, timedelta
from types import SimpleNamespace
from unittest.mock import MagicMock

from app.core.enums import SlaStatus, TimelineEvent
from app.modules.sla.evaluation import SlaCompletionFacts
from app.modules.sla.service import SlaService
from app.modules.sla.timeline import timeline_event_for_transition, timeline_summary


def _sla_row(**overrides: object) -> SimpleNamespace:
    created = datetime(2026, 7, 23, 10, 0, tzinfo=UTC)
    due = created + timedelta(minutes=60)
    base = {
        "id": uuid.uuid4(),
        "complaint_id": uuid.uuid4(),
        "assignment_due_at": due,
        "appointment_due_at": due,
        "resolution_due_at": due,
        "escalation_due_at": due,
        "overall_due_at": due,
        "assignment_status": SlaStatus.PENDING,
        "appointment_status": SlaStatus.PENDING,
        "resolution_status": SlaStatus.PENDING,
        "escalation_status": SlaStatus.PENDING,
        "overall_status": SlaStatus.PENDING,
        "created_at": created,
        "updated_at": created,
    }
    base.update(overrides)
    return SimpleNamespace(**base)


def test_timeline_event_for_completed_transition() -> None:
    assert (
        timeline_event_for_transition(
            stage="assignment",
            old_status=SlaStatus.PENDING,
            new_status=SlaStatus.COMPLETED,
        )
        == TimelineEvent.SLA_ASSIGNMENT_COMPLETED
    )
    assert (
        timeline_summary(TimelineEvent.SLA_ASSIGNMENT_COMPLETED)
        == "SLA Assignment Completed"
    )


def test_timeline_event_for_breached_transition() -> None:
    assert (
        timeline_event_for_transition(
            stage="resolution",
            old_status=SlaStatus.PENDING,
            new_status=SlaStatus.BREACHED,
        )
        == TimelineEvent.SLA_RESOLUTION_BREACHED
    )


def test_no_timeline_event_when_status_unchanged() -> None:
    assert (
        timeline_event_for_transition(
            stage="assignment",
            old_status=SlaStatus.COMPLETED,
            new_status=SlaStatus.COMPLETED,
        )
        is None
    )
    assert (
        timeline_event_for_transition(
            stage="overall",
            old_status=SlaStatus.BREACHED,
            new_status=SlaStatus.BREACHED,
        )
        is None
    )


def test_timeline_created_once_on_completed() -> None:
    complaint_id = uuid.uuid4()
    created = datetime(2026, 7, 23, 10, 0, tzinfo=UTC)
    due = created + timedelta(minutes=60)
    row = _sla_row(complaint_id=complaint_id, assignment_due_at=due)
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

    now = created + timedelta(minutes=45)
    SlaService(repo).evaluate_for_complaint(complaint_id, now=now)

    repo.add_timeline.assert_called_once()
    kwargs = repo.add_timeline.call_args.kwargs
    assert kwargs["event_type"] == TimelineEvent.SLA_ASSIGNMENT_COMPLETED.value
    assert kwargs["summary"] == "SLA Assignment Completed"
    assert kwargs["metadata"]["actor"] == "SYSTEM"
    assert kwargs["metadata"]["oldStatus"] == SlaStatus.PENDING
    assert kwargs["metadata"]["newStatus"] == SlaStatus.COMPLETED
    assert kwargs["metadata"]["slaStage"] == "assignment"


def test_timeline_created_once_on_breached() -> None:
    complaint_id = uuid.uuid4()
    created = datetime(2026, 7, 23, 10, 0, tzinfo=UTC)
    due = created + timedelta(minutes=60)
    row = _sla_row(complaint_id=complaint_id, assignment_due_at=due)
    repo = MagicMock()
    repo.get_by_complaint_id.return_value = row
    repo.load_completion_facts.return_value = SlaCompletionFacts()

    def _update(r, **kwargs):
        for key, value in kwargs.items():
            if key != "now":
                setattr(r, key, value)
        return r

    repo.update_statuses.side_effect = _update

    now = due + timedelta(minutes=1)
    SlaService(repo).evaluate_for_complaint(complaint_id, now=now)

    breached_calls = [
        c
        for c in repo.add_timeline.call_args_list
        if c.kwargs["event_type"].endswith(".breached")
    ]
    assert len(breached_calls) >= 1
    assert any(
        c.kwargs["event_type"] == TimelineEvent.SLA_ASSIGNMENT_BREACHED.value
        for c in breached_calls
    )


def test_overall_timeline_event() -> None:
    assert (
        timeline_event_for_transition(
            stage="overall",
            old_status="PENDING",
            new_status="COMPLETED",
        )
        == TimelineEvent.SLA_OVERALL_COMPLETED
    )
    assert (
        timeline_summary(TimelineEvent.SLA_OVERALL_COMPLETED)
        == "SLA Overall Completed"
    )


def test_duplicate_evaluations_produce_no_duplicate_events() -> None:
    complaint_id = uuid.uuid4()
    created = datetime(2026, 7, 23, 10, 0, tzinfo=UTC)
    due = created + timedelta(minutes=60)
    row = _sla_row(
        complaint_id=complaint_id,
        assignment_due_at=due,
        assignment_status=SlaStatus.COMPLETED,
        appointment_status=SlaStatus.BREACHED,
        resolution_status=SlaStatus.BREACHED,
        escalation_status=SlaStatus.BREACHED,
        overall_status=SlaStatus.BREACHED,
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

    now = due + timedelta(hours=1)
    service = SlaService(repo)
    service.evaluate_for_complaint(complaint_id, now=now)
    service.evaluate_for_complaint(complaint_id, now=now)

    repo.add_timeline.assert_not_called()
