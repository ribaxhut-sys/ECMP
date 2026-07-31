"""Complaint Assignment application + API tests (CAPABILITY-006)."""

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
    AssignComplaintInput,
    ComplaintApplicationError,
    ComplaintAssignmentApplicationService,
    ComplaintCrudApplicationService,
    ComplaintDomainService,
    ComplaintEscalationApplicationService,
    ComplaintProcessingApplicationService,
    CreateComplaintInput,
    ReassignComplaintInput,
    UnassignComplaintInput,
)
from app.modules.complaint.domain.models import (
    AssigneeType,
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
    complaints: InMemoryComplaintRepository | None = None,
    assignments: InMemoryAssignmentRepository | None = None,
) -> tuple[
    ComplaintCrudApplicationService,
    ComplaintProcessingApplicationService,
    ComplaintAssignmentApplicationService,
    ComplaintEscalationApplicationService,
    InMemoryComplaintRepository,
    InMemoryAssignmentRepository,
]:
    store = complaints if complaints is not None else InMemoryComplaintRepository()
    assign_store = (
        assignments if assignments is not None else InMemoryAssignmentRepository()
    )
    domain = ComplaintDomainService()
    return (
        ComplaintCrudApplicationService(complaints=store, domain=domain),
        ComplaintProcessingApplicationService(complaints=store, domain=domain),
        ComplaintAssignmentApplicationService(
            complaints=store, assignments=assign_store, domain=domain
        ),
        ComplaintEscalationApplicationService(
            complaints=store,
            escalations=InMemoryEscalationRepository(),
            domain=domain,
        ),
        store,
        assign_store,
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
    crud, processing, assignment, escalation, _, _ = _services()
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
            title="Assign me",
            description="Need an owner",
        ),
    )
    return created.complaint_id


def test_first_assignment() -> None:
    crud, _processing, assignment, _esc, store, _ = _services()

    async def scenario() -> None:
        complaint_id = await _create_complaint(crud)
        status_before = store.rows[complaint_id].status
        created = await assignment.assign(
            _ctx(),
            complaint_id,
            AssignComplaintInput(
                assignee_type=AssigneeType.USER,
                assignee_id="user-1",
                assigned_by="supervisor-1",
            ),
        )
        assert created.is_active is True
        assert created.assignee_id == "user-1"
        assert created.released_at is None
        assert store.rows[complaint_id].status is status_before

    _run(scenario())


def test_reassignment_appends_history() -> None:
    crud, _processing, assignment, _esc, store, assign_store = _services()

    async def scenario() -> None:
        complaint_id = await _create_complaint(crud)
        first = await assignment.assign(
            _ctx(),
            complaint_id,
            AssignComplaintInput(
                assignee_type=AssigneeType.USER,
                assignee_id="user-1",
                assigned_by="supervisor-1",
            ),
        )
        status_before = store.rows[complaint_id].status
        second = await assignment.reassign(
            _ctx(),
            complaint_id,
            ReassignComplaintInput(
                assignee_type=AssigneeType.USER,
                assignee_id="user-2",
                assigned_by="supervisor-2",
            ),
        )
        assert second.is_active is True
        assert second.assignee_id == "user-2"
        assert second.assignment_id != first.assignment_id

        history = await assignment.list_history(_ctx(), complaint_id)
        assert len(history) == 2
        assert history[0].assignment_id == first.assignment_id
        assert history[0].is_active is False
        assert history[0].assignee_id == "user-1"
        assert history[0].released_at is not None
        assert history[1].is_active is True
        assert store.rows[complaint_id].status is status_before
        assert len(assign_store.rows) == 2

    _run(scenario())


