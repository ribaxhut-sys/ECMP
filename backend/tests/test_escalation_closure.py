"""Escalation Closure unit/service tests (TASK-020 / API-313)."""

from __future__ import annotations

import uuid
from datetime import UTC, datetime
from types import SimpleNamespace
from unittest.mock import MagicMock

import pytest

from app.core.auth import Principal, require_escalation_close
from app.core.enums import ComplaintStatus, EscalationRequestStatus
from app.core.errors import ForbiddenError, NotFoundError, ValidationAppError
from app.modules.escalations.schemas import CloseEscalationRequest
from app.modules.escalations.service import (
    ALREADY_CLOSED_MESSAGE,
    COMPLAINT_NOT_CLOSED_MESSAGE,
    FINAL_RESOLUTION_REQUIRED_MESSAGE,
    EscalationService,
)


def _escalation(**overrides: object) -> SimpleNamespace:
    now = datetime.now(UTC)
    base = {
        "id": uuid.uuid4(),
        "complaint_id": uuid.uuid4(),
        "status": EscalationRequestStatus.APPROVED,
        "closed_at": None,
        "closed_by": None,
        "closure_notes": None,
        "updated_at": now,
        "updated_by": None,
    }
    base.update(overrides)
    return SimpleNamespace(**base)


def _complaint(**overrides: object) -> SimpleNamespace:
    now = datetime.now(UTC)
    base = {
        "id": uuid.uuid4(),
        "status": ComplaintStatus.CLOSED,
        "updated_at": now,
        "updated_by": None,
    }
    base.update(overrides)
    return SimpleNamespace(**base)


def _payload() -> CloseEscalationRequest:
    return CloseEscalationRequest(notes="Escalation verified and officially closed.")


def test_close_escalation_success(monkeypatch: pytest.MonkeyPatch) -> None:
    actor_id = uuid.uuid4()
    escalation = _escalation()
    complaint = _complaint(id=escalation.complaint_id, status="CLOSED")
    final = SimpleNamespace(final_resolution_at=datetime.now(UTC))
    closer = SimpleNamespace(id=actor_id, full_name="Admin One")

    repo = MagicMock()
    repo.get_by_id.return_value = escalation
    repo.get_complaint.return_value = complaint
    repo.get_final_resolution.return_value = final
    repo.get_user.return_value = closer
    monkeypatch.setattr(
        "app.modules.sla.hooks.evaluate_sla_for_complaint",
        lambda *args, **kwargs: None,
    )

    result = EscalationService(repo).close(
        escalation.id,
        _payload(),
        actor_user_id=actor_id,
    )

    assert result.status == EscalationRequestStatus.CLOSED
    assert result.escalation_id == escalation.id
    assert result.closed_by == actor_id
    assert escalation.status == EscalationRequestStatus.CLOSED
    assert escalation.closed_at is not None
    assert escalation.closed_by == actor_id
    assert escalation.closure_notes.startswith("Escalation verified")
    assert complaint.status == ComplaintStatus.CLOSED
    repo.add_timeline.assert_called_once()
    assert repo.add_timeline.call_args.kwargs["event_type"] == "escalation.closed"
    assert repo.add_timeline.call_args.kwargs["summary"] == "Escalation closed"
    meta = repo.add_timeline.call_args.kwargs["metadata"]
    assert meta["escalationId"] == str(escalation.id)
    assert meta["complaintId"] == str(complaint.id)
    assert meta["closedBy"] == str(actor_id)
    assert "closedAt" in meta
    repo.commit.assert_called_once()


def test_reject_when_complaint_not_closed() -> None:
    escalation = _escalation()
    complaint = _complaint(id=escalation.complaint_id, status="IN_PROGRESS")
    repo = MagicMock()
    repo.get_by_id.return_value = escalation
    repo.get_complaint.return_value = complaint

    with pytest.raises(ValidationAppError) as exc:
        EscalationService(repo).close(
            escalation.id,
            _payload(),
            actor_user_id=uuid.uuid4(),
        )
    assert exc.value.message == COMPLAINT_NOT_CLOSED_MESSAGE
    repo.add_timeline.assert_not_called()
    repo.commit.assert_not_called()


def test_reject_duplicate_closure() -> None:
    escalation = _escalation(
        status=EscalationRequestStatus.CLOSED,
        closed_at=datetime.now(UTC),
        closed_by=uuid.uuid4(),
    )
    repo = MagicMock()
    repo.get_by_id.return_value = escalation

    with pytest.raises(ValidationAppError) as exc:
        EscalationService(repo).close(
            escalation.id,
            _payload(),
            actor_user_id=uuid.uuid4(),
        )
    assert exc.value.message == ALREADY_CLOSED_MESSAGE
    repo.add_timeline.assert_not_called()
    repo.commit.assert_not_called()


def test_timeline_created_and_complaint_remains_closed(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    actor_id = uuid.uuid4()
    escalation = _escalation()
    complaint = _complaint(id=escalation.complaint_id, status="CLOSED")
    final = SimpleNamespace(final_resolution_at=datetime.now(UTC))

    repo = MagicMock()
    repo.get_by_id.return_value = escalation
    repo.get_complaint.return_value = complaint
    repo.get_final_resolution.return_value = final
    repo.get_user.return_value = SimpleNamespace(id=actor_id)
    monkeypatch.setattr(
        "app.modules.sla.hooks.evaluate_sla_for_complaint",
        lambda *args, **kwargs: None,
    )

    EscalationService(repo).close(
        escalation.id,
        _payload(),
        actor_user_id=actor_id,
    )

    assert escalation.status == EscalationRequestStatus.CLOSED
    assert complaint.status == ComplaintStatus.CLOSED
    repo.add_timeline.assert_called_once()


def test_reject_without_final_resolution() -> None:
    escalation = _escalation()
    complaint = _complaint(id=escalation.complaint_id, status="CLOSED")
    repo = MagicMock()
    repo.get_by_id.return_value = escalation
    repo.get_complaint.return_value = complaint
    repo.get_final_resolution.return_value = None

    with pytest.raises(ValidationAppError) as exc:
        EscalationService(repo).close(
            escalation.id,
            _payload(),
            actor_user_id=uuid.uuid4(),
        )
    assert exc.value.message == FINAL_RESOLUTION_REQUIRED_MESSAGE
    repo.add_timeline.assert_not_called()


def test_escalation_not_found() -> None:
    repo = MagicMock()
    repo.get_by_id.return_value = None

    with pytest.raises(NotFoundError):
        EscalationService(repo).close(
            uuid.uuid4(),
            _payload(),
            actor_user_id=uuid.uuid4(),
        )


def test_require_escalation_close_permission_admin() -> None:
    principal = Principal(
        user_id=uuid.uuid4(),
        roles=("ADMIN",),
        permissions=frozenset({"escalations:close", "*"}),
    )
    assert require_escalation_close(principal) is principal


def test_require_escalation_close_rejects_supervisor() -> None:
    principal = Principal(
        user_id=uuid.uuid4(),
        roles=("BRANCH_SUPERVISOR",),
        permissions=frozenset({"escalations:close", "complaints:close"}),
    )
    with pytest.raises(ForbiddenError):
        require_escalation_close(principal)


def test_require_escalation_close_rejects_missing_permission() -> None:
    from app.core.auth import require_permissions

    principal = Principal(
        user_id=uuid.uuid4(),
        roles=("ADMIN",),
        permissions=frozenset({"escalations:read"}),
    )
    gate = require_permissions("escalations:close")
    with pytest.raises(ForbiddenError):
        gate(principal)
