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
        checked_in_at=None,
        checked_in_by=None,
        checkin_notes=None,
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


def _booked_appointment(**overrides: object) -> SimpleNamespace:
    now = datetime.now(UTC)
    base = {
        "id": uuid.uuid4(),
        "escalation_id": uuid.uuid4(),
        "status": "BOOKED",
        "checked_in_at": None,
        "checked_in_by": None,
        "checkin_notes": None,
        "updated_at": now,
        "updated_by": None,
    }
    base.update(overrides)
    return SimpleNamespace(**base)


def test_check_in_success() -> None:
    from app.modules.appointments.schemas import AppointmentCheckInRequest

    actor = uuid.uuid4()
    complaint = _complaint()
    escalation = _escalation(complaint_id=complaint.id, status="APPROVED")
    row = _booked_appointment(escalation_id=escalation.id)
    repo = MagicMock()
    repo.get_by_id.return_value = row
    repo.get_escalation.return_value = escalation
    repo.get_complaint.return_value = complaint

    result = AppointmentService(repo).check_in(
        row.id,
        AppointmentCheckInRequest(notes="Customer arrived and identity verified."),
        actor_user_id=actor,
    )

    assert result.status == "CHECKED_IN"
    assert result.checked_in_by == actor
    assert row.status == "CHECKED_IN"
    assert row.checked_in_by == actor
    assert row.checkin_notes == "Customer arrived and identity verified."
    assert complaint.status == "IN_PROGRESS"
    assert escalation.status == "APPROVED"
    repo.add_timeline.assert_called_once()
    assert (
        repo.add_timeline.call_args.kwargs["event_type"]
        == "complaint.appointment_checked_in"
    )
    assert repo.add_timeline.call_args.kwargs["summary"] == "Customer checked in"
    meta = repo.add_timeline.call_args.kwargs["metadata"]
    assert meta["appointmentId"] == str(row.id)
    assert meta["escalationId"] == str(escalation.id)
    assert meta["checkedInBy"] == str(actor)
    assert "checkedInAt" in meta
    repo.commit.assert_called_once()


def test_check_in_rejects_not_booked() -> None:
    from app.modules.appointments.schemas import AppointmentCheckInRequest
    from app.modules.appointments.service import NOT_BOOKED_MESSAGE

    row = _booked_appointment(status="OPEN")
    repo = MagicMock()
    repo.get_by_id.return_value = row

    with pytest.raises(ValidationAppError) as exc:
        AppointmentService(repo).check_in(
            row.id,
            AppointmentCheckInRequest(notes="Nope"),
            actor_user_id=uuid.uuid4(),
        )
    assert exc.value.message == NOT_BOOKED_MESSAGE
    repo.commit.assert_not_called()


def test_check_in_rejects_second_attempt() -> None:
    from app.modules.appointments.schemas import AppointmentCheckInRequest
    from app.modules.appointments.service import ALREADY_CHECKED_IN_MESSAGE

    now = datetime.now(UTC)
    row = _booked_appointment(
        status="CHECKED_IN",
        checked_in_at=now,
        checked_in_by=uuid.uuid4(),
    )
    repo = MagicMock()
    repo.get_by_id.return_value = row

    with pytest.raises(ValidationAppError) as exc:
        AppointmentService(repo).check_in(
            row.id,
            AppointmentCheckInRequest(notes="Again"),
            actor_user_id=uuid.uuid4(),
        )
    assert exc.value.message == ALREADY_CHECKED_IN_MESSAGE
    repo.commit.assert_not_called()


def test_check_in_not_found() -> None:
    from app.modules.appointments.schemas import AppointmentCheckInRequest

    repo = MagicMock()
    repo.get_by_id.return_value = None
    with pytest.raises(NotFoundError):
        AppointmentService(repo).check_in(
            uuid.uuid4(),
            AppointmentCheckInRequest(),
            actor_user_id=uuid.uuid4(),
        )
