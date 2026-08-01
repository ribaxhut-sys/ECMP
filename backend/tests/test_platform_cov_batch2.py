"""Platform coverage batch 2 (TASK-PLATFORM-CI-COV-001).

Heavy MagicMock / AsyncMock coverage for low-miss repository and core modules.
Does not exercise real DB or change application business logic.
"""

from __future__ import annotations

import logging
import uuid
from datetime import UTC, datetime
from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from starlette.requests import Request
from starlette.responses import Response

from app.core import logging as logging_mod
from app.core import middleware as middleware_mod
from app.core.middleware import (
    RequestLoggingMiddleware,
    SecurityHeadersMiddleware,
    _sanitize_id,
)
from app.modules.complaint.domain.models import (
    AssigneeType,
    Assignment,
    ComplaintSLA,
    Escalation,
    EscalationLevel,
    SLAPolicy,
)
from app.modules.complaint.infrastructure.repositories import (
    assignment_repository as assign_mod,
)
from app.modules.complaint.infrastructure.repositories import (
    escalation_repository as esc_infra_mod,
)
from app.modules.complaint.infrastructure.repositories import (
    sla_repository as sla_infra_mod,
)
from app.modules.complaint.infrastructure.repositories.assignment_repository import (
    SqlAlchemyAssignmentRepository,
)
from app.modules.complaint.infrastructure.repositories.escalation_repository import (
    SqlAlchemyEscalationRepository,
)
from app.modules.complaint.infrastructure.repositories.sla_repository import (
    SqlAlchemyComplaintSlaRepository,
    SqlAlchemySLAPolicyRepository,
)
from app.modules.customers.repository import CustomerRepository
from app.modules.escalations import repository as esc_mod
from app.modules.escalations.repository import EscalationRepository


def _async_session() -> MagicMock:
    session = MagicMock()
    session.get = AsyncMock(return_value=None)
    session.scalars = AsyncMock()
    session.flush = AsyncMock()
    session.refresh = AsyncMock()
    session.add = MagicMock()
    return session


def _now() -> datetime:
    return datetime(2026, 7, 29, 10, 0, 0, tzinfo=UTC)


def _policy() -> SLAPolicy:
    return SLAPolicy(
        policy_id=uuid.uuid4(),
        name="default",
        target_minutes=60,
        is_default=True,
        description="d",
    )


def _complaint_sla() -> ComplaintSLA:
    started = _now()
    return ComplaintSLA(
        sla_id=uuid.uuid4(),
        complaint_id=uuid.uuid4(),
        policy_id=uuid.uuid4(),
        started_at=started,
        due_at=datetime(2026, 7, 29, 11, 0, 0, tzinfo=UTC),
        is_active=True,
        is_breached=False,
    )


def _escalation() -> Escalation:
    return Escalation(
        escalation_id=uuid.uuid4(),
        complaint_id=uuid.uuid4(),
        level=EscalationLevel.LEVEL_1,
        reason="need help",
        escalated_by="agent-1",
        escalated_at=_now(),
        is_current=True,
    )


def _assignment() -> Assignment:
    return Assignment(
        assignment_id=uuid.uuid4(),
        complaint_id=uuid.uuid4(),
        assignee_type=AssigneeType.USER,
        assignee_id="user-1",
        assigned_at=_now(),
        assigned_by="agent-1",
        is_active=True,
    )


# ---------------------------------------------------------------------------
# 1. SqlAlchemy SLAPolicy / ComplaintSla repositories
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_sla_policy_repo_get_by_id_none_and_hit() -> None:
    session = _async_session()
    repo = SqlAlchemySLAPolicyRepository(session)
    pid = uuid.uuid4()

    session.get = AsyncMock(return_value=None)
    assert await repo.get_by_id(pid) is None

    row = MagicMock()
    policy = _policy()
    session.get = AsyncMock(return_value=row)
    with patch.object(sla_infra_mod.SLAPolicyMapper, "to_domain", return_value=policy):
        assert await repo.get_by_id(pid) is policy


