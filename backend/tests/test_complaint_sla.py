"""Complaint SLA application + API tests (CAPABILITY-008)."""

from __future__ import annotations

import asyncio
import uuid
from collections.abc import Generator
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any

import pytest
import yaml
from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from app.core.user_messages import field_errors_from_validation
from fastapi.responses import JSONResponse
from fastapi.testclient import TestClient

from app.core.auth import Principal, get_current_principal
from app.core.errors import ApiError
from app.core.request_context import RequestContext, get_request_context
from app.core.schemas import ErrorResponse
from app.modules.complaint.api import complaint_foundation_router
from app.modules.complaint.api.dependencies import (
    get_complaint_assignment_service,
    get_complaint_crud_service,
    get_complaint_escalation_service,
    get_complaint_processing_service,
    get_complaint_sla_service,
)
from app.modules.complaint.application.services import (
    ComplaintApplicationError,
    ComplaintAssignmentApplicationService,
    ComplaintCrudApplicationService,
    ComplaintDomainService,
    ComplaintEscalationApplicationService,
    ComplaintProcessingApplicationService,
    ComplaintSLAApplicationService,
    CreateComplaintInput,
    RecalculateSlaInput,
    ResolveComplaintInput,
    StartSlaInput,
)
from app.modules.complaint.domain.errors import ComplaintDomainError
from app.modules.complaint.domain.models import (
    Assignment,
    Complaint,
    ComplaintPriority,
    ComplaintSLA,
    ComplaintStatus,
    Escalation,
    SLAPolicy,
)
from app.modules.complaint.domain.repositories import (
    AssignmentRepository,
    ComplaintRepository,
    ComplaintSlaRepository,
    EscalationRepository,
    SLAPolicyRepository,
)


def _run(coro: Any) -> Any:
    return asyncio.run(coro)


def _id() -> uuid.UUID:
    return uuid.uuid4()


def _ctx() -> RequestContext:
    return RequestContext(
        request_id="test-request-id",
        correlation_id="test-correlation-id",
    )


def _principal() -> Principal:
    return Principal(
        user_id=uuid.uuid4(),
        roles=("AGENT",),
        permissions=frozenset(
            {
                "complaints:create",
                "complaints:read",
                "complaints:update",
                "complaints:delete",
            }
        ),
    )


def _now() -> datetime:
    return datetime(2026, 7, 24, 10, 0, 0, tzinfo=timezone.utc)


class InMemoryComplaintRepository(ComplaintRepository):
    def __init__(self) -> None:
        self.rows: dict[uuid.UUID, Complaint] = {}

    async def add(self, complaint: Complaint) -> Complaint:
        self.rows[complaint.complaint_id] = complaint
        return complaint

    async def get_by_id(self, complaint_id: uuid.UUID) -> Complaint | None:
        return self.rows.get(complaint_id)

    async def update(self, complaint: Complaint) -> Complaint:
        if complaint.complaint_id not in self.rows:
            raise KeyError(complaint.complaint_id)
        self.rows[complaint.complaint_id] = complaint
        return complaint

    async def list_by_organization(
        self, organization_id: uuid.UUID
    ) -> tuple[Complaint, ...]:
        items = [
            c for c in self.rows.values() if c.organization_id == organization_id
        ]
        items.sort(key=lambda c: (c.created_at, str(c.complaint_id)))
        return tuple(items)

    async def list_by_queue_ticket(
        self, queue_ticket_id: uuid.UUID
    ) -> tuple[Complaint, ...]:
        items = [
            c for c in self.rows.values() if c.queue_ticket_id == queue_ticket_id
        ]
        items.sort(key=lambda c: (c.created_at, str(c.complaint_id)))
        return tuple(items)

    async def delete(self, complaint_id: uuid.UUID) -> bool:
        return self.rows.pop(complaint_id, None) is not None


class InMemoryAssignmentRepository(AssignmentRepository):
    def __init__(self) -> None:
        self.rows: dict[uuid.UUID, Assignment] = {}

    async def add(self, assignment: Assignment) -> Assignment:
        self.rows[assignment.assignment_id] = assignment
        return assignment

    async def update(self, assignment: Assignment) -> Assignment:
        if assignment.assignment_id not in self.rows:
            raise KeyError(assignment.assignment_id)
        self.rows[assignment.assignment_id] = assignment
        return assignment

    async def get_by_id(self, assignment_id: uuid.UUID) -> Assignment | None:
        return self.rows.get(assignment_id)

    async def get_active_by_complaint(
        self, complaint_id: uuid.UUID
    ) -> Assignment | None:
        for row in self.rows.values():
            if row.complaint_id == complaint_id and row.is_active:
                return row
        return None

    async def list_by_complaint(
        self, complaint_id: uuid.UUID
    ) -> tuple[Assignment, ...]:
        items = [r for r in self.rows.values() if r.complaint_id == complaint_id]
        items.sort(key=lambda a: (a.assigned_at, str(a.assignment_id)))
        return tuple(items)


