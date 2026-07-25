"""Queue REST API Foundation tests (TASK-064).

Unit · Controller · Integration · Validation · Exception · OpenAPI.
"""

from __future__ import annotations

import asyncio
import uuid
from collections.abc import AsyncIterator, Generator
from contextlib import asynccontextmanager
from datetime import datetime, timezone
from pathlib import Path
from typing import Any
from unittest.mock import AsyncMock

import pytest
import yaml
from fastapi import Response
from fastapi.testclient import TestClient
from sqlalchemy import create_engine, text
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from app.core.auth import Principal, get_current_principal
from app.core.config import get_settings
from app.core.errors import ConflictError, InvalidStateError, NotFoundError, ValidationAppError
from app.core.request_context import RequestContext, get_request_context
from app.core.schemas import DataResponse
from app.db.async_session import _to_async_url
from app.db.base import Base
from app.main import create_app
from app.modules.queue.api.controllers import (
    CounterController,
    QueueController,
    TicketController,
)
from app.modules.queue.api.dependencies import (
    get_queue_crud_service,
    get_queue_operations_service,
)
from app.modules.queue.api.exception_handlers import map_queue_error
from app.modules.queue.api.requests import (
    CreateCounterRequest,
    CreateQueueRequest,
    CreateTicketRequest,
    UpdateCounterRequest,
    UpdateQueueRequest,
    UpdateTicketRequest,
)
from app.modules.queue.api.responses import (
    QueueCounterResponse,
    QueueResponse,
    QueueTicketResponse,
)
from app.modules.queue.application.dto import QueueDto, QueueTicketDto
from app.modules.queue.application.services import (
    CreateCounterInput,
    CreateQueueInput,
    IssueTicketInput,
    QueueApplicationError,
    QueueCounterView,
    QueueCrudApplicationService,
    QueueDomainService,
    QueueOperationsApplicationService,
    UpdateCounterInput,
    UpdateQueueInput,
    UpdateTicketInput,
)
from app.modules.queue.interfaces.repositories import (
    QueueCounterRepository,
    QueueRepository,
    QueueTicketRepository,
)
from app.modules.queue.models import (
    Queue,
    QueueCounter,
    QueuePolicy,
    QueuePriority,
    QueueStatus,
    QueueTicket,
    QueueTicketStatus,
)
from app.modules.queue.orm import QueueCounterORM, QueueORM, QueueTicketORM


# ---------------------------------------------------------------------------
# Helpers / fakes
# ---------------------------------------------------------------------------


def _qid() -> uuid.UUID:
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


class InMemoryQueueRepository(QueueRepository):
    def __init__(self) -> None:
        self.rows: dict[uuid.UUID, Queue] = {}

    async def add(self, queue: Queue) -> Queue:
        self.rows[queue.queue_id] = queue
        return queue

    async def get_by_id(self, queue_id: uuid.UUID) -> Queue | None:
        return self.rows.get(queue_id)

    async def update(self, queue: Queue) -> Queue:
        if queue.queue_id not in self.rows:
            raise KeyError(queue.queue_id)
        self.rows[queue.queue_id] = queue
        return queue

    async def list_by_organization(
        self, organization_id: uuid.UUID
    ) -> tuple[Queue, ...]:
        items = [q for q in self.rows.values() if q.organization_id == organization_id]
        items.sort(key=lambda q: (q.name, str(q.queue_id)))
        return tuple(items)

    async def delete(self, queue_id: uuid.UUID) -> bool:
        return self.rows.pop(queue_id, None) is not None