@pytest.mark.asyncio
async def test_sla_policy_repo_get_default_none_and_hit() -> None:
    session = _async_session()
    repo = SqlAlchemySLAPolicyRepository(session)

    result = MagicMock()
    result.first.return_value = None
    session.scalars = AsyncMock(return_value=result)
    assert await repo.get_default() is None

    row = MagicMock()
    result.first.return_value = row
    policy = _policy()
    with patch.object(sla_infra_mod.SLAPolicyMapper, "to_domain", return_value=policy):
        assert await repo.get_default() is policy


@pytest.mark.asyncio
async def test_sla_policy_repo_add() -> None:
    session = _async_session()
    repo = SqlAlchemySLAPolicyRepository(session)
    policy = _policy()
    orm_row = MagicMock()
    with (
        patch.object(sla_infra_mod.SLAPolicyMapper, "to_orm", return_value=orm_row),
        patch.object(sla_infra_mod.SLAPolicyMapper, "to_domain", return_value=policy) as to_dom,
    ):
        out = await repo.add(policy)
    assert out is policy
    session.add.assert_called_once_with(orm_row)
    session.flush.assert_awaited()
    session.refresh.assert_awaited_with(orm_row)
    to_dom.assert_called_once_with(orm_row)


@pytest.mark.asyncio
async def test_complaint_sla_repo_add_and_update() -> None:
    session = _async_session()
    repo = SqlAlchemyComplaintSlaRepository(session)
    sla = _complaint_sla()
    orm_row = MagicMock()

    with (
        patch.object(sla_infra_mod.ComplaintSlaMapper, "to_orm", return_value=orm_row),
        patch.object(sla_infra_mod.ComplaintSlaMapper, "to_domain", return_value=sla),
    ):
        assert await repo.add(sla) is sla
    session.add.assert_called_with(orm_row)

    session.get = AsyncMock(return_value=None)
    with pytest.raises(KeyError, match="SLA not found"):
        await repo.update(sla)

    session.get = AsyncMock(return_value=orm_row)
    with (
        patch.object(sla_infra_mod.ComplaintSlaMapper, "apply_to_orm") as apply,
        patch.object(sla_infra_mod.ComplaintSlaMapper, "to_domain", return_value=sla),
    ):
        assert await repo.update(sla) is sla
    apply.assert_called_once_with(sla, orm_row)
    session.flush.assert_awaited()
    session.refresh.assert_awaited_with(orm_row)


@pytest.mark.asyncio
async def test_complaint_sla_repo_get_paths() -> None:
    session = _async_session()
    repo = SqlAlchemyComplaintSlaRepository(session)
    sla = _complaint_sla()
    cid = sla.complaint_id
    sid = sla.sla_id

    session.get = AsyncMock(return_value=None)
    assert await repo.get_by_id(sid) is None

    row = MagicMock()
    session.get = AsyncMock(return_value=row)
    with patch.object(sla_infra_mod.ComplaintSlaMapper, "to_domain", return_value=sla):
        assert await repo.get_by_id(sid) is sla

    result = MagicMock()
    result.first.return_value = None
    session.scalars = AsyncMock(return_value=result)
    assert await repo.get_active_by_complaint(cid) is None
    assert await repo.get_latest_by_complaint(cid) is None

    result.first.return_value = row
    with patch.object(sla_infra_mod.ComplaintSlaMapper, "to_domain", return_value=sla):
        assert await repo.get_active_by_complaint(cid) is sla
        assert await repo.get_latest_by_complaint(cid) is sla