class InMemoryEscalationRepository(EscalationRepository):
    def __init__(self) -> None:
        self.rows: dict[uuid.UUID, Escalation] = {}

    async def add(self, escalation: Escalation) -> Escalation:
        self.rows[escalation.escalation_id] = escalation
        return escalation

    async def update(self, escalation: Escalation) -> Escalation:
        if escalation.escalation_id not in self.rows:
            raise KeyError(escalation.escalation_id)
        self.rows[escalation.escalation_id] = escalation
        return escalation

    async def get_by_id(self, escalation_id: uuid.UUID) -> Escalation | None:
        return self.rows.get(escalation_id)

    async def get_current_by_complaint(
        self, complaint_id: uuid.UUID
    ) -> Escalation | None:
        for row in self.rows.values():
            if row.complaint_id == complaint_id and row.is_current:
                return row
        return None

    async def list_by_complaint(
        self, complaint_id: uuid.UUID
    ) -> tuple[Escalation, ...]:
        items = [r for r in self.rows.values() if r.complaint_id == complaint_id]
        items.sort(key=lambda e: (e.escalated_at, str(e.escalation_id)))
        return tuple(items)


class InMemorySLAPolicyRepository(SLAPolicyRepository):
    def __init__(self, default: SLAPolicy | None = None) -> None:
        self.rows: dict[uuid.UUID, SLAPolicy] = {}
        if default is not None:
            self.rows[default.policy_id] = default

    async def get_by_id(self, policy_id: uuid.UUID) -> SLAPolicy | None:
        return self.rows.get(policy_id)

    async def get_default(self) -> SLAPolicy | None:
        for row in self.rows.values():
            if row.is_default:
                return row
        return None

    async def add(self, policy: SLAPolicy) -> SLAPolicy:
        self.rows[policy.policy_id] = policy
        return policy


class InMemoryComplaintSlaRepository(ComplaintSlaRepository):
    def __init__(self) -> None:
        self.rows: dict[uuid.UUID, ComplaintSLA] = {}

    async def add(self, sla: ComplaintSLA) -> ComplaintSLA:
        self.rows[sla.sla_id] = sla
        return sla

    async def update(self, sla: ComplaintSLA) -> ComplaintSLA:
        if sla.sla_id not in self.rows:
            raise KeyError(sla.sla_id)
        self.rows[sla.sla_id] = sla
        return sla

    async def get_by_id(self, sla_id: uuid.UUID) -> ComplaintSLA | None:
        return self.rows.get(sla_id)

    async def get_active_by_complaint(
        self, complaint_id: uuid.UUID
    ) -> ComplaintSLA | None:
        for row in self.rows.values():
            if row.complaint_id == complaint_id and row.is_active:
                return row
        return None

    async def get_latest_by_complaint(
        self, complaint_id: uuid.UUID
    ) -> ComplaintSLA | None:
        items = [r for r in self.rows.values() if r.complaint_id == complaint_id]
        if not items:
            return None
        items.sort(
            key=lambda s: (s.is_active, s.started_at, str(s.sla_id)), reverse=True
        )
        return items[0]


def _default_policy(*, minutes: int = 60) -> SLAPolicy:
    return SLAPolicy(
        policy_id=_id(),
        name="Default Test Policy",
        target_minutes=minutes,
        is_default=True,
        description="test default",
    )


def _services(
    *,
    policy: SLAPolicy | None = None,
) -> tuple[
    ComplaintCrudApplicationService,
    ComplaintProcessingApplicationService,
    ComplaintAssignmentApplicationService,
    ComplaintEscalationApplicationService,
    ComplaintSLAApplicationService,
    InMemoryComplaintRepository,
    InMemoryComplaintSlaRepository,
    InMemorySLAPolicyRepository,
]:
    store = InMemoryComplaintRepository()
    assign_store = InMemoryAssignmentRepository()
    esc_store = InMemoryEscalationRepository()
    sla_store = InMemoryComplaintSlaRepository()
    policy_store = InMemorySLAPolicyRepository(
        default=policy if policy is not None else _default_policy()
    )
    domain = ComplaintDomainService()
    return (
        ComplaintCrudApplicationService(complaints=store, domain=domain),
        ComplaintProcessingApplicationService(
            complaints=store, domain=domain, slas=sla_store
        ),
        ComplaintAssignmentApplicationService(
            complaints=store, assignments=assign_store, domain=domain
        ),
        ComplaintEscalationApplicationService(
            complaints=store, escalations=esc_store, domain=domain
        ),
        ComplaintSLAApplicationService(
            complaints=store,
            slas=sla_store,
            policies=policy_store,
            domain=domain,
        ),
        store,
        sla_store,
        policy_store,
    )