class InMemoryTicketRepository(QueueTicketRepository):
    def __init__(self) -> None:
        self.rows: dict[uuid.UUID, QueueTicket] = {}

    async def add(self, ticket: QueueTicket) -> QueueTicket:
        self.rows[ticket.ticket_id] = ticket
        return ticket

    async def get_by_id(self, ticket_id: uuid.UUID) -> QueueTicket | None:
        return self.rows.get(ticket_id)

    async def update(self, ticket: QueueTicket) -> QueueTicket:
        if ticket.ticket_id not in self.rows:
            raise KeyError(ticket.ticket_id)
        self.rows[ticket.ticket_id] = ticket
        return ticket

    async def list_by_queue(self, queue_id: uuid.UUID) -> tuple[QueueTicket, ...]:
        items = [t for t in self.rows.values() if t.queue_id == queue_id]
        items.sort(key=lambda t: (t.created_at, str(t.ticket_id)))
        return tuple(items)

    async def list_by_queue_and_status(
        self, queue_id: uuid.UUID, status: str
    ) -> tuple[QueueTicket, ...]:
        return tuple(
            t
            for t in await self.list_by_queue(queue_id)
            if t.status.value == status
        )

    async def delete(self, ticket_id: uuid.UUID) -> bool:
        return self.rows.pop(ticket_id, None) is not None


class InMemoryCounterRepository(QueueCounterRepository):
    def __init__(self) -> None:
        self.rows: dict[uuid.UUID, tuple[uuid.UUID, QueueCounter]] = {}

    async def add(
        self, queue_id: uuid.UUID, counter: QueueCounter
    ) -> QueueCounter:
        self.rows[counter.counter_id] = (queue_id, counter)
        return counter

    async def get_by_id(self, counter_id: uuid.UUID) -> QueueCounter | None:
        item = self.rows.get(counter_id)
        return None if item is None else item[1]

    async def get_queue_id(self, counter_id: uuid.UUID) -> uuid.UUID | None:
        item = self.rows.get(counter_id)
        return None if item is None else item[0]

    async def update(
        self, queue_id: uuid.UUID, counter: QueueCounter
    ) -> QueueCounter:
        if counter.counter_id not in self.rows:
            raise KeyError(counter.counter_id)
        self.rows[counter.counter_id] = (queue_id, counter)
        return counter

    async def list_by_queue(self, queue_id: uuid.UUID) -> tuple[QueueCounter, ...]:
        items = [c for qid, c in self.rows.values() if qid == queue_id]
        items.sort(key=lambda c: (c.name, str(c.counter_id)))
        return tuple(items)

    async def delete(self, counter_id: uuid.UUID) -> bool:
        return self.rows.pop(counter_id, None) is not None


def _service() -> QueueCrudApplicationService:
    return QueueCrudApplicationService(
        queues=InMemoryQueueRepository(),
        tickets=InMemoryTicketRepository(),
        counters=InMemoryCounterRepository(),
        domain=QueueDomainService(),
    )


def _run(coro: Any) -> Any:
    return asyncio.run(coro)


def _postgres_available() -> bool:
    settings = get_settings()
    try:
        eng = create_engine(
            settings.database_url,
            pool_pre_ping=True,
            future=True,
            connect_args={"connect_timeout": 2},
        )
        with eng.connect() as conn:
            conn.execute(text("SELECT 1"))
        eng.dispose()
        return True
    except Exception:
        return False


# ---------------------------------------------------------------------------
# Unit — application CRUD service
# ---------------------------------------------------------------------------


def test_crud_create_list_get_update_delete_queue() -> None:
    svc = _service()
    org = _qid()
    ctx = _ctx()

    async def scenario() -> None:
        created = await svc.create_queue(
            ctx,
            CreateQueueInput(
                organization_id=org,
                name="Lobby",
                description="main",
                policy=QueuePolicy.FIFO,
            ),
        )
        assert created.status is QueueStatus.CLOSED
        assert created.name == "Lobby"

        listed = await svc.list_queues(ctx, org)
        assert len(listed) == 1

        got = await svc.get_queue(ctx, created.queue_id)
        assert got.queue_id == created.queue_id

        updated = await svc.update_queue(
            ctx,
            created.queue_id,
            UpdateQueueInput(name="Lobby B", status=QueueStatus.OPEN),
        )
        assert updated.name == "Lobby B"
        assert updated.status is QueueStatus.OPEN

        await svc.delete_queue(ctx, created.queue_id)
        with pytest.raises(QueueApplicationError) as exc:
            await svc.get_queue(ctx, created.queue_id)
        assert exc.value.code == "QUEUE_NOT_FOUND"

    _run(scenario())


