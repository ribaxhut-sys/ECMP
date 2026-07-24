"""SLA domain foundation unit/service tests (TASK-021 / API-314)."""

from __future__ import annotations

import uuid
from datetime import UTC, datetime
from types import SimpleNamespace
from unittest.mock import MagicMock

import pytest

from app.core.enums import SlaStatus
from app.core.errors import NotFoundError, ValidationAppError
from app.modules.sla.service import (
    COMPLAINT_DELETE_RESTRICTED_MESSAGE,
    DUPLICATE_SLA_MESSAGE,
    SlaService,
)


def _sla_row(**overrides: object) -> SimpleNamespace:
    now = datetime.now(UTC)
    base = {
        "id": uuid.uuid4(),
        "complaint_id": uuid.uuid4(),
        "assignment_due_at": None,
        "resolution_due_at": None,
        "appointment_due_at": None,
        "escalation_due_at": None,
        "overall_due_at": None,
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


def test_sla_record_retrieval() -> None:
    complaint_id = uuid.uuid4()
    row = _sla_row(complaint_id=complaint_id)
    repo = MagicMock()
    repo.get_complaint.return_value = SimpleNamespace(id=complaint_id)
    repo.get_by_complaint_id.return_value = row
    repo.load_completion_facts.return_value = SimpleNamespace(
        assignment_completed_at=None,
        appointment_completed_at=None,
        resolution_completed_at=None,
        escalation_completed_at=None,
        overall_completed_at=None,
    )

    def _update(r, **kwargs):
        for key, value in kwargs.items():
            if key != "now":
                setattr(r, key, value)
        return r

    repo.update_statuses.side_effect = _update

    result = SlaService(repo).get_for_complaint(complaint_id)

    assert result.complaint_id == complaint_id
    assert result.overall_status == SlaStatus.PENDING
    assert result.assignment_status == SlaStatus.PENDING
    assert result.appointment_status == SlaStatus.PENDING
    assert result.resolution_status == SlaStatus.PENDING
    assert result.escalation_status == SlaStatus.PENDING
    assert result.assignment_due_at is None
    assert result.overall_due_at is None
    repo.update_statuses.assert_called_once()


def test_complaint_relationship_required() -> None:
    repo = MagicMock()
    repo.get_complaint.return_value = None

    with pytest.raises(NotFoundError):
        SlaService(repo).get_for_complaint(uuid.uuid4())


def test_one_sla_record_per_complaint() -> None:
    complaint_id = uuid.uuid4()
    existing = _sla_row(complaint_id=complaint_id)
    repo = MagicMock()
    repo.get_by_complaint_id.return_value = existing

    with pytest.raises(ValidationAppError) as exc:
        SlaService(repo).create_pending_for_complaint(complaint_id)
    assert exc.value.message == DUPLICATE_SLA_MESSAGE
    repo.create_pending.assert_not_called()


def test_create_pending_success() -> None:
    complaint_id = uuid.uuid4()
    created = _sla_row(complaint_id=complaint_id)
    repo = MagicMock()
    repo.get_by_complaint_id.return_value = None
    repo.create_pending.return_value = created

    result = SlaService(repo).create_pending_for_complaint(complaint_id)

    assert result.complaint_id == complaint_id
    assert result.overall_status == SlaStatus.PENDING
    repo.create_pending.assert_called_once_with(complaint_id)
    repo.commit.assert_not_called()


def test_complaint_deletion_restricted_while_sla_exists() -> None:
    complaint_id = uuid.uuid4()
    repo = MagicMock()
    repo.get_by_complaint_id.return_value = _sla_row(complaint_id=complaint_id)

    with pytest.raises(ValidationAppError) as exc:
        SlaService(repo).assert_complaint_deletable(complaint_id)
    assert exc.value.message == COMPLAINT_DELETE_RESTRICTED_MESSAGE


def test_complaint_deletable_when_no_sla() -> None:
    repo = MagicMock()
    repo.get_by_complaint_id.return_value = None
    SlaService(repo).assert_complaint_deletable(uuid.uuid4())