def _error_body(
    code: str,
    message: str,
    details: dict[str, Any] | None = None,
) -> dict[str, Any]:
    return ErrorResponse(code=code, message=message, details=details).model_dump()


def _foundation_app(
    crud: ComplaintCrudApplicationService,
    processing: ComplaintProcessingApplicationService,
    assignment: ComplaintAssignmentApplicationService,
    escalation: ComplaintEscalationApplicationService,
    sla: ComplaintSLAApplicationService,
) -> FastAPI:
    app = FastAPI()
    app.include_router(complaint_foundation_router)

    @app.exception_handler(ApiError)
    async def api_error_handler(_: Request, exc: ApiError) -> JSONResponse:
        return JSONResponse(
            status_code=exc.status_code,
            content=_error_body(exc.code, exc.message, exc.details),
        )

    @app.exception_handler(RequestValidationError)
    async def validation_error_handler(
        _: Request, exc: RequestValidationError
    ) -> JSONResponse:
        field_errors = field_errors_from_validation(exc.errors())
        return JSONResponse(
            status_code=422,
            content=_error_body(
                "VALIDATION_ERROR",
                "Validasi permintaan gagal.",
                field_errors or None,
            ),
        )

    app.dependency_overrides[get_complaint_crud_service] = lambda: crud
    app.dependency_overrides[get_complaint_processing_service] = lambda: processing
    app.dependency_overrides[get_complaint_assignment_service] = lambda: assignment
    app.dependency_overrides[get_complaint_escalation_service] = lambda: escalation
    app.dependency_overrides[get_complaint_sla_service] = lambda: sla
    app.dependency_overrides[get_request_context] = _ctx
    app.dependency_overrides[get_current_principal] = _principal
    return app


@pytest.fixture()
def client() -> Generator[TestClient, None, None]:
    crud, processing, assignment, escalation, sla, _, _, _ = _services()
    app = _foundation_app(crud, processing, assignment, escalation, sla)
    with TestClient(app) as test_client:
        yield test_client


async def _create_complaint(
    crud: ComplaintCrudApplicationService,
) -> uuid.UUID:
    created = await crud.create_complaint(
        _ctx(),
        CreateComplaintInput(
            organization_id=_id(),
            branch_id=_id(),
            queue_ticket_id=_id(),
            category="Billing",
            title="SLA me",
            description="Need SLA tracking",
        ),
    )
    return created.complaint_id


# --- Domain ---


def test_domain_start_sla_due_time() -> None:
    now = _now()
    complaint = Complaint(
        complaint_id=_id(),
        organization_id=_id(),
        branch_id=_id(),
        queue_ticket_id=_id(),
        category="Billing",
        title="t",
        description="d",
        priority=ComplaintPriority.NORMAL,
        status=ComplaintStatus.OPEN,
        created_at=now,
        updated_at=now,
    )
    policy = SLAPolicy(
        policy_id=_id(),
        name="60m",
        target_minutes=60,
        is_default=True,
    )
    sla = complaint.start_sla(policy=policy, active=None, now=now)
    assert sla.due_at == now + timedelta(minutes=60)
    assert sla.is_active is True
    assert sla.is_breached is False
    assert sla.remaining_minutes(current_time=now) == 60
    assert sla.remaining_minutes(current_time=now + timedelta(minutes=15)) == 45


def test_domain_one_active_sla() -> None:
    now = _now()
    complaint = Complaint(
        complaint_id=_id(),
        organization_id=_id(),
        branch_id=_id(),
        queue_ticket_id=_id(),
        category="Billing",
        title="t",
        description="d",
        priority=ComplaintPriority.NORMAL,
        status=ComplaintStatus.OPEN,
        created_at=now,
        updated_at=now,
    )
    policy = SLAPolicy(
        policy_id=_id(), name="60m", target_minutes=60, is_default=True
    )
    active = complaint.start_sla(policy=policy, active=None, now=now)
    with pytest.raises(ComplaintDomainError) as exc:
        complaint.start_sla(policy=policy, active=active, now=now)
    assert exc.value.code == "ACTIVE_SLA_EXISTS"