def test_crud_issue_ticket_requires_open_queue() -> None:
    svc = _service()
    ctx = _ctx()

    async def scenario() -> None:
        closed = await svc.create_queue(
            ctx, CreateQueueInput(organization_id=_qid(), name="Closed Q")
        )
        with pytest.raises(QueueApplicationError) as exc:
            await svc.issue_ticket(
                ctx, IssueTicketInput(queue_id=closed.queue_id)
            )
        assert exc.value.code == "QUEUE_CLOSED"

        await svc.update_queue(
            ctx, closed.queue_id, UpdateQueueInput(status=QueueStatus.OPEN)
        )
        ticket = await svc.issue_ticket(
            ctx,
            IssueTicketInput(
                queue_id=closed.queue_id, priority=QueuePriority.VIP
            ),
        )
        assert ticket.ticket_number == "A001"
        assert ticket.status is QueueTicketStatus.WAITING
        assert ticket.priority is QueuePriority.VIP

    _run(scenario())


def test_crud_ticket_and_counter_lifecycle() -> None:
    svc = _service()
    ctx = _ctx()

    async def scenario() -> None:
        queue = await svc.create_queue(
            ctx,
            CreateQueueInput(
                organization_id=_qid(),
                name="Svc",
                status=QueueStatus.OPEN,
            ),
        )
        ticket = await svc.issue_ticket(
            ctx, IssueTicketInput(queue_id=queue.queue_id)
        )
        got = await svc.get_ticket(ctx, ticket.ticket_id)
        assert got.ticket_id == ticket.ticket_id

        updated = await svc.update_ticket(
            ctx,
            ticket.ticket_id,
            UpdateTicketInput(status=QueueTicketStatus.CALLED),
        )
        assert updated.status is QueueTicketStatus.CALLED

        counter = await svc.create_counter(
            ctx, CreateCounterInput(queue_id=queue.queue_id, name="C1")
        )
        assert counter.queue_id == queue.queue_id
        listed = await svc.list_counters(ctx, queue.queue_id)
        assert len(listed) == 1

        c_upd = await svc.update_counter(
            ctx,
            counter.counter_id,
            UpdateCounterInput(name="C1-renamed", status=QueueStatus.OPEN),
        )
        assert c_upd.name == "C1-renamed"

        await svc.delete_ticket(ctx, ticket.ticket_id)
        await svc.delete_counter(ctx, counter.counter_id)

    _run(scenario())


# ---------------------------------------------------------------------------
# Unit — exception mapping
# ---------------------------------------------------------------------------


def test_map_queue_error_not_found() -> None:
    err = map_queue_error(QueueApplicationError("QUEUE_NOT_FOUND", "missing"))
    assert isinstance(err, NotFoundError)
    assert err.status_code == 404


def test_map_queue_error_invalid_state() -> None:
    err = map_queue_error(QueueApplicationError("QUEUE_CLOSED", "closed"))
    assert isinstance(err, InvalidStateError)
    assert err.status_code == 409


def test_map_queue_error_conflict() -> None:
    err = map_queue_error(
        QueueApplicationError("DUPLICATE_TICKET_NUMBER", "dup")
    )
    assert isinstance(err, ConflictError)
    assert err.status_code == 409


def test_map_queue_error_validation() -> None:
    err = map_queue_error(QueueApplicationError("INVALID_PRIORITY", "bad"))
    assert isinstance(err, ValidationAppError)
    assert err.status_code == 400


# ---------------------------------------------------------------------------
# Unit / Controller — controllers with mocked service
# ---------------------------------------------------------------------------


