"""Final coverage push toward 90% (TASK-PLATFORM-CI-COV-001)."""

from __future__ import annotations

import uuid
from datetime import UTC, datetime
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from app.modules.complaint.domain.models import AssigneeType, Assignment
from app.modules.complaint.infrastructure.mappers.assignment_mapper import (
    AssignmentMapper,
)
from app.modules.complaint.infrastructure.mappers.escalation_mapper import (
    EscalationMapper,
)
from app.modules.complaint.infrastructure.mappers.sla_mapper import (
    ComplaintSlaMapper,
    SLAPolicyMapper,
)
from app.modules.queue.mappers.queue_mapper import QueueCounterMapper
from app.modules.queue.repositories.queue_counter_repository import (
    SqlAlchemyQueueCounterRepository,
)


def test_assignment_mapper_roundtrip() -> None:
    now = datetime.now(UTC)
    aid = uuid.uuid4()
    cid = uuid.uuid4()
    domain = Assignment(
        assignment_id=aid,
        complaint_id=cid,
        assignee_type=AssigneeType.USER,
        assignee_id="user-1",
        assigned_at=now,
        assigned_by="admin-1",
        released_at=None,
        release_reason=None,
        is_active=True,
    )
    row = AssignmentMapper.to_orm(domain)
    back = AssignmentMapper.to_domain(row)
    assert back.assignment_id == aid
    assert back.assignee_type == AssigneeType.USER
    domain2 = Assignment(
        assignment_id=aid,
        complaint_id=cid,
        assignee_type=AssigneeType.USER,
        assignee_id="user-1",
        assigned_at=now,
        assigned_by="admin-1",
        released_at=now,
        release_reason="done",
        is_active=False,
    )
    AssignmentMapper.apply_to_orm(domain2, row)
    assert row.is_active is False
    assert row.release_reason == "done"


def test_escalation_and_sla_mapper_roundtrips() -> None:
    from app.modules.complaint.domain.models import (
        ComplaintSLA,
        Escalation,
        EscalationLevel,
        SLAPolicy,
    )

    now = datetime.now(UTC)
    esc = Escalation(
        escalation_id=uuid.uuid4(),
        complaint_id=uuid.uuid4(),
        level=EscalationLevel.LEVEL_1,
        reason="need more help",
        escalated_by="agent-1",
        escalated_at=now,
        released_at=None,
        is_current=True,
    )
    erow = EscalationMapper.to_orm(esc)
    assert EscalationMapper.to_domain(erow).level == EscalationLevel.LEVEL_1
    esc2 = Escalation(
        escalation_id=esc.escalation_id,
        complaint_id=esc.complaint_id,
        level=EscalationLevel.LEVEL_1,
        reason=esc.reason,
        escalated_by=esc.escalated_by,
        escalated_at=now,
        released_at=now,
        is_current=False,
    )
    EscalationMapper.apply_to_orm(esc2, erow)
    assert erow.is_current is False

    policy = SLAPolicy(
        policy_id=uuid.uuid4(),
        name="default",
        target_minutes=60,
        is_default=True,
        description="d",
    )
    prow = SLAPolicyMapper.to_orm(policy)
    assert SLAPolicyMapper.to_domain(prow).name == "default"

    sla = ComplaintSLA(
        sla_id=uuid.uuid4(),
        complaint_id=uuid.uuid4(),
        policy_id=policy.policy_id,
        started_at=now,
        due_at=now,
        completed_at=None,
        breached_at=None,
        is_active=True,
        is_breached=False,
    )
    srow = ComplaintSlaMapper.to_orm(sla)
    assert ComplaintSlaMapper.to_domain(srow).is_active is True
    sla2 = ComplaintSLA(
        sla_id=sla.sla_id,
        complaint_id=sla.complaint_id,
        policy_id=sla.policy_id,
        started_at=now,
        due_at=now,
        completed_at=now,
        breached_at=None,
        is_active=False,
        is_breached=False,
    )
    ComplaintSlaMapper.apply_to_orm(sla2, srow)
    assert srow.is_active is False


@pytest.mark.asyncio
async def test_queue_counter_repository_async_paths() -> None:
    session = AsyncMock()
    repo = SqlAlchemyQueueCounterRepository(session)
    qid = uuid.uuid4()
    cid = uuid.uuid4()
    counter = MagicMock()
    counter.counter_id = cid
    row = MagicMock()
    row.queue_id = qid
    row.counter_id = cid

    with (
        patch.object(QueueCounterMapper, "to_orm", return_value=row),
        patch.object(QueueCounterMapper, "to_domain", return_value=counter),
        patch.object(QueueCounterMapper, "apply_to_orm"),
    ):
        session.get = AsyncMock(side_effect=[row, None, row, None, row])
        assert await repo.get_by_id(cid) is counter
        assert await repo.get_by_id(cid) is None
        assert await repo.get_queue_id(cid) == qid
        assert await repo.get_queue_id(cid) is None

        session.add = MagicMock()
        session.flush = AsyncMock()
        session.refresh = AsyncMock()
        assert await repo.add(qid, counter) is counter

        session.get = AsyncMock(return_value=row)
        assert await repo.update(qid, counter) is counter

        session.get = AsyncMock(return_value=None)
        with pytest.raises(KeyError):
            await repo.update(qid, counter)

        result = MagicMock()
        result.all.return_value = [row]
        session.scalars = AsyncMock(return_value=result)
        listed = await repo.list_by_queue(qid)
        assert listed == (counter,)

        exec_result = MagicMock()
        exec_result.rowcount = 1
        session.execute = AsyncMock(return_value=exec_result)
        assert await repo.delete(cid) is True
