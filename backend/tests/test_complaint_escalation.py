"""Complaint Escalation application + API tests (CAPABILITY-007)."""

from __future__ import annotations

import asyncio
import uuid
from collections.abc import Generator
from datetime import datetime, timezone
from pathlib import Path
from typing import Any
from unittest.mock import MagicMock

import pytest
import yaml
from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from fastapi.testclient import TestClient

from app.core.auth import Principal, get_current_principal
from app.core.errors import ApiError
from app.core.request_context import RequestContext, get_request_context
from app.core.schemas import ErrorResponse
from app.core.user_messages import field_errors_from_validation
from app.modules.complaint.api import complaint_foundation_router
from app.modules.complaint.api.dependencies import (
    get_complaint_assignment_service,
    get_complaint_crud_service,
    get_complaint_escalation_service,
    get_complaint_processing_service,
    get_complaint_sla_service,
)
from app.modules.complaint.application.services import (
    AssignComplaintInput,
    ComplaintApplicationError,
    ComplaintAssignmentApplicationService,
    ComplaintCrudApplicationService,
    ComplaintDomainService,
    ComplaintEscalationApplicationService,
    ComplaintProcessingApplicationService,
    CreateComplaintInput,
    EscalateComplaintInput,
)
from app.modules.complaint.domain.errors import ComplaintDomainError
from app.modules.complaint.domain.models import (
    AssigneeType,
    Assignment,
    Complaint,
    ComplaintPriority,
    ComplaintStatus,
    Escalation,
    EscalationLevel,
)
from app.modules.complaint.domain.repositories import (
    AssignmentRepository,
    ComplaintRepository,
    EscalationRepository,
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


def _services(
    complaints: InMemoryComplaintRepository | None = None,
    assignments: InMemoryAssignmentRepository | None = None,
    escalations: InMemoryEscalationRepository | None = None,
) -> tuple[
    ComplaintCrudApplicationService,
    ComplaintProcessingApplicationService,
    ComplaintAssignmentApplicationService,
    ComplaintEscalationApplicationService,
    InMemoryComplaintRepository,
    InMemoryAssignmentRepository,
    InMemoryEscalationRepository,
]:
    store = complaints if complaints is not None else InMemoryComplaintRepository()
    assign_store = (
        assignments if assignments is not None else InMemoryAssignmentRepository()
    )
    esc_store = (
        escalations if escalations is not None else InMemoryEscalationRepository()
    )
    domain = ComplaintDomainService()
    return (
        ComplaintCrudApplicationService(complaints=store, domain=domain),
        ComplaintProcessingApplicationService(complaints=store, domain=domain),
        ComplaintAssignmentApplicationService(
            complaints=store, assignments=assign_store, domain=domain
        ),
        ComplaintEscalationApplicationService(
            complaints=store, escalations=esc_store, domain=domain
        ),
        store,
        assign_store,
        esc_store,
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
    app.dependency_overrides[get_complaint_sla_service] = lambda: MagicMock()
    app.dependency_overrides[get_request_context] = _ctx
    app.dependency_overrides[get_current_principal] = _principal
    return app


@pytest.fixture()
def client() -> Generator[TestClient, None, None]:
    crud, processing, assignment, escalation, _, _, _ = _services()
    app = _foundation_app(crud, processing, assignment, escalation)
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
            title="Escalate me",
            description="Need higher handling",
        ),
    )
    return created.complaint_id


def test_first_escalation() -> None:
    crud, _processing, _assignment, escalation, store, _, esc_store = _services()

    async def scenario() -> None:
        complaint_id = await _create_complaint(crud)
        assert await escalation.list_history(_ctx(), complaint_id) == ()
        status_before = store.rows[complaint_id].status
        created = await escalation.escalate(
            _ctx(),
            complaint_id,
            EscalateComplaintInput(
                level=EscalationLevel.LEVEL_1,
                reason="Initial escalate",
                escalated_by="supervisor-1",
            ),
        )
        assert created.is_current is True
        assert created.level is EscalationLevel.LEVEL_1
        assert created.released_at is None
        assert store.rows[complaint_id].status is status_before
        assert len(esc_store.rows) == 1

    _run(scenario())