def test_queue_controller_create_returns_response_dto() -> None:
    service = AsyncMock(spec=QueueCrudApplicationService)
    service.create_queue.return_value = QueueDto(
        queue_id=_qid(),
        organization_id=_qid(),
        name="A",
        description="",
        status=QueueStatus.CLOSED,
        policy=QueuePolicy.FIFO,
    )
    controller = QueueController(service)
    result = _run(
        controller.create(
            CreateQueueRequest(
                organizationId=_qid(),
                name="A",
            ),
            _ctx(),
        )
    )
    assert isinstance(result, DataResponse)
    assert isinstance(result.data, QueueResponse)
    assert result.data.name == "A"


def test_ticket_controller_maps_not_found() -> None:
    service = AsyncMock(spec=QueueCrudApplicationService)
    service.get_ticket.side_effect = QueueApplicationError(
        "TICKET_NOT_FOUND", "missing ticket"
    )
    controller = TicketController(service)
    with pytest.raises(NotFoundError):
        _run(controller.get(_qid(), _ctx()))


def test_counter_controller_delete_204() -> None:
    service = AsyncMock(spec=QueueCrudApplicationService)
    service.delete_counter.return_value = None
    controller = CounterController(service)
    result = _run(controller.delete(_qid(), _ctx()))
    assert isinstance(result, Response)
    assert result.status_code == 204


# ---------------------------------------------------------------------------
# OpenAPI
# ---------------------------------------------------------------------------


def test_openapi_catalog_yaml_has_all_paths() -> None:
    path = (
        Path(__file__).resolve().parents[2]
        / "07 API Catalog"
        / "openapi"
        / "queue-service.v1.yaml"
    )
    doc = yaml.safe_load(path.read_text(encoding="utf-8"))
    paths = doc["paths"]
    assert "/api/v1/queues" in paths
    assert "/api/v1/queues/{queueId}" in paths
    assert "/api/v1/queues/{queueId}/tickets" in paths
    assert "/api/v1/tickets/{ticketId}" in paths
    assert "/api/v1/queues/{queueId}/counters" in paths
    assert "/api/v1/counters/{counterId}" in paths
    assert "/api/v1/queues/{queueId}/open" in paths
    assert "/api/v1/queues/{queueId}/close" in paths
    assert "/api/v1/queues/{queueId}/issue-ticket" in paths
    assert "/api/v1/queues/{queueId}/call-next" in paths
    assert "/api/v1/tickets/{ticketId}/recall" in paths
    assert "/api/v1/tickets/{ticketId}/complete" in paths
    assert "/api/v1/tickets/{ticketId}/skip" in paths
    assert "/api/v1/tickets/{ticketId}/cancel" in paths
    assert doc["info"]["x-ear-id"] == "API-360"


def test_fastapi_openapi_includes_queue_endpoints() -> None:
    app = create_app()
    schema = app.openapi()
    paths = schema["paths"]
    assert "/api/v1/queues" in paths
    assert "post" in paths["/api/v1/queues"]
    assert "get" in paths["/api/v1/queues"]
    assert "/api/v1/queues/{queue_id}" in paths
    assert "/api/v1/queues/{queue_id}/tickets" in paths
    assert "/api/v1/tickets/{ticket_id}" in paths
    assert "/api/v1/queues/{queue_id}/counters" in paths
    assert "/api/v1/counters/{counter_id}" in paths
    assert "/api/v1/queues/{queue_id}/open" in paths
    assert "/api/v1/queues/{queue_id}/close" in paths
    assert "/api/v1/queues/{queue_id}/issue-ticket" in paths
    assert "/api/v1/queues/{queue_id}/call-next" in paths
    assert "/api/v1/tickets/{ticket_id}/recall" in paths
    assert "/api/v1/tickets/{ticket_id}/complete" in paths
    assert "/api/v1/tickets/{ticket_id}/skip" in paths
    assert "/api/v1/tickets/{ticket_id}/cancel" in paths
    tags = {t["name"] for t in schema.get("tags", [])} | {
        op.get("tags", [None])[0]
        for methods in paths.values()
        for op in methods.values()
        if isinstance(op, dict)
    }
    assert "Queues" in tags
    assert "Queue Tickets" in tags
    assert "Queue Counters" in tags