def test_domain_breach_detection_once() -> None:
    now = _now()
    sla = ComplaintSLA(
        sla_id=_id(),
        complaint_id=_id(),
        policy_id=_id(),
        started_at=now,
        due_at=now + timedelta(minutes=30),
        is_active=True,
        is_breached=False,
    )
    before = sla.detect_breach(current_time=now + timedelta(minutes=10))
    assert before.is_breached is False
    breached = sla.detect_breach(current_time=now + timedelta(minutes=31))
    assert breached.is_breached is True
    assert breached.breached_at == now + timedelta(minutes=31)
    again = breached.detect_breach(current_time=now + timedelta(hours=2))
    assert again.breached_at == breached.breached_at


# --- Application ---


def test_start_sla() -> None:
    crud, _p, _a, _e, sla_svc, store, sla_store, policies = _services()

    async def scenario() -> None:
        complaint_id = await _create_complaint(crud)
        status_before = store.rows[complaint_id].status
        started = await sla_svc.start(
            _ctx(),
            complaint_id,
            StartSlaInput(started_at=_now()),
        )
        assert started.is_active is True
        assert started.target_minutes == 60
        assert started.due_at == started.started_at + timedelta(minutes=60)
        assert started.remaining_minutes == 60
        assert store.rows[complaint_id].status is status_before
        assert len(sla_store.rows) == 1
        assert await policies.get_default() is not None

    _run(scenario())


def test_one_active_sla_application() -> None:
    crud, _p, _a, _e, sla_svc, _, _, _ = _services()

    async def scenario() -> None:
        complaint_id = await _create_complaint(crud)
        await sla_svc.start(_ctx(), complaint_id, StartSlaInput(started_at=_now()))
        with pytest.raises(ComplaintApplicationError) as exc:
            await sla_svc.start(_ctx(), complaint_id, StartSlaInput(started_at=_now()))
        assert exc.value.code == "ACTIVE_SLA_EXISTS"

    _run(scenario())


def test_complete_sla() -> None:
    crud, _p, _a, _e, sla_svc, store, _, _ = _services()

    async def scenario() -> None:
        complaint_id = await _create_complaint(crud)
        await sla_svc.start(_ctx(), complaint_id, StartSlaInput(started_at=_now()))
        status_before = store.rows[complaint_id].status
        done = await sla_svc.complete(_ctx(), complaint_id, now=_now())
        assert done.is_active is False
        assert done.completed_at is not None
        assert done.remaining_minutes == 0
        assert store.rows[complaint_id].status is status_before

    _run(scenario())


def test_breach_and_recalculate() -> None:
    crud, _p, _a, _e, sla_svc, _, _, _ = _services(
        policy=_default_policy(minutes=30)
    )

    async def scenario() -> None:
        complaint_id = await _create_complaint(crud)
        start = _now()
        await sla_svc.start(
            _ctx(), complaint_id, StartSlaInput(started_at=start)
        )
        current = start + timedelta(minutes=45)
        result = await sla_svc.recalculate(
            _ctx(),
            complaint_id,
            RecalculateSlaInput(current_time=current),
        )
        assert result.is_breached is True
        assert result.breached_at == current
        assert result.remaining_minutes == -15
        # Idempotent breached_at
        later = await sla_svc.recalculate(
            _ctx(),
            complaint_id,
            RecalculateSlaInput(current_time=current + timedelta(hours=1)),
        )
        assert later.breached_at == current

    _run(scenario())


def test_close_completes_active_sla() -> None:
    crud, processing, _a, _e, sla_svc, store, sla_store, _ = _services()

    async def scenario() -> None:
        complaint_id = await _create_complaint(crud)
        await processing.start_processing(_ctx(), complaint_id)
        await processing.resolve(
            _ctx(),
            complaint_id,
            ResolveComplaintInput(summary="fixed", resolved_by="agent-1"),
        )
        await sla_svc.start(_ctx(), complaint_id, StartSlaInput(started_at=_now()))
        assert (await sla_store.get_active_by_complaint(complaint_id)) is not None
        closed = await processing.close(_ctx(), complaint_id)
        assert closed.status is ComplaintStatus.CLOSED
        active = await sla_store.get_active_by_complaint(complaint_id)
        assert active is None
        latest = await sla_store.get_latest_by_complaint(complaint_id)
        assert latest is not None
        assert latest.is_active is False
        assert latest.completed_at is not None
        assert store.rows[complaint_id].status is ComplaintStatus.CLOSED

    _run(scenario())