# ---------------------------------------------------------------------------
# 2. SqlAlchemy Escalation repository
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_infra_escalation_repo_add_update_get() -> None:
    session = _async_session()
    repo = SqlAlchemyEscalationRepository(session)
    esc = _escalation()
    orm_row = MagicMock()

    with (
        patch.object(esc_infra_mod.EscalationMapper, "to_orm", return_value=orm_row),
        patch.object(esc_infra_mod.EscalationMapper, "to_domain", return_value=esc),
    ):
        assert await repo.add(esc) is esc
    session.add.assert_called_with(orm_row)
    session.flush.assert_awaited()
    session.refresh.assert_awaited_with(orm_row)

    session.get = AsyncMock(return_value=None)
    with pytest.raises(KeyError, match="escalation not found"):
        await repo.update(esc)

    session.get = AsyncMock(return_value=orm_row)
    with (
        patch.object(esc_infra_mod.EscalationMapper, "apply_to_orm") as apply,
        patch.object(esc_infra_mod.EscalationMapper, "to_domain", return_value=esc),
    ):
        assert await repo.update(esc) is esc
    apply.assert_called_once_with(esc, orm_row)

    session.get = AsyncMock(return_value=None)
    assert await repo.get_by_id(esc.escalation_id) is None
    session.get = AsyncMock(return_value=orm_row)
    with patch.object(esc_infra_mod.EscalationMapper, "to_domain", return_value=esc):
        assert await repo.get_by_id(esc.escalation_id) is esc


@pytest.mark.asyncio
async def test_infra_escalation_repo_current_and_list() -> None:
    session = _async_session()
    repo = SqlAlchemyEscalationRepository(session)
    esc = _escalation()
    cid = esc.complaint_id
    row = MagicMock()

    result = MagicMock()
    result.first.return_value = None
    session.scalars = AsyncMock(return_value=result)
    assert await repo.get_current_by_complaint(cid) is None

    result.first.return_value = row
    with patch.object(esc_infra_mod.EscalationMapper, "to_domain", return_value=esc):
        assert await repo.get_current_by_complaint(cid) is esc

    result.all.return_value = [row, row]
    with patch.object(esc_infra_mod.EscalationMapper, "to_domain", return_value=esc):
        listed = await repo.list_by_complaint(cid)
    assert listed == (esc, esc)


# ---------------------------------------------------------------------------
# 3. SqlAlchemy Assignment repository
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_infra_assignment_repo_add_update_get() -> None:
    session = _async_session()
    repo = SqlAlchemyAssignmentRepository(session)
    asn = _assignment()
    orm_row = MagicMock()

    with (
        patch.object(assign_mod.AssignmentMapper, "to_orm", return_value=orm_row),
        patch.object(assign_mod.AssignmentMapper, "to_domain", return_value=asn),
    ):
        assert await repo.add(asn) is asn
    session.add.assert_called_with(orm_row)

    session.get = AsyncMock(return_value=None)
    with pytest.raises(KeyError, match="assignment not found"):
        await repo.update(asn)

    session.get = AsyncMock(return_value=orm_row)
    with (
        patch.object(assign_mod.AssignmentMapper, "apply_to_orm") as apply,
        patch.object(assign_mod.AssignmentMapper, "to_domain", return_value=asn),
    ):
        assert await repo.update(asn) is asn
    apply.assert_called_once_with(asn, orm_row)

    session.get = AsyncMock(return_value=None)
    assert await repo.get_by_id(asn.assignment_id) is None
    session.get = AsyncMock(return_value=orm_row)
    with patch.object(assign_mod.AssignmentMapper, "to_domain", return_value=asn):
        assert await repo.get_by_id(asn.assignment_id) is asn


@pytest.mark.asyncio
async def test_infra_assignment_repo_active_and_list() -> None:
    session = _async_session()
    repo = SqlAlchemyAssignmentRepository(session)
    asn = _assignment()
    cid = asn.complaint_id
    row = MagicMock()

    result = MagicMock()
    result.first.return_value = None
    session.scalars = AsyncMock(return_value=result)
    assert await repo.get_active_by_complaint(cid) is None

    result.first.return_value = row
    with patch.object(assign_mod.AssignmentMapper, "to_domain", return_value=asn):
        assert await repo.get_active_by_complaint(cid) is asn

    result.all.return_value = [row]
    with patch.object(assign_mod.AssignmentMapper, "to_domain", return_value=asn):
        listed = await repo.list_by_complaint(cid)
    assert listed == (asn,)