def test_unassign() -> None:
    crud, _processing, assignment, _esc, store, _ = _services()

    async def scenario() -> None:
        complaint_id = await _create_complaint(crud)
        await assignment.assign(
            _ctx(),
            complaint_id,
            AssignComplaintInput(
                assignee_type=AssigneeType.USER,
                assignee_id="user-1",
                assigned_by="supervisor-1",
            ),
        )
        status_before = store.rows[complaint_id].status
        released = await assignment.unassign(
            _ctx(),
            complaint_id,
            UnassignComplaintInput(released_by="supervisor-1", reason="coverage end"),
        )
        assert released.is_active is False
        assert released.released_at is not None
        with pytest.raises(ComplaintApplicationError) as exc:
            await assignment.get_current(_ctx(), complaint_id)
        assert exc.value.code == "ASSIGNMENT_NOT_FOUND"
        assert store.rows[complaint_id].status is status_before

    _run(scenario())


def test_active_assignment_and_history() -> None:
    crud, _processing, assignment, _esc, _, _ = _services()

    async def scenario() -> None:
        complaint_id = await _create_complaint(crud)
        created = await assignment.assign(
            _ctx(),
            complaint_id,
            AssignComplaintInput(
                assignee_type=AssigneeType.USER,
                assignee_id="user-1",
                assigned_by="supervisor-1",
            ),
        )
        current = await assignment.get_current(_ctx(), complaint_id)
        assert current.assignment_id == created.assignment_id
        assert current.is_active is True
        history = await assignment.list_history(_ctx(), complaint_id)
        assert len(history) == 1

    _run(scenario())


def test_double_active_assignment_rejected() -> None:
    crud, _processing, assignment, _esc, _, _ = _services()

    async def scenario() -> None:
        complaint_id = await _create_complaint(crud)
        await assignment.assign(
            _ctx(),
            complaint_id,
            AssignComplaintInput(
                assignee_type=AssigneeType.USER,
                assignee_id="user-1",
                assigned_by="supervisor-1",
            ),
        )
        with pytest.raises(ComplaintApplicationError) as exc:
            await assignment.assign(
                _ctx(),
                complaint_id,
                AssignComplaintInput(
                    assignee_type=AssigneeType.USER,
                    assignee_id="user-2",
                    assigned_by="supervisor-1",
                ),
            )
        assert exc.value.code == "ACTIVE_ASSIGNMENT_EXISTS"

    _run(scenario())


def test_validation_unsupported_assignee_type() -> None:
    crud, _processing, assignment, _esc, _, _ = _services()

    async def scenario() -> None:
        complaint_id = await _create_complaint(crud)
        with pytest.raises(ComplaintApplicationError) as exc:
            await assignment.assign(
                _ctx(),
                complaint_id,
                AssignComplaintInput(
                    assignee_type=AssigneeType.TEAM,
                    assignee_id="team-1",
                    assigned_by="supervisor-1",
                ),
            )
        assert exc.value.code == "UNSUPPORTED_ASSIGNEE_TYPE"

    _run(scenario())


def test_reassign_without_active_rejected() -> None:
    crud, _processing, assignment, _esc, _, _ = _services()

    async def scenario() -> None:
        complaint_id = await _create_complaint(crud)
        with pytest.raises(ComplaintApplicationError) as exc:
            await assignment.reassign(
                _ctx(),
                complaint_id,
                ReassignComplaintInput(
                    assignee_type=AssigneeType.USER,
                    assignee_id="user-2",
                    assigned_by="supervisor-1",
                ),
            )
        assert exc.value.code == "NO_ACTIVE_ASSIGNMENT"

    _run(scenario())


def test_domain_assign_does_not_change_status() -> None:
    from datetime import datetime, timezone

    from app.modules.complaint.domain.models import ComplaintPriority

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
    created = complaint.assign(
        assignee_type=AssigneeType.USER,
        assignee_id="user-1",
        assigned_by="supervisor-1",
        active=None,
    )
    assert created.is_active is True
    assert complaint.status is ComplaintStatus.OPEN