def test_sla_does_not_create_escalation() -> None:
    crud, _p, _a, escalation, sla_svc, _, _, _ = _services()

    async def scenario() -> None:
        complaint_id = await _create_complaint(crud)
        await sla_svc.start(_ctx(), complaint_id, StartSlaInput(started_at=_now()))
        history = await escalation.list_history(_ctx(), complaint_id)
        assert history == ()
        with pytest.raises(ComplaintApplicationError) as exc:
            await escalation.get_current(_ctx(), complaint_id)
        assert exc.value.code == "ESCALATION_NOT_FOUND"

    _run(scenario())


def test_validation_policy_required() -> None:
    crud, _p, _a, _e, sla_svc, _, _, policies = _services()
    policies.rows.clear()

    async def scenario() -> None:
        complaint_id = await _create_complaint(crud)
        with pytest.raises(ComplaintApplicationError) as exc:
            await sla_svc.start(_ctx(), complaint_id)
        assert exc.value.code == "SLA_POLICY_NOT_FOUND"

    _run(scenario())


# --- API ---


def test_api_start_get_complete_recalculate(client: TestClient) -> None:
    create = client.post(
        "/api/v1/complaints",
        json={
            "organizationId": str(_id()),
            "branchId": str(_id()),
            "queueTicketId": str(_id()),
            "category": "Billing",
            "title": "API SLA",
            "description": "via http",
        },
    )
    assert create.status_code == 201
    complaint_id = create.json()["data"]["complaintId"]

    started = client.post(f"/api/v1/complaints/{complaint_id}/sla/start", json={})
    assert started.status_code == 201
    body = started.json()["data"]
    assert body["isActive"] is True
    assert body["targetMinutes"] == 60
    assert body["isBreached"] is False

    got = client.get(f"/api/v1/complaints/{complaint_id}/sla")
    assert got.status_code == 200
    assert got.json()["data"]["slaId"] == body["slaId"]

    conflict = client.post(f"/api/v1/complaints/{complaint_id}/sla/start", json={})
    assert conflict.status_code == 409

    due = datetime.fromisoformat(body["dueAt"].replace("Z", "+00:00"))
    past = (due + timedelta(minutes=5)).isoformat().replace("+00:00", "Z")
    recalc = client.post(
        f"/api/v1/complaints/{complaint_id}/sla/recalculate",
        json={"currentTime": past},
    )
    assert recalc.status_code == 200
    assert recalc.json()["data"]["isBreached"] is True

    done = client.post(f"/api/v1/complaints/{complaint_id}/sla/complete")
    assert done.status_code == 200
    assert done.json()["data"]["isActive"] is False
    assert done.json()["data"]["completedAt"] is not None


def test_api_recalculate_validation(client: TestClient) -> None:
    create = client.post(
        "/api/v1/complaints",
        json={
            "organizationId": str(_id()),
            "branchId": str(_id()),
            "queueTicketId": str(_id()),
            "category": "Billing",
            "title": "API SLA",
            "description": "via http",
        },
    )
    complaint_id = create.json()["data"]["complaintId"]
    client.post(f"/api/v1/complaints/{complaint_id}/sla/start", json={})
    bad = client.post(
        f"/api/v1/complaints/{complaint_id}/sla/recalculate",
        json={},
    )
    assert bad.status_code == 422


def test_openapi_contract_includes_sla() -> None:
    root = Path(__file__).resolve().parents[2]
    path = root / "07 API Catalog" / "openapi" / "complaint-domain-service.v1.yaml"
    assert path.exists(), path
    doc = yaml.safe_load(path.read_text(encoding="utf-8"))
    assert doc["info"]["version"] == "1.4.0"
    paths = doc["paths"]
    assert "/api/v1/complaints/{complaintId}/sla/start" in paths
    assert "/api/v1/complaints/{complaintId}/sla/complete" in paths
    assert "/api/v1/complaints/{complaintId}/sla/recalculate" in paths
    assert "/api/v1/complaints/{complaintId}/sla" in paths
    assert (
        paths["/api/v1/complaints/{complaintId}/sla/start"]["post"]["x-ear-id"]
        == "API-409"
    )
    assert paths["/api/v1/complaints/{complaintId}/sla"]["get"]["x-ear-id"] == "API-412"
    schemas = doc["components"]["schemas"]
    assert "StartSLARequest" in schemas
    assert "ComplaintSLAResponse" in schemas
    assert "RecalculateRequest" in schemas