# ---------------------------------------------------------------------------
# 4. Escalations module repository (sync Session)
# ---------------------------------------------------------------------------


def test_escalation_repo_lookup_helpers() -> None:
    session = MagicMock()
    repo = EscalationRepository(session)
    assert repo.session is session
    cid = uuid.uuid4()
    uid = uuid.uuid4()
    eid = uuid.uuid4()

    complaint = MagicMock()
    esc = MagicMock()
    appt = MagicMock()
    user = MagicMock()
    resolution = MagicMock()

    session.scalar.side_effect = [
        complaint,
        esc,
        appt,
        uid,
        None,
        user,
        uid,
        None,
        uid,
        uid,
        resolution,
        esc,
        esc,
        3,
    ]
    assert repo.get_complaint(cid) is complaint
    assert repo.get_by_id(eid) is esc
    assert repo.get_active_appointment(eid) is appt
    assert repo.user_exists(uid) is True
    assert repo.user_exists(uid) is False
    assert repo.get_user(uid) is user
    assert repo.role_exists(uid) is True
    assert repo.role_exists(uid) is False
    assert repo.get_current_assignee_id(cid) == uid
    assert repo.has_current_resolution(cid) is True
    assert repo.get_final_resolution(cid) is resolution
    assert repo.get_active_escalation(cid) is esc
    assert repo.get_latest_request_escalation(cid) is esc
    assert repo.next_level(cid) == 4


def test_escalation_repo_next_level_when_none() -> None:
    session = MagicMock()
    repo = EscalationRepository(session)
    session.scalar.return_value = None
    assert repo.next_level(uuid.uuid4()) == 1


def test_escalation_repo_list_add_timeline_commit_refresh() -> None:
    session = MagicMock()
    repo = EscalationRepository(session)
    cid = uuid.uuid4()
    actor = uuid.uuid4()
    esc = MagicMock()

    session.scalars.return_value.unique.return_value.all.return_value = [esc]
    assert repo.list_escalations(cid) == [esc]

    assert repo.add_escalation(esc) is esc
    session.add.assert_called_with(esc)
    session.flush.assert_called()

    timeline = MagicMock()
    with patch.object(esc_mod, "ComplaintTimeline", return_value=timeline) as ctor:
        entry = repo.add_timeline(
            complaint_id=cid,
            actor_user_id=actor,
            event_type="ESCALATED",
            event_at=datetime(2026, 1, 1, 8, 0, 0),  # naive → UTC
            from_status="OPEN",
            to_status="ESCALATED",
            summary="escalated",
            metadata={"k": "v"},
        )
    assert entry is timeline
    ctor.assert_called_once()
    kwargs = ctor.call_args.kwargs
    assert kwargs["event_at"].tzinfo is UTC
    assert kwargs["metadata_json"] == {"k": "v"}

    aware = datetime(2026, 1, 1, 9, 0, 0, tzinfo=UTC)
    with patch.object(esc_mod, "ComplaintTimeline", return_value=timeline):
        repo.add_timeline(
            complaint_id=cid,
            actor_user_id=actor,
            event_type="NOTE",
            event_at=aware,
            from_status=None,
            to_status=None,
            summary="note",
        )

    repo.commit()
    session.commit.assert_called_once()
    assert repo.refresh(esc) is esc
    session.refresh.assert_called_with(esc)


# ---------------------------------------------------------------------------
# 5. Customers repository
# ---------------------------------------------------------------------------


def test_customer_repo_list_page_with_and_without_q() -> None:
    session = MagicMock()
    repo = CustomerRepository(session)
    customer = MagicMock()

    session.scalar.return_value = 0
    session.scalars.return_value.all.return_value = []
    items, total = repo.list_page(page=1, page_size=10)
    assert items == []
    assert total == 0

    session.scalar.return_value = 2
    session.scalars.return_value.all.return_value = [customer, customer]
    items, total = repo.list_page(page=2, page_size=5, q="  acme  ")
    assert total == 2
    assert items == [customer, customer]


