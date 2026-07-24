"""Complaint Closure unit/service tests (TASK-019 / API-312)."""

from __future__ import annotations

import uuid
from datetime import UTC, datetime
from types import SimpleNamespace
from unittest.mock import MagicMock

import pytest

from app.core.auth import Principal, require_complaint_close
from app.core.enums import ComplaintStatus, EscalationRequestStatus
from app.core.errors import ForbiddenError, NotFoundError, ValidationAppError
from app.modules.complaints.schemas import CloseComplaintRequest
from app.modules.complaints.service import (
    ALREADY_CLOSED_MESSAGE,
    FINAL_RESOLUTION_REQUIRED_MESSAGE,
    NOT_IN_PROGRESS_FOR_CLOSE_MESSAGE,
    ComplaintService,
)


def _complaint(**overrides: object) -> SimpleNamespace:
    now = datetime.now(UTC)
    actor_id = uuid.uuid4()
    customer_id = uuid.uuid4()
    base = {
        "id": uuid.uuid4(),
        "complaint_number": "CMP-TEST",
        "customer_id": customer_id,
        "branch_id": None,
        "source_type": "CUSTOMER",
        "source_id": customer_id,
        "target_type": "BRANCH",
        "target_id": None,
        "subject": "s",
        "description": "d",
        "status": "IN_PROGRESS",
        "priority": "MEDIUM",
        "channel": None,
        "category": None,
        "reported_at": now,
        "closed_at": None,
        "closed_by": None,
        "closure_notes": None,
        "created_at": now,
        "created_by": actor_id,
        "updated_at": now,
        "updated_by": actor_id,
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


def _payload() -> CloseComplaintRequest:
    return CloseComplaintRequest(notes="Complaint verified and officially closed.")


def test_close_complaint_success(monkeypatch: pytest.MonkeyPatch) -> None:
    actor_id = uuid.uuid4()
    complaint = _complaint(status="IN_PROGRESS")
    escalation = _escalation()
    final = SimpleNamespace(final_resolution_at=datetime.now(UTC))
    closer = SimpleNamespace(id=actor_id, full_name="Supervisor One")

    repo = MagicMock()
    repo.get_by_id.return_value = complaint
    repo.get_final_resolution.return_value = final
    repo.get_latest_escalation.return_value = escalation
    repo.get_user.return_value = closer
    monkeypatch.setattr(
        "app.modules.sla.hooks.evaluate_sla_for_complaint",
        lambda *args, **kwargs: None,
    )

    result = ComplaintService(repo).close(
        complaint.id,
        _payload(),
        actor_user_id=actor_id,
    )

    assert result.status == ComplaintStatus.CLOSED
    assert result.complaint_id == complaint.id
    assert result.closed_by == actor_id
    assert complaint.status == ComplaintStatus.CLOSED
    assert complaint.closed_at is not None
    assert complaint.closed_by == actor_id
    assert complaint.closure_notes.startswith("Complaint verified")
    assert escalation.status == EscalationRequestStatus.APPROVED
    repo.add_timeline.assert_called_once()
    assert repo.add_timeline.call_args.kwargs["event_type"] == "complaint.closed"
    assert repo.add_timeline.call_args.kwargs["summary"] == "Complaint closed"
    meta = repo.add_timeline.call_args.kwargs["metadata"]
    assert meta["complaintId"] == str(complaint.id)
    assert meta["escalationId"] == str(escalation.id)
    assert meta["closedBy"] == str(actor_id)
    assert "closedAt" in meta
    repo.commit.assert_called_once()


def test_reject_without_final_resolution() -> None:
    complaint = _complaint()
    repo = MagicMock()
    repo.get_by_id.return_value = complaint
    repo.get_final_resolution.return_value = None

    with pytest.raises(ValidationAppError) as exc:
        ComplaintService(repo).close(
            complaint.id,
            _payload(),
            actor_user_id=uuid.uuid4(),
        )
    assert exc.value.message == FINAL_RESOLUTION_REQUIRED_MESSAGE
    repo.add_timeline.assert_not_called()
    repo.commit.assert_not_called()


def test_reject_duplicate_closure() -> None:
    complaint = _complaint(
        status="CLOSED",
        closed_at=datetime.now(UTC),
        closed_by=uuid.uuid4(),
    )
    repo = MagicMock()
    repo.get_by_id.return_value = complaint

    with pytest.raises(ValidationAppError) as exc:
        ComplaintService(repo).close(
            complaint.id,
            _payload(),
            actor_user_id=uuid.uuid4(),
        )
    assert exc.value.message == ALREADY_CLOSED_MESSAGE
    repo.add_timeline.assert_not_called()
    repo.commit.assert_not_called()


def test_timeline_created_and_escalation_remains_approved(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    actor_id = uuid.uuid4()
    complaint = _complaint(status="IN_PROGRESS")
    escalation = _escalation(status=EscalationRequestStatus.APPROVED)
    final = SimpleNamespace(final_resolution_at=datetime.now(UTC))

    repo = MagicMock()
    repo.get_by_id.return_value = complaint
    repo.get_final_resolution.return_value = final
    repo.get_latest_escalation.return_value = escalation
    repo.get_user.return_value = SimpleNamespace(id=actor_id)
    monkeypatch.setattr(
        "app.modules.sla.hooks.evaluate_sla_for_complaint",
        lambda *args, **kwargs: None,
    )

    service = ComplaintService(repo)
    service.close(
        complaint.id,
        _payload(),
        actor_user_id=actor_id,
    )

    assert complaint.status == ComplaintStatus.CLOSED
    assert escalation.status == EscalationRequestStatus.APPROVED
    repo.add_timeline.assert_called_once()
    assert len(service._recent_events) == 1
    assert service._recent_events[0].event_type.value == "ComplaintClosed"


def test_reject_non_in_progress_complaint() -> None:
    complaint = _complaint(status="ASSIGNED")
    repo = MagicMock()
    repo.get_by_id.return_value = complaint

    with pytest.raises(ValidationAppError) as exc:
        ComplaintService(repo).close(
            complaint.id,
            _payload(),
            actor_user_id=uuid.uuid4(),
        )
    assert exc.value.message == NOT_IN_PROGRESS_FOR_CLOSE_MESSAGE


def test_complaint_not_found() -> None:
    repo = MagicMock()
    repo.get_by_id.return_value = None

    with pytest.raises(NotFoundError):
        ComplaintService(repo).close(
            uuid.uuid4(),
            _payload(),
            actor_user_id=uuid.uuid4(),
        )


def test_require_complaint_close_permission_supervisor() -> None:
    principal = Principal(
        user_id=uuid.uuid4(),
        roles=("BRANCH_SUPERVISOR",),
        permissions=frozenset({"complaints:close"}),
    )
    assert require_complaint_close(principal) is principal


def test_require_complaint_close_permission_admin() -> None:
    principal = Principal(
        user_id=uuid.uuid4(),
        roles=("ADMIN",),
        permissions=frozenset({"complaints:close", "*"}),
    )
    assert require_complaint_close(principal) is principal


def test_require_complaint_close_rejects_engineer() -> None:
    principal = Principal(
        user_id=uuid.uuid4(),
        roles=("HO_ENGINEER",),
        permissions=frozenset({"complaints:close", "appointments:complete"}),
    )
    with pytest.raises(ForbiddenError):
        require_complaint_close(principal)


def test_require_complaint_close_rejects_missing_permission() -> None:
    from app.core.auth import require_permissions

    principal = Principal(
        user_id=uuid.uuid4(),
        roles=("BRANCH_SUPERVISOR",),
        permissions=frozenset({"complaints:read"}),
    )
    gate = require_permissions("complaints:close")
    with pytest.raises(ForbiddenError):
        gate(principal)
