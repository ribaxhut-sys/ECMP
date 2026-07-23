"""Escalation service unit tests."""

from __future__ import annotations

import uuid
from datetime import UTC, datetime
from types import SimpleNamespace
from unittest.mock import MagicMock

import pytest

from app.core.auth import Principal, require_supervisor_escalate
from app.core.errors import ForbiddenError, InvalidStateError, ValidationAppError
from app.modules.escalations.schemas import EscalateComplaintRequest
from app.modules.escalations.service import EscalationService


def test_supervisor_escalate_gate() -> None:
    allowed = Principal(
        user_id=uuid.uuid4(),
        roles=("SUPERVISOR",),
        permissions=frozenset({"complaints:escalate"}),
    )
    assert require_supervisor_escalate(allowed) is allowed

    denied = Principal(
        user_id=uuid.uuid4(),
        roles=("AGENT",),
        permissions=frozenset({"complaints:escalate"}),
    )
    with pytest.raises(ForbiddenError):
        require_supervisor_escalate(denied)


@pytest.mark.parametrize(
    "status,message_part",
    [
        ("NEW", "NEW"),
        ("RESOLVED", "RESOLVED"),
        ("CLOSED", "CLOSED"),
    ],
)
def test_reject_disallowed_statuses(status: str, message_part: str) -> None:
    complaint_id = uuid.uuid4()
    repo = MagicMock()
    repo.get_complaint.return_value = SimpleNamespace(id=complaint_id, status=status)
    service = EscalationService(repo)

    with pytest.raises(InvalidStateError) as exc:
        service.escalate(
            complaint_id,
            EscalateComplaintRequest(
                reason="Need higher authority",
                escalatedToUserId=uuid.uuid4(),
            ),
            actor_user_id=uuid.uuid4(),
        )
    assert message_part in exc.value.message


def test_escalate_assigned_success() -> None:
    complaint_id = uuid.uuid4()
    target_user = uuid.uuid4()
    actor = uuid.uuid4()
    now = datetime.now(UTC)
    complaint = SimpleNamespace(
        id=complaint_id,
        status="ASSIGNED",
        updated_at=now,
        updated_by=None,
    )

    repo = MagicMock()
    repo.get_complaint.return_value = complaint
    repo.user_exists.return_value = True
    repo.get_current_assignee_id.return_value = uuid.uuid4()
    repo.next_level.return_value = 1
    repo.add_escalation.side_effect = lambda e: setattr(e, "id", uuid.uuid4()) or e

    service = EscalationService(repo)
    result = service.escalate(
        complaint_id,
        EscalateComplaintRequest(
            reason="SLA risk",
            escalatedToUserId=target_user,
        ),
        actor_user_id=actor,
    )

    assert result.status == "ESCALATED"
    assert complaint.status == "ESCALATED"
    repo.add_timeline.assert_called_once()
    assert repo.add_timeline.call_args.kwargs["event_type"] == "complaint.escalated"
    repo.commit.assert_called_once()


def test_escalate_requires_target() -> None:
    with pytest.raises(Exception):
        EscalateComplaintRequest(reason="missing target")


def test_escalate_invalid_target_user() -> None:
    complaint_id = uuid.uuid4()
    repo = MagicMock()
    repo.get_complaint.return_value = SimpleNamespace(
        id=complaint_id, status="IN_PROGRESS"
    )
    repo.user_exists.return_value = False

    service = EscalationService(repo)
    with pytest.raises(ValidationAppError):
        service.escalate(
            complaint_id,
            EscalateComplaintRequest(
                reason="Need manager",
                escalatedToUserId=uuid.uuid4(),
            ),
            actor_user_id=uuid.uuid4(),
        )