def test_escalate_higher_level() -> None:
    crud, _processing, _assignment, escalation, store, _, esc_store = _services()

    async def scenario() -> None:
        complaint_id = await _create_complaint(crud)
        first = await escalation.escalate(
            _ctx(),
            complaint_id,
            EscalateComplaintInput(
                level=EscalationLevel.LEVEL_1,
                reason="L1",
                escalated_by="supervisor-1",
            ),
        )
        status_before = store.rows[complaint_id].status
        second = await escalation.escalate(
            _ctx(),
            complaint_id,
            EscalateComplaintInput(
                level=EscalationLevel.LEVEL_3,
                reason="L3",
                escalated_by="manager-1",
            ),
        )
        assert second.is_current is True
        assert second.level is EscalationLevel.LEVEL_3
        assert second.escalation_id != first.escalation_id
        history = await escalation.list_history(_ctx(), complaint_id)
        assert len(history) == 2
        assert history[0].escalation_id == first.escalation_id
        assert history[0].is_current is False
        assert history[0].level is EscalationLevel.LEVEL_1
        assert history[0].released_at is not None
        assert history[1].is_current is True
        assert store.rows[complaint_id].status is status_before
        assert len(esc_store.rows) == 2

    _run(scenario())


def test_reject_lower_level() -> None:
    crud, _processing, _assignment, escalation, _, _, _ = _services()

    async def scenario() -> None:
        complaint_id = await _create_complaint(crud)
        await escalation.escalate(
            _ctx(),
            complaint_id,
            EscalateComplaintInput(
                level=EscalationLevel.LEVEL_3,
                reason="L3",
                escalated_by="supervisor-1",
            ),
        )
        with pytest.raises(ComplaintApplicationError) as exc:
            await escalation.escalate(
                _ctx(),
                complaint_id,
                EscalateComplaintInput(
                    level=EscalationLevel.LEVEL_2,
                    reason="down",
                    escalated_by="supervisor-1",
                ),
            )
        assert exc.value.code == "ESCALATION_LEVEL_REGRESSION"

        with pytest.raises(ComplaintApplicationError) as same:
            await escalation.escalate(
                _ctx(),
                complaint_id,
                EscalateComplaintInput(
                    level=EscalationLevel.LEVEL_3,
                    reason="same",
                    escalated_by="supervisor-1",
                ),
            )
        assert same.value.code == "ESCALATION_LEVEL_REGRESSION"

    _run(scenario())


def test_current_escalation_and_history() -> None:
    crud, _processing, _assignment, escalation, _, _, _ = _services()

    async def scenario() -> None:
        complaint_id = await _create_complaint(crud)
        with pytest.raises(ComplaintApplicationError) as missing:
            await escalation.get_current(_ctx(), complaint_id)
        assert missing.value.code == "ESCALATION_NOT_FOUND"

        created = await escalation.escalate(
            _ctx(),
            complaint_id,
            EscalateComplaintInput(
                level=EscalationLevel.LEVEL_2,
                reason="L2",
                escalated_by="supervisor-1",
            ),
        )
        current = await escalation.get_current(_ctx(), complaint_id)
        assert current.escalation_id == created.escalation_id
        assert current.is_current is True
        history = await escalation.list_history(_ctx(), complaint_id)
        assert len(history) == 1

    _run(scenario())


def test_escalation_does_not_change_assignment() -> None:
    crud, _processing, assignment, escalation, _, assign_store, _ = _services()

    async def scenario() -> None:
        complaint_id = await _create_complaint(crud)
        active = await assignment.assign(
            _ctx(),
            complaint_id,
            AssignComplaintInput(
                assignee_type=AssigneeType.USER,
                assignee_id="user-1",
                assigned_by="supervisor-1",
            ),
        )
        await escalation.escalate(
            _ctx(),
            complaint_id,
            EscalateComplaintInput(
                level=EscalationLevel.LEVEL_1,
                reason="escalate",
                escalated_by="supervisor-1",
            ),
        )
        still = await assignment.get_current(_ctx(), complaint_id)
        assert still.assignment_id == active.assignment_id
        assert still.assignee_id == "user-1"
        assert still.is_active is True
        assert len(assign_store.rows) == 1

    _run(scenario())


def test_validation_empty_reason() -> None:
    crud, _processing, _assignment, escalation, _, _, _ = _services()

    async def scenario() -> None:
        complaint_id = await _create_complaint(crud)
        with pytest.raises(ComplaintApplicationError) as exc:
            await escalation.escalate(
                _ctx(),
                complaint_id,
                EscalateComplaintInput(
                    level=EscalationLevel.LEVEL_1,
                    reason="   ",
                    escalated_by="supervisor-1",
                ),
            )
        assert exc.value.code == "VALIDATION_ERROR"

    _run(scenario())


