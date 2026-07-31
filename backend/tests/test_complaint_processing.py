"""Complaint Processing application + API tests (CAPABILITY-005)."""

from __future__ import annotations

import asyncio
import uuid
from collections.abc import Generator
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
    CreateComplaintInput,
    ReopenComplaintInput,
    ResolveComplaintInput,
)
from app.modules.complaint.domain.models import (
    Assignment,
    Complaint,
    ComplaintStatus,
    Escalation,
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
    repo: InMemoryComplaintRepository | None = None,
) -> tuple[
    ComplaintCrudApplicationService,
    ComplaintProcessingApplicationService,
    ComplaintAssignmentApplicationService,
    ComplaintEscalationApplicationService,
]:
    store = repo if repo is not None else InMemoryComplaintRepository()
    assignments = InMemoryAssignmentRepository()
    domain = ComplaintDomainService()
    return (
        ComplaintCrudApplicationService(complaints=store, domain=domain),
        ComplaintProcessingApplicationService(complaints=store, domain=domain),
        ComplaintAssignmentApplicationService(
            complaints=store, assignments=assignments, domain=domain
        ),
        ComplaintEscalationApplicationService(
            complaints=store,
            escalations=InMemoryEscalationRepository(),
            domain=domain,
        ),
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
    assignment: ComplaintAssignmentApplicationService | None = None,
    escalation: ComplaintEscalationApplicationService | None = None,
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
        field_errors: dict[str, Any] = {}
        for err in exc.errors():
            loc = err.get("loc", ())
            key = ".".join(str(part) for part in loc if part != "body")
            field_errors[key or "body"] = err.get("msg")
        return JSONResponse(
            status_code=422,
            content=_error_body(
                "VALIDATION_ERROR",
                "Request validation failed",
                field_errors or None,
            ),
        )

    if assignment is None:
        assignment = ComplaintAssignmentApplicationService(
            complaints=InMemoryComplaintRepository(),
            assignments=InMemoryAssignmentRepository(),
            domain=ComplaintDomainService(),
        )
    if escalation is None:
        escalation = ComplaintEscalationApplicationService(
            complaints=InMemoryComplaintRepository(),
            escalations=InMemoryEscalationRepository(),
            domain=ComplaintDomainService(),
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
    crud, processing, assignment, escalation = _services()
    app = _foundation_app(crud, processing, assignment, escalation)
    with TestClient(app) as test_client:
        yield test_client


def test_processing_start_resolve_close_reopen() -> None:
    crud, processing, _assignment, _esc = _services()

    async def scenario() -> None:
        created = await crud.create_complaint(
            _ctx(),
            CreateComplaintInput(
                organization_id=_id(),
                branch_id=_id(),
                queue_ticket_id=_id(),
                category="Billing",
                title="Double charge",
                description="Charged twice",
            ),
        )
        started = await processing.start_processing(_ctx(), created.complaint_id)
        assert started.status is ComplaintStatus.IN_PROGRESS

        resolved = await processing.resolve(
            _ctx(),
            created.complaint_id,
            ResolveComplaintInput(summary="Refund issued", resolved_by="agent-9"),
        )
        assert resolved.status is ComplaintStatus.RESOLVED
        assert resolved.resolution is not None
        assert resolved.resolution.summary == "Refund issued"
        assert resolved.resolution.resolved_by == "agent-9"

        closed = await processing.close(_ctx(), created.complaint_id)
        assert closed.status is ComplaintStatus.CLOSED
        assert closed.resolution is not None

        # reopen from closed is invalid
        with pytest.raises(ComplaintApplicationError) as exc:
            await processing.reopen(_ctx(), created.complaint_id)
        assert exc.value.code == "INVALID_COMPLAINT_TRANSITION"

        # reopen from resolved path: recreate resolved via second complaint
        created2 = await crud.create_complaint(
            _ctx(),
            CreateComplaintInput(
                organization_id=_id(),
                branch_id=_id(),
                queue_ticket_id=_id(),
                category="Internet",
                title="Outage",
                description="No signal",
            ),
        )
        await processing.start_processing(_ctx(), created2.complaint_id)
        await processing.resolve(
            _ctx(),
            created2.complaint_id,
            ResolveComplaintInput(summary="Tower reset", resolved_by="noc"),
        )
        reopened = await processing.reopen(
            _ctx(),
            created2.complaint_id,
            ReopenComplaintInput(reason="customer called again"),
        )
        assert reopened.status is ComplaintStatus.IN_PROGRESS
        assert reopened.resolution is None

    _run(scenario())


def test_processing_invalid_transition_open_to_resolve() -> None:
    crud, processing, _assignment, _esc = _services()

    async def scenario() -> None:
        created = await crud.create_complaint(
            _ctx(),
            CreateComplaintInput(
                organization_id=_id(),
                branch_id=_id(),
                queue_ticket_id=_id(),
                category="Sales",
                title="X",
                description="Y",
            ),
        )
        with pytest.raises(ComplaintApplicationError) as exc:
            await processing.resolve(
                _ctx(),
                created.complaint_id,
                ResolveComplaintInput(summary="nope", resolved_by="x"),
            )
        assert exc.value.code == "INVALID_COMPLAINT_TRANSITION"

    _run(scenario())


def test_immutable_resolution_after_close() -> None:
    from app.modules.complaint.domain.errors import ComplaintDomainError
    from app.modules.complaint.domain.models import Resolution

    crud, processing, _assignment, _esc = _services()

    async def scenario() -> None:
        created = await crud.create_complaint(
            _ctx(),
            CreateComplaintInput(
                organization_id=_id(),
                branch_id=_id(),
                queue_ticket_id=_id(),
                category="General",
                title="T",
                description="D",
            ),
        )
        await processing.start_processing(_ctx(), created.complaint_id)
        await processing.resolve(
            _ctx(),
            created.complaint_id,
            ResolveComplaintInput(summary="Done", resolved_by="a1"),
        )
        closed = await processing.close(_ctx(), created.complaint_id)
        assert closed.resolution is not None
        with pytest.raises(ComplaintApplicationError) as exc:
            await processing.resolve(
                _ctx(),
                created.complaint_id,
                ResolveComplaintInput(summary="Changed", resolved_by="a2"),
            )
        assert exc.value.code == "INVALID_COMPLAINT_TRANSITION"

        domain_closed = Complaint(
            complaint_id=closed.complaint_id,
            organization_id=closed.organization_id,
            branch_id=closed.branch_id,
            queue_ticket_id=closed.queue_ticket_id,
            category=closed.category,
            title=closed.title,
            description=closed.description,
            priority=closed.priority,
            status=ComplaintStatus.CLOSED,
            created_at=closed.created_at,
            updated_at=closed.updated_at,
            resolution=Resolution(
                summary=closed.resolution.summary,
                resolved_by=closed.resolution.resolved_by,
                resolved_at=closed.resolution.resolved_at,
            ),
        )
        with pytest.raises(ComplaintDomainError) as imm:
            domain_closed.assert_resolution_mutable()
        assert imm.value.code == "RESOLUTION_IMMUTABLE"

    _run(scenario())


def test_api_processing_happy_path(client: TestClient) -> None:
    created = client.post(
        "/api/v1/complaints",
        json={
            "organizationId": str(_id()),
            "branchId": str(_id()),
            "queueTicketId": str(_id()),
            "category": "Billing",
            "title": "Fee dispute",
            "description": "Unexpected fee",
            "priority": "HIGH",
        },
    ).json()["data"]
    cid = created["complaintId"]

    started = client.post(f"/api/v1/complaints/{cid}/start")
    assert started.status_code == 200
    assert started.json()["data"]["status"] == "IN_PROGRESS"

    resolved = client.post(
        f"/api/v1/complaints/{cid}/resolve",
        json={"summary": "Fee waived", "resolvedBy": "agent-42"},
    )
    assert resolved.status_code == 200
    body = resolved.json()["data"]
    assert body["status"] == "RESOLVED"
    assert body["resolution"]["summary"] == "Fee waived"
    assert body["resolution"]["resolvedBy"] == "agent-42"
    assert "resolvedAt" in body["resolution"]
    assert body["category"] == "Billing"
    assert body["priority"] == "HIGH"
    assert "updatedAt" in body

    closed = client.post(f"/api/v1/complaints/{cid}/close", json={})
    assert closed.status_code == 200
    assert closed.json()["data"]["status"] == "CLOSED"
    assert closed.json()["data"]["resolution"]["summary"] == "Fee waived"


def test_api_reopen(client: TestClient) -> None:
    created = client.post(
        "/api/v1/complaints",
        json={
            "organizationId": str(_id()),
            "branchId": str(_id()),
            "queueTicketId": str(_id()),
            "category": "Internet",
            "title": "Slow",
            "description": "Speed drop",
        },
    ).json()["data"]
    cid = created["complaintId"]
    client.post(f"/api/v1/complaints/{cid}/start")
    client.post(
        f"/api/v1/complaints/{cid}/resolve",
        json={"summary": "Modem reset", "resolvedBy": "tech"},
    )
    reopened = client.post(
        f"/api/v1/complaints/{cid}/reopen",
        json={"reason": "still slow"},
    )
    assert reopened.status_code == 200
    data = reopened.json()["data"]
    assert data["status"] == "IN_PROGRESS"
    assert data["resolution"] is None


def test_api_invalid_transition(client: TestClient) -> None:
    created = client.post(
        "/api/v1/complaints",
        json={
            "organizationId": str(_id()),
            "branchId": str(_id()),
            "queueTicketId": str(_id()),
            "category": "General",
            "title": "X",
            "description": "Y",
        },
    ).json()["data"]
    response = client.post(
        f"/api/v1/complaints/{created['complaintId']}/resolve",
        json={"summary": "too early", "resolvedBy": "x"},
    )
    assert response.status_code == 409
    assert response.json()["code"] == "INVALID_STATE"


def test_api_resolve_validation(client: TestClient) -> None:
    created = client.post(
        "/api/v1/complaints",
        json={
            "organizationId": str(_id()),
            "branchId": str(_id()),
            "queueTicketId": str(_id()),
            "category": "General",
            "title": "X",
            "description": "Y",
        },
    ).json()["data"]
    cid = created["complaintId"]
    client.post(f"/api/v1/complaints/{cid}/start")
    missing = client.post(
        f"/api/v1/complaints/{cid}/resolve",
        json={"summary": "  ", "resolvedBy": "agent"},
    )
    assert missing.status_code == 422
    missing_by = client.post(
        f"/api/v1/complaints/{cid}/resolve",
        json={"summary": "ok"},
    )
    assert missing_by.status_code == 422


def test_api_immutable_resolution_after_close(client: TestClient) -> None:
    created = client.post(
        "/api/v1/complaints",
        json={
            "organizationId": str(_id()),
            "branchId": str(_id()),
            "queueTicketId": str(_id()),
            "category": "Billing",
            "title": "X",
            "description": "Y",
        },
    ).json()["data"]
    cid = created["complaintId"]
    client.post(f"/api/v1/complaints/{cid}/start")
    client.post(
        f"/api/v1/complaints/{cid}/resolve",
        json={"summary": "Done", "resolvedBy": "a"},
    )
    client.post(f"/api/v1/complaints/{cid}/close")
    again = client.post(
        f"/api/v1/complaints/{cid}/resolve",
        json={"summary": "Changed", "resolvedBy": "b"},
    )
    assert again.status_code == 409


def test_openapi_processing_paths() -> None:
    path = (
        Path(__file__).resolve().parents[2]
        / "07 API Catalog"
        / "openapi"
        / "complaint-domain-service.v1.yaml"
    )
    spec = yaml.safe_load(path.read_text(encoding="utf-8"))
    paths = spec["paths"]
    assert paths["/api/v1/complaints/{complaintId}/start"]["post"]["x-ear-id"] == (
        "API-397"
    )
    assert paths["/api/v1/complaints/{complaintId}/resolve"]["post"]["x-ear-id"] == (
        "API-398"
    )
    assert paths["/api/v1/complaints/{complaintId}/close"]["post"]["x-ear-id"] == (
        "API-399"
    )
    assert paths["/api/v1/complaints/{complaintId}/reopen"]["post"]["x-ear-id"] == (
        "API-400"
    )
    assert "ResolveRequest" in spec["components"]["schemas"]
    assert "ResolutionResponse" in spec["components"]["schemas"]
