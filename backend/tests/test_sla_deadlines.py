"""SLA deadline calculator unit/service tests (TASK-023 / DEC-012 / API-314)."""

from __future__ import annotations

import uuid
from datetime import UTC, datetime, timedelta
from types import SimpleNamespace
from unittest.mock import MagicMock

import pytest

from app.core.enums import SlaStatus
from app.core.errors import ValidationAppError
from app.modules.sla.service import (
    DUPLICATE_SLA_MESSAGE,
    NO_ACTIVE_SLA_POLICY_MESSAGE,
    SlaService,
    calculate_deadlines,
)


def _policy_row(**overrides: object) -> SimpleNamespace:
    now = datetime.now(UTC)
    base = {
        "id": uuid.uuid4(),
        "name": "Standard SLA",
        "description": "Default targets",
        "assignment_target_minutes": 60,
        "appointment_target_minutes": 1440,
        "resolution_target_minutes": 2880,
        "escalation_target_minutes": 480,
        "overall_target_minutes": 4320,
        "is_active": True,
        "created_at": now,
        "updated_at": now,
    }
    base.update(overrides)
    return SimpleNamespace(**base)


def _sla_row(**overrides: object) -> SimpleNamespace:
    now = datetime.now(UTC)
    base = {
        "id": uuid.uuid4(),
        "complaint_id": uuid.uuid4(),
        "assignment_due_at": now + timedelta(minutes=60),
        "resolution_due_at": now + timedelta(minutes=2880),
        "appointment_due_at": now + timedelta(minutes=1440),
        "escalation_due_at": now + timedelta(minutes=480),
        "overall_due_at": now + timedelta(minutes=4320),
        "assignment_status": SlaStatus.PENDING,
        "resolution_status": SlaStatus.PENDING,
        "appointment_status": SlaStatus.PENDING,
        "escalation_status": SlaStatus.PENDING,
        "overall_status": SlaStatus.PENDING,
        "created_at": now,
        "updated_at": now,
    }
    base.update(overrides)
    return SimpleNamespace(**base)


def test_correct_deadline_calculation() -> None:
    created_at = datetime(2026, 7, 23, 5, 0, 0, tzinfo=UTC)
    deadlines = calculate_deadlines(
        created_at,
        assignment_target_minutes=60,
        appointment_target_minutes=120,
        resolution_target_minutes=240,
        escalation_target_minutes=90,
        overall_target_minutes=480,
    )
    assert deadlines["assignment_due_at"] == datetime(2026, 7, 23, 6, 0, 0, tzinfo=UTC)
    assert deadlines["appointment_due_at"] == datetime(2026, 7, 23, 7, 0, 0, tzinfo=UTC)
    assert deadlines["resolution_due_at"] == datetime(2026, 7, 23, 9, 0, 0, tzinfo=UTC)
    assert deadlines["escalation_due_at"] == datetime(2026, 7, 23, 6, 30, 0, tzinfo=UTC)
    assert deadlines["overall_due_at"] == datetime(2026, 7, 23, 13, 0, 0, tzinfo=UTC)


