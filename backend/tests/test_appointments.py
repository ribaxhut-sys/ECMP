"""Appointment booking unit/service tests (TASK-014)."""

from __future__ import annotations

import uuid
from datetime import UTC, date, datetime, time
from types import SimpleNamespace
from unittest.mock import MagicMock

import pytest

from app.core.errors import NotFoundError, ValidationAppError
from app.modules.appointments.schemas import AppointmentCreate
from app.modules.appointments.service import (
    ENGINEER_NOT_FOUND_MESSAGE,
    HAS_ACTIVE_APPOINTMENT_MESSAGE,
    NOT_APPROVED_MESSAGE,
    OVERLAP_MESSAGE,
    AppointmentService,
)


def _escalation(**overrides: object) -> SimpleNamespace:
    now = datetime.now(UTC)
    base = {
        "id": uuid.uuid4(),
        "complaint_id": uuid.uuid4(),
        "status": "APPROVED",
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


def _payload(**overrides: object) -> AppointmentCreate:
    data = {
        "appointmentDate": date(2026, 7, 30),
        "startTime": "09:00",
        "endTime": "10:00",
        "assignedEngineerId": uuid.uuid4(),
        "notes": "Customer confirmed.",
    }
    data.update(overrides)
    return AppointmentCreate.model_validate(data)


def test_book_appointment_success() -> None:
    actor = uuid.uuid4()
    complaint = _complaint()
    escalation = _escalation(complaint_id=complaint.id)
    payload = _payload()
    repo = MagicMock()
    repo.get_escalation.return_value = escalation
    repo.get_active_by_escalation.return_value = None
    repo.user_exists.return_value = True
    repo.find_engineer_overlap.return_value = None
    repo.get_complaint.return_value = complaint

    def _add(appt: object) -> object:
        appt.id = uuid.uuid4()  # type: ignore[attr-defined]
        return appt

    repo.add.side_effect = _add

    result = AppointmentService(repo).book(
        escalation.id, payload, actor_user_id=actor
    )

    assert result.status == "BOOKED"
    assert complaint.status == "IN_PROGRESS"
    assert escalation.status == "APPROVED"
    repo.add_timeline.assert_called_once()
    assert (
        repo.add_timeline.call_args.kwargs["event_type"]
        == "complaint.appointment_booked"
    )
    assert repo.add_timeline.call_args.kwargs["summary"] == "Appointment booked"
    repo.commit.assert_called_once()


def test_reject_when_escalation_not_approved() -> None:
    escalation = _escalation(status="REQUESTED")
    repo = MagicMock()
    repo.get_escalation.return_value = escalation

    with pytest.raises(ValidationAppError) as exc:
        AppointmentService(repo).book(
            escalation.id, _payload(), actor_user_id=uuid.uuid4()
        )
    assert exc.value.message == NOT_APPROVED_MESSAGE
    repo.commit.assert_not_called()


def test_reject_duplicate_active_appointment() -> None:
    escalation = _escalation()
    existing = SimpleNamespace(id=uuid.uuid4())
    repo = MagicMock()
    repo.get_escalation.return_value = escalation
    repo.get_active_by_escalation.return_value = existing

    with pytest.raises(ValidationAppError) as exc:
        AppointmentService(repo).book(
            escalation.id, _payload(), actor_user_id=uuid.uuid4()
        )
    assert exc.value.message == HAS_ACTIVE_APPOINTMENT_MESSAGE
    repo.commit.assert_not_called()


def test_reject_missing_engineer() -> None:
    escalation = _escalation()
    complaint = _complaint(id=escalation.complaint_id)
    repo = MagicMock()
    repo.get_escalation.return_value = escalation
    repo.get_active_by_escalation.return_value = None
    repo.user_exists.return_value = False

    with pytest.raises(ValidationAppError) as exc:
        AppointmentService(repo).book(
            escalation.id, _payload(), actor_user_id=uuid.uuid4()
        )
    assert exc.value.message == ENGINEER_NOT_FOUND_MESSAGE
    repo.commit.assert_not_called()
    _ = complaint


def test_reject_overlapping_engineer_schedule() -> None:
    escalation = _escalation()
    repo = MagicMock()
    repo.get_escalation.return_value = escalation
    repo.get_active_by_escalation.return_value = None
    repo.user_exists.return_value = True
    repo.find_engineer_overlap.return_value = SimpleNamespace(id=uuid.uuid4())

    with pytest.raises(ValidationAppError) as exc:
        AppointmentService(repo).book(
            escalation.id, _payload(), actor_user_id=uuid.uuid4()
        )
    assert exc.value.message == OVERLAP_MESSAGE
    repo.commit.assert_not_called()


def test_get_appointment_not_found() -> None:
    repo = MagicMock()
    repo.get_by_id.return_value = None
    with pytest.raises(NotFoundError):
        AppointmentService(repo).get_appointment(uuid.uuid4())


def test_get_appointment_success() -> None:
    now = datetime.now(UTC)
    engineer_id = uuid.uuid4()
    row = SimpleNamespace(
        id=uuid.uuid4(),
        escalation_id=uuid.uuid4(),
        appointment_date=date(2026, 7, 30),
        appointment_start_time=time(9, 0),
        appointment_end_time=time(10, 0),
        status="BOOKED",
        assigned_engineer_id=engineer_id,
        notes="Customer confirmed.",
        created_by=uuid.uuid4(),
        created_at=now,
        updated_at=now,
        assigned_engineer=SimpleNamespace(full_name="Ada Engineer"),
    )
    repo = MagicMock()
    repo.get_by_id.return_value = row

    result = AppointmentService(repo).get_appointment(row.id)
    assert result.status == "BOOKED"
    assert result.assigned_engineer_name == "Ada Engineer"
