"""Final Resolution unit/service tests (TASK-018 / DEC-011)."""

from __future__ import annotations

import uuid
from datetime import UTC, datetime
from types import SimpleNamespace
from unittest.mock import MagicMock

import pytest

from app.core.auth import Principal, require_final_resolution
from app.core.enums import ComplaintStatus, EscalationRequestStatus
from app.core.errors import ForbiddenError, NotFoundError, ValidationAppError
from app.modules.resolutions.schemas import FinalResolutionRequest
from app.modules.resolutions.service import (
    ALREADY_FINAL_RESOLUTION_MESSAGE,
    APPOINTMENT_NO_SHOW_MESSAGE,
    APPOINTMENT_NOT_COMPLETED_MESSAGE,
    NOT_IN_PROGRESS_FOR_FINAL_MESSAGE,
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


def _appointment(**overrides: object) -> SimpleNamespace:
    now = datetime.now(UTC)
    base = {
        "id": uuid.uuid4(),
        "escalation_id": uuid.uuid4(),
        "status": "COMPLETED",
        "completed_at": now,
        "no_show_at": None,
    }
    base.update(overrides)
    return SimpleNamespace(**base)


def _escalation(**overrides: object) -> SimpleNamespace:
    now = datetime.now(UTC)
    base = {
        "id": uuid.uuid4(),
        "status": EscalationRequestStatus.APPROVED,
        "updated_at": now,
        "updated_by": None,
    }
    base.update(overrides)
    return SimpleNamespace(**base)


def _payload() -> FinalResolutionRequest:
    return FinalResolutionRequest(
        summary="Root cause identified and corrective action completed.",
        notes="Replaced defective component and verified operation.",
        followUpRequired=False,
    )


def test_submit_final_resolution_success(monkeypatch: pytest.MonkeyPatch) -> None:
    actor_id = uuid.uuid4()
    complaint = _complaint(status="IN_PROGRESS")
    appointment = _appointment()
    escalation = _escalation(id=appointment.escalation_id)
    submitter = SimpleNamespace(id=actor_id, full_name="Engineer One")

    repo = MagicMock()
    repo.get_complaint.return_value = complaint
    repo.get_final_resolution.return_value = None
    repo.get_latest_appointment_for_complaint.return_value = appointment
    repo.get_escalation.return_value = escalation
    repo.get_user.return_value = submitter
    repo.get_current_resolution.return_value = None
    repo.add_resolution.side_effect = lambda r: setattr(r, "id", uuid.uuid4()) or r
    monkeypatch.setattr(
        "app.modules.sla.hooks.evaluate_sla_for_complaint",
        lambda *args, **kwargs: None,
    )

    result = ResolutionService(repo).submit_final_resolution(
        complaint.id,
        _payload(),
        actor_user_id=actor_id,
    )

    assert result.status == "FINAL_RESOLUTION_SUBMITTED"
    assert result.complaint_id == complaint.id
    assert result.submitted_by == actor_id
    assert complaint.status == ComplaintStatus.IN_PROGRESS
    assert escalation.status == EscalationRequestStatus.APPROVED
    repo.add_timeline.assert_called_once()
    assert (
        repo.add_timeline.call_args.kwargs["event_type"]
        == "complaint.final_resolution_submitted"
    )
    assert (
        repo.add_timeline.call_args.kwargs["summary"]
        == "Final resolution submitted"
    )
    meta = repo.add_timeline.call_args.kwargs["metadata"]
    assert meta["appointmentId"] == str(appointment.id)
    assert meta["escalationId"] == str(escalation.id)
    assert meta["followUpRequired"] is False
    repo.commit.assert_called_once()


def test_reject_when_appointment_not_completed() -> None:
    complaint = _complaint()
    appointment = _appointment(status="CHECKED_IN", completed_at=None)
    repo = MagicMock()
    repo.get_complaint.return_value = complaint
    repo.get_final_resolution.return_value = None
    repo.get_latest_appointment_for_complaint.return_value = appointment

    with pytest.raises(ValidationAppError) as exc:
        ResolutionService(repo).submit_final_resolution(
            complaint.id,
            _payload(),
            actor_user_id=uuid.uuid4(),
        )
    assert exc.value.message == APPOINTMENT_NOT_COMPLETED_MESSAGE
    repo.add_timeline.assert_not_called()
    repo.commit.assert_not_called()


def test_reject_duplicate_final_resolution() -> None:
    complaint = _complaint()
    existing = SimpleNamespace(
        final_resolution_at=datetime.now(UTC),
        final_resolution_by=uuid.uuid4(),
    )
    repo = MagicMock()
    repo.get_complaint.return_value = complaint
    repo.get_final_resolution.return_value = existing

    with pytest.raises(ValidationAppError) as exc:
        ResolutionService(repo).submit_final_resolution(
            complaint.id,
            _payload(),
            actor_user_id=uuid.uuid4(),
        )
    assert exc.value.message == ALREADY_FINAL_RESOLUTION_MESSAGE
    repo.add_timeline.assert_not_called()
    repo.commit.assert_not_called()


def test_reject_when_appointment_no_show() -> None:
    complaint = _complaint()
    appointment = _appointment(
        status="NO_SHOW",
        completed_at=None,
        no_show_at=datetime.now(UTC),
    )
    repo = MagicMock()
    repo.get_complaint.return_value = complaint
    repo.get_final_resolution.return_value = None
    repo.get_latest_appointment_for_complaint.return_value = appointment

    with pytest.raises(ValidationAppError) as exc:
        ResolutionService(repo).submit_final_resolution(
            complaint.id,
            _payload(),
            actor_user_id=uuid.uuid4(),
        )
    assert exc.value.message == APPOINTMENT_NO_SHOW_MESSAGE
    repo.add_timeline.assert_not_called()
    repo.commit.assert_not_called()


def test_timeline_created_and_statuses_unchanged(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    actor_id = uuid.uuid4()
    complaint = _complaint(status="IN_PROGRESS")
    appointment = _appointment()
    escalation = _escalation(
        id=appointment.escalation_id,
        status=EscalationRequestStatus.APPROVED,
    )
    submitter = SimpleNamespace(id=actor_id, full_name="Engineer One")
    current = SimpleNamespace(
        final_resolution_at=None,
        final_resolution_by=None,
        final_resolution_summary=None,
        final_resolution_notes=None,
        follow_up_required=False,
        updated_at=None,
        updated_by=None,
    )

    repo = MagicMock()
    repo.get_complaint.return_value = complaint
    repo.get_final_resolution.return_value = None
    repo.get_latest_appointment_for_complaint.return_value = appointment
    repo.get_escalation.return_value = escalation
    repo.get_user.return_value = submitter
    repo.get_current_resolution.return_value = current
    monkeypatch.setattr(
        "app.modules.sla.hooks.evaluate_sla_for_complaint",
        lambda *args, **kwargs: None,
    )

    ResolutionService(repo).submit_final_resolution(
        complaint.id,
        _payload(),
        actor_user_id=actor_id,
    )

    assert current.final_resolution_summary.startswith("Root cause")
    assert complaint.status == "IN_PROGRESS"
    assert escalation.status == EscalationRequestStatus.APPROVED
    repo.add_timeline.assert_called_once()
    repo.add_resolution.assert_not_called()


def test_reject_non_in_progress_complaint() -> None:
    complaint = _complaint(status="ASSIGNED")
    repo = MagicMock()
    repo.get_complaint.return_value = complaint

    with pytest.raises(ValidationAppError) as exc:
        ResolutionService(repo).submit_final_resolution(
            complaint.id,
            _payload(),
            actor_user_id=uuid.uuid4(),
        )
    assert exc.value.message == NOT_IN_PROGRESS_FOR_FINAL_MESSAGE


def test_complaint_not_found() -> None:
    repo = MagicMock()
    repo.get_complaint.return_value = None

    with pytest.raises(NotFoundError):
        ResolutionService(repo).submit_final_resolution(
            uuid.uuid4(),
            _payload(),
            actor_user_id=uuid.uuid4(),
        )


def test_require_final_resolution_permission_ho_engineer() -> None:
    principal = Principal(
        user_id=uuid.uuid4(),
        roles=("HO_ENGINEER",),
        permissions=frozenset({"appointments:complete"}),
    )
    assert require_final_resolution(principal) is principal


def test_require_final_resolution_rejects_scheduler() -> None:
    principal = Principal(
        user_id=uuid.uuid4(),
        roles=("HO_SCHEDULER",),
        permissions=frozenset({"appointments:complete", "escalations:review"}),
    )
    with pytest.raises(ForbiddenError):
        require_final_resolution(principal)


def test_require_final_resolution_rejects_missing_permission() -> None:
    from app.core.auth import require_permissions

    principal = Principal(
        user_id=uuid.uuid4(),
        roles=("HO_ENGINEER",),
        permissions=frozenset({"complaints:read"}),
    )
    gate = require_permissions("appointments:complete")
    request = MagicMock()
    request.state = SimpleNamespace(request_id="unit-req-1")
    request.headers = {}
    request.url.path = "/unit"
    request.client = None
    with pytest.raises(ForbiddenError):
        gate(principal=principal, request=request, session=MagicMock())
