"""Complaint REST API Foundation tests (CAPABILITY-004).

Unit · Controller · Integration · Validation · Exception · OpenAPI.
Uses an isolated FastAPI app mounting only the Complaint Domain router so
legacy ECMF ``/api/v1/complaints`` routes do not shadow foundation CRUD.
"""

from __future__ import annotations

import asyncio
import uuid
from collections.abc import AsyncIterator, Generator
from contextlib import asynccontextmanager
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
from sqlalchemy import create_engine, text
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from app.core.auth import Principal, get_current_principal
from app.core.config import get_settings
from app.core.errors import ApiError, InvalidStateError, NotFoundError, ValidationAppError
from app.core.request_context import RequestContext, get_request_context
from app.core.schemas import ErrorResponse
from app.db.async_session import _to_async_url
from app.db.base import Base
from app.modules.complaint.api import complaint_foundation_router
from app.modules.complaint.api.controllers import ComplaintController
from app.modules.complaint.api.dependencies import (
    get_complaint_assignment_service,
    get_complaint_crud_service,
    get_complaint_escalation_service,
    get_complaint_processing_service,
    get_complaint_sla_service,
)
from app.modules.complaint.api.exception_handlers import map_complaint_error
from app.modules.complaint.api.requests import CreateComplaintRequest
from app.modules.complaint.api.responses import ComplaintResponse
from app.modules.complaint.application.dto import ComplaintDto
from app.modules.complaint.application.services import (
    ComplaintApplicationError,
    ComplaintAssignmentApplicationService,
    ComplaintCrudApplicationService,
    ComplaintDomainService,
    ComplaintEscalationApplicationService,
    ComplaintProcessingApplicationService,
    CreateComplaintInput,
    UpdateComplaintInput,
)
from app.modules.complaint.domain.models import (
    Assignment,
    Complaint,
    ComplaintPriority,
    ComplaintStatus,
    Escalation,
)
from app.modules.complaint.domain.repositories import (
    AssignmentRepository,
    ComplaintRepository,
    EscalationRepository,
)
from app.modules.complaint.infrastructure.orm import ComplaintORM


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
            {"complaints:create", "complaints:read", "complaints:update"}
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
    domain = ComplaintDomainService()
    return (
        ComplaintCrudApplicationService(complaints=store, domain=domain),
        ComplaintProcessingApplicationService(complaints=store, domain=domain),
        ComplaintAssignmentApplicationService(
            complaints=store,
            assignments=InMemoryAssignmentRepository(),
            domain=domain,
        ),
        ComplaintEscalationApplicationService(
            complaints=store,
            escalations=InMemoryEscalationRepository(),
            domain=domain,
        ),
    )


def _crud(
    repo: InMemoryComplaintRepository | None = None,
) -> ComplaintCrudApplicationService:
    return _services(repo)[0]


def _error_body(
    code: str,
    message: str,
    details: dict[str, Any] | None = None,
) -> dict[str, Any]:
    return ErrorResponse(code=code, message=message, details=details).model_dump()


