"""SLA repository coverage (TASK-PLATFORM-CI-COV-001)."""

from __future__ import annotations

import uuid
from datetime import UTC, datetime
from unittest.mock import MagicMock, patch

from app.core.enums import SlaStatus
from app.modules.sla import repository as sla_mod
from app.modules.sla.repository import SlaRepository


def test_sla_repository_basic_queries_and_status_update() -> None:
    session = MagicMock()
    repo = SlaRepository(session)
    assert repo.session is session
    cid = uuid.uuid4()
    row = MagicMock()
    session.scalar.side_effect = [MagicMock(), row]
    assert repo.get_complaint(cid) is not None
    assert repo.get_by_complaint_id(cid) is row

    session.scalars.return_value.all.return_value = [1, 2]
    assert repo.count_for_complaint(cid) == 2

    when = datetime(2026, 1, 1, 12, 0, 0)
    updated = repo.update_statuses(
        row,
        assignment_status=SlaStatus.ON_TIME,
        appointment_status=SlaStatus.ON_TIME,
        resolution_status=SlaStatus.BREACHED,
        escalation_status=SlaStatus.ON_TIME,
        overall_status=SlaStatus.BREACHED,
        now=when,
    )
    assert updated is row
    assert row.overall_status == SlaStatus.BREACHED


def test_sla_load_completion_facts_and_timeline() -> None:
    session = MagicMock()
    repo = SlaRepository(session)
    cid = uuid.uuid4()
    t1 = datetime.now(UTC)
    complaint = MagicMock()
    complaint.closed_at = t1
    session.scalar.side_effect = [t1, t1, t1, None, t1, complaint]
    facts = repo.load_completion_facts(cid)
    assert facts.assignment_completed_at == t1
    assert facts.overall_completed_at == t1

    timeline = MagicMock()
    with patch.object(sla_mod, "ComplaintTimeline", return_value=timeline):
        entry = repo.add_timeline(
            complaint_id=cid,
            event_type="SLA_BREACH",
            event_at=datetime(2026, 1, 1, 8, 0, 0),
            summary="breach",
            metadata={"x": 1},
        )
    assert entry is timeline


def test_sla_create_and_policy_helpers() -> None:
    session = MagicMock()
    repo = SlaRepository(session)
    cid = uuid.uuid4()
    when = datetime.now(UTC)
    record = MagicMock()
    policy = MagicMock()

    with patch.object(sla_mod, "SlaRecord", return_value=record):
        assert repo.create_pending(cid, now=when) is record
        assert (
            repo.create_with_deadlines(
                cid,
                created_at=when,
                assignment_due_at=when,
                appointment_due_at=when,
                resolution_due_at=when,
                escalation_due_at=when,
                overall_due_at=when,
            )
            is record
        )

    session.scalars.return_value.all.return_value = [policy]
    assert repo.list_policies() == [policy]
    session.scalar.side_effect = [policy, policy]
    assert repo.get_policy(uuid.uuid4()) is policy
    assert repo.get_active_policy() is policy

    with patch.object(sla_mod, "SlaPolicy", return_value=policy):
        created = repo.create_policy(
            name="default",
            description=None,
            assignment_target_minutes=30,
            appointment_target_minutes=60,
            resolution_target_minutes=120,
            escalation_target_minutes=90,
            overall_target_minutes=240,
            is_active=True,
            now=when,
        )
    assert created is policy

    repo.deactivate_all_policies(now=when)
    session.execute.assert_called()
    assert repo.set_policy_active(policy, is_active=False, now=when) is policy
    repo.commit()
    assert repo.refresh(policy) is policy
