"""Assignment API unit/service tests (no Timeline/Escalation APIs)."""

from __future__ import annotations

import uuid
from datetime import UTC, datetime
from types import SimpleNamespace
from unittest.mock import MagicMock

import pytest

from app.core.errors import ForbiddenError, InvalidStateError, ValidationAppError
from app.core.auth import Principal, require_supervisor_assign
from app.modules.assignments.schemas import AssignComplaintRequest
from app.modules.assignments.service import AssignmentService


def test_supervisor_gate_rejects_non_supervisor() -> None:
    principal = Principal(
        user_id=uuid.uuid4(),
        roles=("AGENT",),
        permissions=frozenset({"complaints:assign"}),
    )
    with pytest.raises(ForbiddenError):
        require_supervisor_assign(principal)


def test_supervisor_gate_allows_supervisor() -> None:
    principal = Principal(
        user_id=uuid.uuid4(),
        roles=("SUPERVISOR",),
        permissions=frozenset({"complaints:assign"}),
    )
    assert require_supervisor_assign(principal) is principal


def test_assign_new_to_assigned(monkeypatch: pytest.MonkeyPatch) -> None:
    complaint_id = uuid.uuid4()
    assignee_id = uuid.uuid4()
    actor_id = uuid.uuid4()
    now = datetime.now(UTC)

    complaint = SimpleNamespace(
        id=complaint_id,
        status="NEW",
        updated_at=now,
        updated_by=None,
    )
    created_assignment = SimpleNamespace(
        id=uuid.uuid4(),
        complaint_id=complaint_id,
        assignee_id=assignee_id,
        assigned_by=actor_id,
        assigned_at=now,
        unassigned_at=None,
        is_current=True,
        notes=None,
    )

    repo = MagicMock()
    repo.get_complaint.return_value = complaint
    repo.user_exists.return_value = True
    repo.get_user_full_name.return_value = "Agent One"
    repo.get_current_assignment.return_value = None
    repo.add_assignment.side_effect = lambda a: setattr(a, "id", created_assignment.id) or a
    monkeypatch.setattr(
        "app.modules.sla.hooks.evaluate_sla_for_complaint",
        lambda *args, **kwargs: None,
    )

    service = AssignmentService(repo)
    result = service.assign(
        complaint_id,
        AssignComplaintRequest(assigneeId=assignee_id),
        actor_user_id=actor_id,
    )

    assert result.status == "ASSIGNED"
    assert result.reassigned is False
    assert complaint.status == "ASSIGNED"
    repo.close_assignment.assert_not_called()
    repo.add_timeline.assert_called_once()
    assert repo.add_timeline.call_args.kwargs["event_type"] == "complaint.assigned"
    assert "Agent One" in repo.add_timeline.call_args.kwargs["summary"]
    repo.commit.assert_called_once()


def test_reassignment_requires_reason() -> None:
    complaint_id = uuid.uuid4()
    complaint = SimpleNamespace(id=complaint_id, status="ASSIGNED", updated_at=None, updated_by=None)
    current = SimpleNamespace(id=uuid.uuid4(), is_current=True)

    repo = MagicMock()
    repo.get_complaint.return_value = complaint
    repo.user_exists.return_value = True
    repo.get_current_assignment.return_value = current

    service = AssignmentService(repo)
    with pytest.raises(ValidationAppError) as exc:
        service.assign(
            complaint_id,
            AssignComplaintRequest(assigneeId=uuid.uuid4()),
            actor_user_id=uuid.uuid4(),
        )
    assert "reason" in exc.value.message.lower()
    repo.close_assignment.assert_not_called()


def test_reassignment_closes_previous_without_delete(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    complaint_id = uuid.uuid4()
    assignee_id = uuid.uuid4()
    actor_id = uuid.uuid4()
    now = datetime.now(UTC)
    complaint = SimpleNamespace(
        id=complaint_id,
        status="ASSIGNED",
        updated_at=now,
        updated_by=None,
    )
    current = SimpleNamespace(
        id=uuid.uuid4(),
        is_current=True,
        unassigned_at=None,
        updated_at=None,
        updated_by=None,
    )

    repo = MagicMock()
    repo.get_complaint.return_value = complaint
    repo.user_exists.return_value = True
    repo.get_user_full_name.return_value = "Agent Two"
    repo.get_current_assignment.return_value = current
    repo.add_assignment.side_effect = lambda a: setattr(a, "id", uuid.uuid4()) or a
    monkeypatch.setattr(
        "app.modules.sla.hooks.evaluate_sla_for_complaint",
        lambda *args, **kwargs: None,
    )

    service = AssignmentService(repo)
    result = service.assign(
        complaint_id,
        AssignComplaintRequest(assigneeId=assignee_id, reason="Workload balance"),
        actor_user_id=actor_id,
    )

    assert result.reassigned is True
    repo.close_assignment.assert_called_once()
    assert current is repo.close_assignment.call_args.args[0]
    assert repo.add_timeline.call_args.kwargs["event_type"] == "complaint.reassigned"
    assert "Agent Two" in repo.add_timeline.call_args.kwargs["summary"]
    # ensure we never call a delete helper
    assert not hasattr(repo, "delete_assignment") or not repo.delete_assignment.called


def test_invalid_status_rejected() -> None:
    complaint_id = uuid.uuid4()
    complaint = SimpleNamespace(id=complaint_id, status="CLOSED")
    repo = MagicMock()
    repo.get_complaint.return_value = complaint

    service = AssignmentService(repo)
    with pytest.raises(InvalidStateError):
        service.assign(
            complaint_id,
            AssignComplaintRequest(assigneeId=uuid.uuid4()),
            actor_user_id=uuid.uuid4(),
        )