def test_domain_escalate_does_not_change_status() -> None:
    now = datetime.now(timezone.utc)
    complaint = Complaint(
        complaint_id=_id(),
        organization_id=_id(),
        branch_id=_id(),
        queue_ticket_id=_id(),
        category="Billing",
        title="T",
        description="D",
        priority=ComplaintPriority.NORMAL,
        status=ComplaintStatus.OPEN,
        created_at=now,
        updated_at=now,
    )
    released, created = complaint.escalate(
        level=EscalationLevel.LEVEL_1,
        reason="first",
        escalated_by="supervisor-1",
        current=None,
    )
    assert released is None
    assert created.is_current is True
    assert complaint.status is ComplaintStatus.OPEN

    with pytest.raises(ComplaintDomainError) as exc:
        complaint.escalate(
            level=EscalationLevel.LEVEL_1,
            reason="same",
            escalated_by="supervisor-1",
            current=created,
        )
    assert exc.value.code == "ESCALATION_LEVEL_REGRESSION"


def test_escalation_api_integration(client: TestClient) -> None:
    create = client.post(
        "/api/v1/complaints",
        json={
            "organizationId": str(_id()),
            "branchId": str(_id()),
            "queueTicketId": str(_id()),
            "category": "Billing",
            "title": "API escalate",
            "description": "via HTTP",
        },
    )
    assert create.status_code == 201
    complaint_id = create.json()["data"]["complaintId"]
    status_open = create.json()["data"]["status"]

    missing = client.get(f"/api/v1/complaints/{complaint_id}/escalation")
    assert missing.status_code == 404

    first = client.post(
        f"/api/v1/complaints/{complaint_id}/escalate",
        json={
            "level": "LEVEL_1",
            "reason": "Initial",
            "escalatedBy": "supervisor-1",
        },
    )
    assert first.status_code == 201
    body = first.json()["data"]
    assert body["isCurrent"] is True
    assert body["level"] == "LEVEL_1"
    assert "escalationId" in body

    current = client.get(f"/api/v1/complaints/{complaint_id}/escalation")
    assert current.status_code == 200
    assert current.json()["data"]["escalationId"] == body["escalationId"]

    higher = client.post(
        f"/api/v1/complaints/{complaint_id}/escalate",
        json={
            "level": "LEVEL_2",
            "reason": "Higher",
            "escalatedBy": "manager-1",
        },
    )
    assert higher.status_code == 201
    assert higher.json()["data"]["level"] == "LEVEL_2"

    history = client.get(f"/api/v1/complaints/{complaint_id}/escalations")
    assert history.status_code == 200
    rows = history.json()["data"]
    assert len(rows) == 2
    assert rows[0]["isCurrent"] is False
    assert rows[1]["isCurrent"] is True

    lower = client.post(
        f"/api/v1/complaints/{complaint_id}/escalate",
        json={
            "level": "LEVEL_1",
            "reason": "down",
            "escalatedBy": "manager-1",
        },
    )
    assert lower.status_code == 409

    got = client.get(f"/api/v1/complaints/{complaint_id}")
    assert got.status_code == 200
    assert got.json()["data"]["status"] == status_open


def test_escalation_validation_http(client: TestClient) -> None:
    create = client.post(
        "/api/v1/complaints",
        json={
            "organizationId": str(_id()),
            "branchId": str(_id()),
            "queueTicketId": str(_id()),
            "category": "Billing",
            "title": "API validate",
            "description": "via HTTP",
        },
    )
    complaint_id = create.json()["data"]["complaintId"]
    response = client.post(
        f"/api/v1/complaints/{complaint_id}/escalate",
        json={
            "level": "LEVEL_1",
            "reason": "   ",
            "escalatedBy": "supervisor-1",
        },
    )
    assert response.status_code == 422


def test_openapi_escalation_paths() -> None:
    path = (
        Path(__file__).resolve().parents[2]
        / "07 API Catalog"
        / "openapi"
        / "complaint-domain-service.v1.yaml"
    )
    spec = yaml.safe_load(path.read_text(encoding="utf-8"))
    paths = spec["paths"]
    assert paths["/api/v1/complaints/{complaintId}/escalate"]["post"]["x-ear-id"] == (
        "API-406"
    )
    assert paths["/api/v1/complaints/{complaintId}/escalation"]["get"]["x-ear-id"] == (
        "API-407"
    )
    assert paths["/api/v1/complaints/{complaintId}/escalations"]["get"]["x-ear-id"] == (
        "API-408"
    )
    assert "EscalationLevel" in spec["components"]["schemas"]
    assert "EscalationResponse" in spec["components"]["schemas"]