def test_request_context_ready_dependency() -> None:
    org = _qid()
    branch = _qid()
    user = _qid()
    ctx = get_request_context(
        x_request_id="req-064",
        x_correlation_id="corr-064",
        x_organization_id=org,
        x_branch_id=branch,
        x_user_id=user,
        x_locale="id-ID",
        x_timezone="Asia/Jakarta",
    )
    assert ctx.request_id == "req-064"
    assert ctx.correlation_id == "corr-064"
    assert ctx.organization_id == org
    assert ctx.branch_id == branch
    assert ctx.user_id == user
    assert ctx.locale == "id-ID"
    assert ctx.timezone == "Asia/Jakarta"
    assert ctx.roles == frozenset()
    assert ctx.permissions == frozenset()


# ---------------------------------------------------------------------------
# HTTP — validation + controller wiring (in-memory service override)
# ---------------------------------------------------------------------------


@pytest.fixture()
def api_client() -> Generator[TestClient, None, None]:
    app = create_app()
    queues = InMemoryQueueRepository()
    tickets = InMemoryTicketRepository()
    counters = InMemoryCounterRepository()
    domain = QueueDomainService()
    crud = QueueCrudApplicationService(
        queues=queues, tickets=tickets, counters=counters, domain=domain
    )
    ops = QueueOperationsApplicationService(
        queues=queues, tickets=tickets, domain=domain
    )

    app.dependency_overrides[get_queue_crud_service] = lambda: crud
    app.dependency_overrides[get_queue_operations_service] = lambda: ops
    app.dependency_overrides[get_current_principal] = _principal
    with TestClient(app) as client:
        client.svc = crud  # type: ignore[attr-defined]
        yield client
    app.dependency_overrides.clear()


def test_http_create_and_get_queue(api_client: TestClient) -> None:
    org = str(_qid())
    resp = api_client.post(
        "/api/v1/queues",
        json={
            "organizationId": org,
            "name": "HTTP Lobby",
            "description": "d",
            "policy": "FIFO",
        },
    )
    assert resp.status_code == 201, resp.text
    body = resp.json()["data"]
    assert body["name"] == "HTTP Lobby"
    assert body["status"] == "CLOSED"
    queue_id = body["queueId"]

    got = api_client.get(f"/api/v1/queues/{queue_id}")
    assert got.status_code == 200
    assert got.json()["data"]["queueId"] == queue_id

    listed = api_client.get(f"/api/v1/queues?organizationId={org}")
    assert listed.status_code == 200
    assert len(listed.json()["data"]) == 1


def test_http_validation_blank_name(api_client: TestClient) -> None:
    resp = api_client.post(
        "/api/v1/queues",
        json={"organizationId": str(_qid()), "name": "   "},
    )
    assert resp.status_code == 400
    assert resp.json()["code"] == "VALIDATION_ERROR"


def test_http_validation_invalid_uuid_path(api_client: TestClient) -> None:
    resp = api_client.get("/api/v1/queues/not-a-uuid")
    assert resp.status_code == 400
    assert resp.json()["code"] == "VALIDATION_ERROR"


def test_http_validation_invalid_enum(api_client: TestClient) -> None:
    resp = api_client.post(
        "/api/v1/queues",
        json={
            "organizationId": str(_qid()),
            "name": "X",
            "policy": "ROUND_ROBIN",
        },
    )
    assert resp.status_code == 400
    assert resp.json()["code"] == "VALIDATION_ERROR"


def test_http_queue_not_found(api_client: TestClient) -> None:
    resp = api_client.get(f"/api/v1/queues/{_qid()}")
    assert resp.status_code == 404
    assert resp.json()["code"] == "NOT_FOUND"