# ---------------------------------------------------------------------------
# 6. Middleware — sanitize + exception path + security headers
# ---------------------------------------------------------------------------


def test_sanitize_id_branches() -> None:
    assert _sanitize_id(None) is None
    assert _sanitize_id("") is None
    assert _sanitize_id("   ") is None
    assert _sanitize_id("x" * 129) is None
    assert _sanitize_id("bad\x00id") is None
    assert _sanitize_id("  ok-id  ") == "ok-id"


@pytest.mark.asyncio
async def test_request_logging_middleware_success_and_exception() -> None:
    app = MagicMock()
    mw = RequestLoggingMiddleware(app)

    scope = {
        "type": "http",
        "asgi": {"version": "3.0"},
        "http_version": "1.1",
        "method": "GET",
        "scheme": "http",
        "path": "/health",
        "raw_path": b"/health",
        "query_string": b"",
        "headers": [(b"x-request-id", b"req-123")],
        "client": ("127.0.0.1", 123),
        "server": ("test", 80),
    }
    request = Request(scope)

    async def ok_next(_req: Request) -> Response:
        return Response(content=b"ok", status_code=200)

    with patch.object(middleware_mod, "logger") as log:
        resp = await mw.dispatch(request, ok_next)
    assert resp.status_code == 200
    assert resp.headers["X-Request-ID"] == "req-123"
    log.info.assert_called()

    async def boom_next(_req: Request) -> Response:
        raise RuntimeError("fail")

    with patch.object(middleware_mod, "logger") as log:
        with pytest.raises(RuntimeError, match="fail"):
            await mw.dispatch(request, boom_next)
    log.exception.assert_called()
    log.info.assert_called()


@pytest.mark.asyncio
async def test_security_headers_middleware() -> None:
    app = MagicMock()
    mw = SecurityHeadersMiddleware(app)
    scope = {
        "type": "http",
        "asgi": {"version": "3.0"},
        "http_version": "1.1",
        "method": "GET",
        "scheme": "http",
        "path": "/",
        "raw_path": b"/",
        "query_string": b"",
        "headers": [],
        "client": ("127.0.0.1", 123),
        "server": ("test", 80),
    }
    request = Request(scope)

    async def ok_next(_req: Request) -> Response:
        return Response(content=b"ok", status_code=204)

    resp = await mw.dispatch(request, ok_next)
    assert resp.headers["X-Content-Type-Options"] == "nosniff"
    assert resp.headers["X-Frame-Options"] == "DENY"


# ---------------------------------------------------------------------------
# 7. Logging helpers
# ---------------------------------------------------------------------------


def test_configure_logging_existing_handlers_and_fresh() -> None:
    existing = MagicMock()
    existing.handlers = [MagicMock()]
    with patch.object(logging_mod.logging, "getLogger", return_value=existing):
        logging_mod.configure_logging("debug")
    existing.setLevel.assert_called_with("DEBUG")

    fresh = MagicMock()
    fresh.handlers = []
    handler = MagicMock()
    with (
        patch.object(logging_mod.logging, "getLogger", return_value=fresh),
        patch.object(logging_mod.logging, "StreamHandler", return_value=handler),
        patch.object(logging_mod.logging, "Formatter", return_value=MagicMock()),
    ):
        logging_mod.configure_logging("WARNING")
    fresh.addHandler.assert_called_once_with(handler)
    fresh.setLevel.assert_called_with("WARNING")


def test_get_logger_and_log_extra() -> None:
    log = logging_mod.get_logger("app.test.cov")
    assert isinstance(log, logging.Logger)
    assert log.name == "app.test.cov"
    extra = logging_mod.log_extra(a=1, b="x")
    assert extra == {"extra_fields": {"a": 1, "b": "x"}}