def test_complaint_creation_with_active_policy() -> None:
    complaint_id = uuid.uuid4()
    created_at = datetime(2026, 7, 23, 5, 0, 0, tzinfo=UTC)
    policy = _policy_row(
        assignment_target_minutes=30,
        appointment_target_minutes=120,
        resolution_target_minutes=240,
        escalation_target_minutes=90,
        overall_target_minutes=480,
    )
    created = _sla_row(
        complaint_id=complaint_id,
        created_at=created_at,
        assignment_due_at=created_at + timedelta(minutes=30),
        appointment_due_at=created_at + timedelta(minutes=120),
        resolution_due_at=created_at + timedelta(minutes=240),
        escalation_due_at=created_at + timedelta(minutes=90),
        overall_due_at=created_at + timedelta(minutes=480),
    )
    repo = MagicMock()
    repo.get_by_complaint_id.return_value = None
    repo.get_active_policy.return_value = policy
    repo.create_with_deadlines.return_value = created

    result = SlaService(repo).create_for_complaint(
        complaint_id, created_at=created_at
    )

    assert result.complaint_id == complaint_id
    assert result.assignment_status == SlaStatus.PENDING
    assert result.overall_status == SlaStatus.PENDING
    assert result.assignment_due_at == created_at + timedelta(minutes=30)
    assert result.overall_due_at == created_at + timedelta(minutes=480)
    repo.create_with_deadlines.assert_called_once()
    kwargs = repo.create_with_deadlines.call_args.kwargs
    assert kwargs["assignment_due_at"] == created_at + timedelta(minutes=30)
    assert kwargs["appointment_due_at"] == created_at + timedelta(minutes=120)
    assert kwargs["resolution_due_at"] == created_at + timedelta(minutes=240)
    assert kwargs["escalation_due_at"] == created_at + timedelta(minutes=90)
    assert kwargs["overall_due_at"] == created_at + timedelta(minutes=480)
    repo.commit.assert_not_called()


def test_reject_when_no_active_policy() -> None:
    repo = MagicMock()
    repo.get_by_complaint_id.return_value = None
    repo.get_active_policy.return_value = None

    with pytest.raises(ValidationAppError) as exc:
        SlaService(repo).create_for_complaint(
            uuid.uuid4(),
            created_at=datetime.now(UTC),
        )
    assert exc.value.message == NO_ACTIVE_SLA_POLICY_MESSAGE
    repo.create_with_deadlines.assert_not_called()


def test_sla_status_remains_pending() -> None:
    complaint_id = uuid.uuid4()
    created_at = datetime.now(UTC)
    created = _sla_row(complaint_id=complaint_id, created_at=created_at)
    repo = MagicMock()
    repo.get_by_complaint_id.return_value = None
    repo.get_active_policy.return_value = _policy_row()
    repo.create_with_deadlines.return_value = created

    result = SlaService(repo).create_for_complaint(
        complaint_id, created_at=created_at
    )

    assert result.assignment_status == "PENDING"
    assert result.appointment_status == "PENDING"
    assert result.resolution_status == "PENDING"
    assert result.escalation_status == "PENDING"
    assert result.overall_status == "PENDING"


def test_snapshot_unchanged_after_policy_activation_changes() -> None:
    """Activating a new policy must not touch existing SLA deadline rows."""
    existing_due = datetime(2026, 7, 23, 6, 0, 0, tzinfo=UTC)
    snapshot = _sla_row(assignment_due_at=existing_due)
    frozen_assignment = snapshot.assignment_due_at

    policy_b = _policy_row(name="Faster", is_active=False, assignment_target_minutes=15)
    repo = MagicMock()
    repo.get_policy.return_value = policy_b

    def _activate(row: SimpleNamespace, *, is_active: bool, now=None):
        _ = now
        row.is_active = is_active
        return row

    repo.set_policy_active.side_effect = _activate

    SlaService(repo).activate_policy(policy_b.id)

    # Snapshot object is untouched; activate path never writes sla_records.
    assert snapshot.assignment_due_at == frozen_assignment
    assert snapshot.assignment_due_at == existing_due
    repo.create_with_deadlines.assert_not_called()
    repo.create_pending.assert_not_called()


def test_duplicate_sla_rejected() -> None:
    complaint_id = uuid.uuid4()
    repo = MagicMock()
    repo.get_by_complaint_id.return_value = _sla_row(complaint_id=complaint_id)

    with pytest.raises(ValidationAppError) as exc:
        SlaService(repo).create_for_complaint(
            complaint_id,
            created_at=datetime.now(UTC),
        )
    assert exc.value.message == DUPLICATE_SLA_MESSAGE
    repo.get_active_policy.assert_not_called()