def _foundation_app(
    crud: ComplaintCrudApplicationService,
    processing: ComplaintProcessingApplicationService | None = None,
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

    if processing is None:
        processing = ComplaintProcessingApplicationService(
            complaints=InMemoryComplaintRepository(),
            domain=ComplaintDomainService(),
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


def test_create_complaint_http(client: TestClient) -> None:
    org, branch, ticket = str(_id()), str(_id()), str(_id())
    response = client.post(
        "/api/v1/complaints",
        json={
            "organizationId": org,
            "branchId": branch,
            "queueTicketId": ticket,
            "category": "Billing",
            "title": "Overcharge",
            "description": "Billed twice",
            "priority": "HIGH",
        },
    )
    assert response.status_code == 201
    body = response.json()["data"]
    assert body["title"] == "Overcharge"
    assert body["status"] == "OPEN"
    assert body["priority"] == "HIGH"
    assert body["queueTicketId"] == ticket
    assert "complaintId" in body
    assert "createdAt" in body


def test_get_update_delete_complaint_http(client: TestClient) -> None:
    created = client.post(
        "/api/v1/complaints",
        json={
            "organizationId": str(_id()),
            "branchId": str(_id()),
            "queueTicketId": str(_id()),
            "category": "Internet",
            "title": "Outage",
            "description": "No service since morning",
        },
    ).json()["data"]
    cid = created["complaintId"]

    got = client.get(f"/api/v1/complaints/{cid}")
    assert got.status_code == 200
    assert got.json()["data"]["title"] == "Outage"

    updated = client.put(
        f"/api/v1/complaints/{cid}",
        json={"title": "Service outage", "status": "IN_PROGRESS"},
    )
    assert updated.status_code == 200
    assert updated.json()["data"]["title"] == "Service outage"
    assert updated.json()["data"]["status"] == "IN_PROGRESS"

    deleted = client.delete(f"/api/v1/complaints/{cid}")
    assert deleted.status_code == 204
    assert client.get(f"/api/v1/complaints/{cid}").status_code == 404


def test_get_complaints_by_ticket_http(client: TestClient) -> None:
    ticket = str(_id())
    org, branch = str(_id()), str(_id())
    client.post(
        f"/api/v1/tickets/{ticket}/complaints",
        json={
            "organizationId": org,
            "branchId": branch,
            "category": "Sales",
            "title": "A",
            "description": "first",
        },
    )
    client.post(
        "/api/v1/complaints",
        json={
            "organizationId": org,
            "branchId": branch,
            "queueTicketId": ticket,
            "category": "Billing",
            "title": "B",
            "description": "second",
        },
    )
    listed = client.get(f"/api/v1/tickets/{ticket}/complaints")
    assert listed.status_code == 200
    titles = {row["title"] for row in listed.json()["data"]}
    assert titles == {"A", "B"}


def test_invalid_lifecycle_http(client: TestClient) -> None:
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
    response = client.put(
        f"/api/v1/complaints/{created['complaintId']}",
        json={"status": "CLOSED"},
    )
    assert response.status_code == 409
    assert response.json()["code"] == "INVALID_STATE"


def test_invalid_priority_http(client: TestClient) -> None:
    response = client.post(
        "/api/v1/complaints",
        json={
            "organizationId": str(_id()),
            "branchId": str(_id()),
            "queueTicketId": str(_id()),
            "category": "Billing",
            "title": "X",
            "description": "Y",
            "priority": "CRITICAL",
        },
    )
    assert response.status_code == 422


def test_validation_missing_title_http(client: TestClient) -> None:
    response = client.post(
        "/api/v1/complaints",
        json={
            "organizationId": str(_id()),
            "branchId": str(_id()),
            "queueTicketId": str(_id()),
            "category": "Billing",
            "title": "  ",
            "description": "Y",
        },
    )
    assert response.status_code == 422


def test_create_requires_queue_ticket_id(client: TestClient) -> None:
    response = client.post(
        "/api/v1/complaints",
        json={
            "organizationId": str(_id()),
            "branchId": str(_id()),
            "category": "Billing",
            "title": "X",
            "description": "Y",
        },
    )
    assert response.status_code == 400
    assert "queue_ticket_id" in response.json()["message"]


def test_controller_create_and_get() -> None:
    crud, processing, assignment, escalation = _services()
    controller = ComplaintController(crud, processing, assignment, escalation)
    payload = CreateComplaintRequest(
        organizationId=_id(),
        branchId=_id(),
        queueTicketId=_id(),
        category="General",
        title="T",
        description="D",
    )

    async def scenario() -> None:
        created = await controller.create(payload, _ctx())
        assert created.data.title == "T"
        fetched = await controller.get(created.data.complaint_id, _ctx())
        assert fetched.data.complaint_id == created.data.complaint_id

    _run(scenario())


def test_map_complaint_error() -> None:
    assert isinstance(
        map_complaint_error(ComplaintApplicationError("COMPLAINT_NOT_FOUND", "x")),
        NotFoundError,
    )
    assert isinstance(
        map_complaint_error(
            ComplaintApplicationError("INVALID_COMPLAINT_TRANSITION", "x")
        ),
        InvalidStateError,
    )
    assert isinstance(
        map_complaint_error(ComplaintApplicationError("INVALID_PRIORITY", "x")),
        ValidationAppError,
    )


def test_response_dto_camel_case() -> None:
    now = datetime.now(timezone.utc)
    dto = ComplaintDto(
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
    response = ComplaintResponse.from_dto(dto)
    payload = response.model_dump(by_alias=True)
    assert "complaintId" in payload
    assert "queueTicketId" in payload
    assert "complaint_id" not in payload


def test_openapi_catalog_paths() -> None:
    path = (
        Path(__file__).resolve().parents[2]
        / "07 API Catalog"
        / "openapi"
        / "complaint-domain-service.v1.yaml"
    )
    spec = yaml.safe_load(path.read_text(encoding="utf-8"))
    paths = spec["paths"]
    assert "/api/v1/complaints" in paths
    assert "/api/v1/complaints/{complaintId}" in paths
    assert "/api/v1/tickets/{ticketId}/complaints" in paths
    assert paths["/api/v1/complaints"]["post"]["x-ear-id"] == "API-390"
    assert paths["/api/v1/tickets/{ticketId}/complaints"]["get"]["x-ear-id"] == "API-395"
    assert paths["/api/v1/complaints/{complaintId}/start"]["post"]["x-ear-id"] == (
        "API-397"
    )
    assert paths["/api/v1/complaints/{complaintId}/assign"]["post"]["x-ear-id"] == (
        "API-401"
    )
    assert paths["/api/v1/complaints/{complaintId}/assignments"]["get"]["x-ear-id"] == (
        "API-405"
    )


def test_controller_forbids_orm_imports() -> None:
    root = (
        Path(__file__).resolve().parents[1]
        / "app"
        / "modules"
        / "complaint"
        / "api"
        / "controllers"
    )
    for path in root.rglob("*.py"):
        source = path.read_text(encoding="utf-8")
        assert "infrastructure.orm" not in source
        assert "SqlAlchemy" not in source
        assert "ComplaintORM" not in source


def _postgres_available() -> bool:
    try:
        settings = get_settings()
        engine = create_engine(
            settings.database_url,
            pool_pre_ping=True,
            future=True,
            connect_args={"connect_timeout": 2},
        )
        with engine.connect() as conn:
            conn.execute(text("SELECT 1"))
        engine.dispose()
        return True
    except Exception:
        return False


@asynccontextmanager
async def _pg_session() -> AsyncIterator[AsyncSession]:
    settings = get_settings()
    engine = create_async_engine(
        _to_async_url(settings.database_url),
        pool_pre_ping=True,
        future=True,
    )
    import app.modules.complaint.infrastructure.orm  # noqa: F401

    async with engine.begin() as conn:
        await conn.run_sync(
            lambda sync_conn: Base.metadata.create_all(
                sync_conn,
                tables=[ComplaintORM.__table__],
                checkfirst=True,
            )
        )
        # CAPABILITY-005 — ensure resolution columns exist on pre-005 tables
        await conn.execute(
            text(
                "ALTER TABLE complaint_cases "
                "ADD COLUMN IF NOT EXISTS resolution_summary TEXT"
            )
        )
        await conn.execute(
            text(
                "ALTER TABLE complaint_cases "
                "ADD COLUMN IF NOT EXISTS resolution_resolved_by VARCHAR(200)"
            )
        )
        await conn.execute(
            text(
                "ALTER TABLE complaint_cases "
                "ADD COLUMN IF NOT EXISTS resolution_resolved_at TIMESTAMPTZ"
            )
        )
    factory = async_sessionmaker(
        bind=engine,
        autoflush=False,
        expire_on_commit=False,
        class_=AsyncSession,
    )
    session = factory()
    try:
        yield session
        await session.commit()
    except Exception:
        await session.rollback()
        raise
    finally:
        await session.close()
        async with engine.begin() as conn:
            await conn.execute(
                text("DELETE FROM complaint_cases WHERE title LIKE 'C004-%'")
            )
        await engine.dispose()


@pytest.mark.skipif(
    not _postgres_available(),
    reason="PostgreSQL not available for Complaint API integration tests",
)
def test_integration_crud_against_postgres() -> None:
    from app.modules.complaint.infrastructure import get_complaint_repository

    async def scenario() -> None:
        async with _pg_session() as session:
            svc = ComplaintCrudApplicationService(
                complaints=get_complaint_repository(session),
                domain=ComplaintDomainService(),
            )
            created = await svc.create_complaint(
                _ctx(),
                CreateComplaintInput(
                    organization_id=_id(),
                    branch_id=_id(),
                    queue_ticket_id=_id(),
                    category="Billing",
                    title="C004-integration",
                    description="persistence check",
                    priority=ComplaintPriority.LOW,
                ),
            )
            fetched = await svc.get_complaint(_ctx(), created.complaint_id)
            assert fetched.title == "C004-integration"
            progressed = await svc.update_complaint(
                _ctx(),
                created.complaint_id,
                UpdateComplaintInput(status=ComplaintStatus.IN_PROGRESS),
            )
            assert progressed.status is ComplaintStatus.IN_PROGRESS
            await svc.delete_complaint(_ctx(), created.complaint_id)

    _run(scenario())