def test_assignment_api_integration(client: TestClient) -> None:
    create = client.post(
        "/api/v1/complaints",
        json={
            "organizationId": str(_id()),
            "branchId": str(_id()),
            "queueTicketId": str(_id()),
            "category": "Billing",
            "title": "API assign",
            "description": "via HTTP",
        },
    )
    assert create.status_code == 201
    complaint_id = create.json()["data"]["complaintId"]
    status_open = create.json()["data"]["status"]

    assign = client.post(
        f"/api/v1/complaints/{complaint_id}/assign",
        json={
            "assigneeType": "USER",
            "assigneeId": "user-1",
            "assignedBy": "supervisor-1",
        },
    )
    assert assign.status_code == 201
    body = assign.json()["data"]
    assert body["isActive"] is True
    assert body["assigneeId"] == "user-1"
    assert "assignmentId" in body

    current = client.get(f"/api/v1/complaints/{complaint_id}/assignment")
    assert current.status_code == 200
    assert current.json()["data"]["assignmentId"] == body["assignmentId"]

    reassign = client.post(
        f"/api/v1/complaints/{complaint_id}/reassign",
        json={
            "assigneeType": "USER",
            "assigneeId": "user-2",
            "assignedBy": "supervisor-2",
        },
    )
    assert reassign.status_code == 200
    assert reassign.json()["data"]["assigneeId"] == "user-2"

    history = client.get(f"/api/v1/complaints/{complaint_id}/assignments")
    assert history.status_code == 200
    rows = history.json()["data"]
    assert len(rows) == 2
    assert rows[0]["isActive"] is False
    assert rows[1]["isActive"] is True

    unassign = client.post(
        f"/api/v1/complaints/{complaint_id}/unassign",
        json={"releasedBy": "supervisor-2", "reason": "done"},
    )
    assert unassign.status_code == 200
    assert unassign.json()["data"]["isActive"] is False

    missing = client.get(f"/api/v1/complaints/{complaint_id}/assignment")
    assert missing.status_code == 404

    conflict = client.post(
        f"/api/v1/complaints/{complaint_id}/assign",
        json={
            "assigneeType": "USER",
            "assigneeId": "user-3",
            "assignedBy": "supervisor-1",
        },
    )
    # after unassign, assign again is allowed
    assert conflict.status_code == 201

    again = client.post(
        f"/api/v1/complaints/{complaint_id}/assign",
        json={
            "assigneeType": "USER",
            "assigneeId": "user-4",
            "assignedBy": "supervisor-1",
        },
    )
    assert again.status_code == 409

    got = client.get(f"/api/v1/complaints/{complaint_id}")
    assert got.status_code == 200
    assert got.json()["data"]["status"] == status_open


def test_assignment_validation_http(client: TestClient) -> None:
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
        f"/api/v1/complaints/{complaint_id}/assign",
        json={
            "assigneeType": "USER",
            "assigneeId": "   ",
            "assignedBy": "supervisor-1",
        },
    )
    assert response.status_code == 422


def test_openapi_assignment_paths() -> None:
    path = (
        Path(__file__).resolve().parents[2]
        / "07 API Catalog"
        / "openapi"
        / "complaint-domain-service.v1.yaml"
    )
    spec = yaml.safe_load(path.read_text(encoding="utf-8"))
    paths = spec["paths"]
    assert paths["/api/v1/complaints/{complaintId}/assign"]["post"]["x-ear-id"] == (
        "API-401"
    )
    assert paths["/api/v1/complaints/{complaintId}/reassign"]["post"]["x-ear-id"] == (
        "API-402"
    )
    assert paths["/api/v1/complaints/{complaintId}/unassign"]["post"]["x-ear-id"] == (
        "API-403"
    )
    assert paths["/api/v1/complaints/{complaintId}/assignment"]["get"]["x-ear-id"] == (
        "API-404"
    )
    assert paths["/api/v1/complaints/{complaintId}/assignments"]["get"]["x-ear-id"] == (
        "API-405"
    )
    assert "AssigneeType" in spec["components"]["schemas"]
    assert "AssignmentResponse" in spec["components"]["schemas"]