def test_http_ticket_issue_and_invalid_state(api_client: TestClient) -> None:
    org = str(_qid())
    created = api_client.post(
        "/api/v1/queues",
        json={"organizationId": org, "name": "TicketQ"},
    ).json()["data"]
    queue_id = created["queueId"]

    closed_issue = api_client.post(
        f"/api/v1/queues/{queue_id}/tickets",
        json={"priority": "NORMAL"},
    )
    assert closed_issue.status_code == 409
    assert closed_issue.json()["code"] == "INVALID_STATE"

    api_client.put(
        f"/api/v1/queues/{queue_id}",
        json={"status": "OPEN"},
    )
    issued = api_client.post(
        f"/api/v1/queues/{queue_id}/tickets",
        json={"priority": "PRIORITY"},
    )
    assert issued.status_code == 201, issued.text
    ticket = issued.json()["data"]
    assert ticket["ticketNumber"] == "A001"
    assert ticket["status"] == "WAITING"

    listed = api_client.get(f"/api/v1/queues/{queue_id}/tickets")
    assert listed.status_code == 200
    assert len(listed.json()["data"]) == 1

    got = api_client.get(f"/api/v1/tickets/{ticket['ticketId']}")
    assert got.status_code == 200

    bad_transition = api_client.put(
        f"/api/v1/tickets/{ticket['ticketId']}",
        json={"status": "COMPLETED"},
    )
    assert bad_transition.status_code == 409

    called = api_client.put(
        f"/api/v1/tickets/{ticket['ticketId']}",
        json={"status": "CALLED"},
    )
    assert called.status_code == 200
    assert called.json()["data"]["status"] == "CALLED"

    deleted = api_client.delete(f"/api/v1/tickets/{ticket['ticketId']}")
    assert deleted.status_code == 204


def test_http_counter_crud(api_client: TestClient) -> None:
    queue = api_client.post(
        "/api/v1/queues",
        json={"organizationId": str(_qid()), "name": "CounterQ", "status": "OPEN"},
    ).json()["data"]
    queue_id = queue["queueId"]

    created = api_client.post(
        f"/api/v1/queues/{queue_id}/counters",
        json={"name": "Window 1", "status": "CLOSED"},
    )
    assert created.status_code == 201, created.text
    counter = created.json()["data"]
    assert counter["queueId"] == queue_id
    assert counter["name"] == "Window 1"

    listed = api_client.get(f"/api/v1/queues/{queue_id}/counters")
    assert listed.status_code == 200
    assert len(listed.json()["data"]) == 1

    updated = api_client.put(
        f"/api/v1/counters/{counter['counterId']}",
        json={"name": "Window 1A", "status": "OPEN"},
    )
    assert updated.status_code == 200
    assert updated.json()["data"]["name"] == "Window 1A"

    deleted = api_client.delete(f"/api/v1/counters/{counter['counterId']}")
    assert deleted.status_code == 204


def test_http_delete_queue(api_client: TestClient) -> None:
    queue = api_client.post(
        "/api/v1/queues",
        json={"organizationId": str(_qid()), "name": "ToDelete"},
    ).json()["data"]
    resp = api_client.delete(f"/api/v1/queues/{queue['queueId']}")
    assert resp.status_code == 204
    assert api_client.get(f"/api/v1/queues/{queue['queueId']}").status_code == 404


def test_http_list_queues_requires_organization_id(api_client: TestClient) -> None:
    resp = api_client.get("/api/v1/queues")
    assert resp.status_code == 400
    assert resp.json()["code"] == "VALIDATION_ERROR"


def test_response_models_never_expose_domain_keys() -> None:
    q = QueueResponse(
        queueId=_qid(),
        organizationId=_qid(),
        name="n",
        description="",
        status=QueueStatus.OPEN,
        policy=QueuePolicy.FIFO,
    )
    payload = q.model_dump(by_alias=True)
    assert "queue_id" not in payload
    assert "queueId" in payload

    t = QueueTicketResponse(
        ticketId=_qid(),
        queueId=_qid(),
        ticketNumber="A001",
        priority=QueuePriority.NORMAL,
        status=QueueTicketStatus.WAITING,
        createdAt=datetime.now(timezone.utc),
    )
    assert "ticketId" in t.model_dump(by_alias=True)

    c = QueueCounterResponse(
        counterId=_qid(),
        queueId=_qid(),
        name="C",
        status=QueueStatus.CLOSED,
    )
    assert "counterId" in c.model_dump(by_alias=True)


# ---------------------------------------------------------------------------
# Integration — SQLAlchemy persistence + HTTP (Postgres)
# ---------------------------------------------------------------------------


@asynccontextmanager
async def _pg_session() -> AsyncIterator[AsyncSession]:
    settings = get_settings()
    engine = create_async_engine(
        _to_async_url(settings.database_url),
        pool_pre_ping=True,
        future=True,
    )
    import app.modules.queue.orm  # noqa: F401

    async with engine.begin() as conn:
        await conn.run_sync(
            lambda sync_conn: Base.metadata.create_all(
                sync_conn,
                tables=[
                    QueueORM.__table__,
                    QueueTicketORM.__table__,
                    QueueCounterORM.__table__,
                ],
                checkfirst=True,
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
                text("DELETE FROM queue_tickets WHERE ticket_number LIKE 'T064-%'")
            )
            await conn.execute(
                text("DELETE FROM queue_counters WHERE name LIKE 'T064-%'")
            )
            await conn.execute(text("DELETE FROM queues WHERE name LIKE 'T064-%'"))
        await engine.dispose()


@pytest.mark.skipif(
    not _postgres_available(),
    reason="PostgreSQL not available for Queue API integration tests",
)
def test_integration_crud_service_against_postgres() -> None:
    from app.modules.queue.infrastructure import (
        get_queue_counter_repository,
        get_queue_repository,
        get_queue_ticket_repository,
    )

    async def scenario() -> None:
        async with _pg_session() as session:
            svc = QueueCrudApplicationService(
                queues=get_queue_repository(session),
                tickets=get_queue_ticket_repository(session),
                counters=get_queue_counter_repository(session),
            )
            org = _qid()
            ctx = _ctx()
            queue = await svc.create_queue(
                ctx,
                CreateQueueInput(
                    organization_id=org,
                    name="T064-Lobby",
                    status=QueueStatus.OPEN,
                ),
            )
            ticket = await svc.issue_ticket(
                ctx, IssueTicketInput(queue_id=queue.queue_id)
            )
            assert ticket.ticket_number.startswith("A")
            counter = await svc.create_counter(
                ctx,
                CreateCounterInput(
                    queue_id=queue.queue_id,
                    name="T064-Window",
                ),
            )
            assert counter.queue_id == queue.queue_id
            await svc.delete_counter(ctx, counter.counter_id)
            await svc.delete_ticket(ctx, ticket.ticket_id)
            await svc.delete_queue(ctx, queue.queue_id)

    _run(scenario())


def test_architecture_controllers_do_not_import_orm() -> None:
    root = (
        Path(__file__).resolve().parents[1]
        / "app"
        / "modules"
        / "queue"
        / "api"
        / "controllers"
    )
    for path in root.glob("*.py"):
        source = path.read_text(encoding="utf-8")
        assert "queue.orm" not in source
        assert "SqlAlchemy" not in source
        assert "repositories" not in source


def test_architecture_controllers_do_not_parse_headers() -> None:
    root = (
        Path(__file__).resolve().parents[1]
        / "app"
        / "modules"
        / "queue"
        / "api"
        / "controllers"
    )
    for path in (
        root / "queue_controller.py",
        root / "ticket_controller.py",
        root / "counter_controller.py",
    ):
        source = path.read_text(encoding="utf-8")
        assert "Header(" not in source
        assert "X-Organization-Id" not in source
        assert "X-Branch-Id" not in source
        assert "X-User-Id" not in source
        assert "from app.core.request_context import RequestContext" in source
