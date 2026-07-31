"""Queue Operations tests (CAPABILITY-003).

Issue · Queue Closed · Call Next · Complete · Skip · Cancel · Invalid Transition.
"""

from __future__ import annotations

from collections.abc import Generator
from datetime import datetime, timezone

import pytest
from fastapi.testclient import TestClient
from tests.test_queue_api import (
    InMemoryCounterRepository,
    InMemoryQueueRepository,
    InMemoryTicketRepository,
    _ctx,
    _principal,
    _qid,
    _run,
)

from app.core.auth import get_current_principal
from app.main import create_app
from app.modules.queue.api.dependencies import (
    get_queue_crud_service,
    get_queue_operations_service,
)
from app.modules.queue.application.services import (
    CreateQueueInput,
    IssueTicketOperationInput,
    QueueApplicationError,
    QueueCrudApplicationService,
    QueueDomainService,
    QueueOperationsApplicationService,
)
from app.modules.queue.domain import PrefixSequenceTicketNumberGenerator
from app.modules.queue.models import (
    QueuePriority,
    QueueStatus,
    QueueTicket,
    QueueTicketStatus,
)


def _paired_services() -> tuple[
    QueueCrudApplicationService, QueueOperationsApplicationService
]:
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
    return crud, ops


# ---------------------------------------------------------------------------
# Domain / generator
# ---------------------------------------------------------------------------


def test_ticket_number_generator_default_a001() -> None:
    gen = PrefixSequenceTicketNumberGenerator()
    assert gen.generate(1) == "A001"
    assert gen.generate(2) == "A002"
    assert gen.generate(3) == "A003"


def test_ticket_number_generator_is_pluggable() -> None:
    domain = QueueDomainService(
        ticket_number_generator=PrefixSequenceTicketNumberGenerator(
            prefix="B", width=3
        )
    )
    assert domain.generate_ticket_number(1) == "B001"


def test_invalid_transition_waiting_to_completed() -> None:
    domain = QueueDomainService()
    ticket = QueueTicket(
        ticket_id=_qid(),
        queue_id=_qid(),
        ticket_number="A001",
        priority=QueuePriority.NORMAL,
        status=QueueTicketStatus.WAITING,
        created_at=datetime.now(timezone.utc),
    )
    with pytest.raises(QueueApplicationError) as exc:
        domain.transition_ticket(ticket, QueueTicketStatus.COMPLETED)
    assert exc.value.code == "INVALID_TICKET_TRANSITION"


# ---------------------------------------------------------------------------
# Application operations
# ---------------------------------------------------------------------------


def test_ops_issue_ticket() -> None:
    crud, ops = _paired_services()
    ctx = _ctx()

    async def scenario() -> None:
        queue = await crud.create_queue(
            ctx,
            CreateQueueInput(
                organization_id=_qid(),
                name="Ops Lobby",
                status=QueueStatus.OPEN,
            ),
        )
        t1 = await ops.issue_ticket(
            ctx, IssueTicketOperationInput(queue_id=queue.queue_id)
        )
        t2 = await ops.issue_ticket(
            ctx, IssueTicketOperationInput(queue_id=queue.queue_id)
        )
        assert t1.ticket_number == "A001"
        assert t2.ticket_number == "A002"
        assert t1.status is QueueTicketStatus.WAITING

    _run(scenario())


def test_ops_queue_closed_rejects_issue() -> None:
    crud, ops = _paired_services()
    ctx = _ctx()

    async def scenario() -> None:
        queue = await crud.create_queue(
            ctx,
            CreateQueueInput(organization_id=_qid(), name="Closed"),
        )
        assert queue.status is QueueStatus.CLOSED
        with pytest.raises(QueueApplicationError) as exc:
            await ops.issue_ticket(
                ctx, IssueTicketOperationInput(queue_id=queue.queue_id)
            )
        assert exc.value.code == "QUEUE_CLOSED"

    _run(scenario())


def test_ops_call_next_complete_skip_cancel() -> None:
    crud, ops = _paired_services()
    ctx = _ctx()

    async def scenario() -> None:
        queue = await crud.create_queue(
            ctx,
            CreateQueueInput(
                organization_id=_qid(),
                name="Flow",
                status=QueueStatus.OPEN,
            ),
        )
        t1 = await ops.issue_ticket(
            ctx, IssueTicketOperationInput(queue_id=queue.queue_id)
        )
        t2 = await ops.issue_ticket(
            ctx, IssueTicketOperationInput(queue_id=queue.queue_id)
        )
        t3 = await ops.issue_ticket(
            ctx, IssueTicketOperationInput(queue_id=queue.queue_id)
        )

        called = await ops.call_next(ctx, queue.queue_id)
        assert called is not None
        assert called.ticket_id == t1.ticket_id
        assert called.status is QueueTicketStatus.CALLED

        recalled = await ops.recall_ticket(ctx, called.ticket_id)
        assert recalled.status is QueueTicketStatus.CALLED

        completed = await ops.complete_ticket(ctx, called.ticket_id)
        assert completed.status is QueueTicketStatus.COMPLETED

        skipped = await ops.skip_ticket(ctx, t2.ticket_id)
        assert skipped.status is QueueTicketStatus.SKIPPED

        cancelled = await ops.cancel_ticket(ctx, t3.ticket_id)
        assert cancelled.status is QueueTicketStatus.CANCELLED

        empty = await ops.call_next(ctx, queue.queue_id)
        assert empty is None

    _run(scenario())


def test_ops_open_close() -> None:
    crud, ops = _paired_services()
    ctx = _ctx()

    async def scenario() -> None:
        queue = await crud.create_queue(
            ctx, CreateQueueInput(organization_id=_qid(), name="Gate")
        )
        opened = await ops.open_queue(ctx, queue.queue_id)
        assert opened.status is QueueStatus.OPEN
        closed = await ops.close_queue(ctx, queue.queue_id)
        assert closed.status is QueueStatus.CLOSED
        with pytest.raises(QueueApplicationError) as exc:
            await ops.issue_ticket(
                ctx, IssueTicketOperationInput(queue_id=queue.queue_id)
            )
        assert exc.value.code == "QUEUE_CLOSED"

    _run(scenario())


# ---------------------------------------------------------------------------
# HTTP operations
# ---------------------------------------------------------------------------


@pytest.fixture()
def ops_client() -> Generator[TestClient, None, None]:
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
        yield client
    app.dependency_overrides.clear()


def test_http_operations_lifecycle(ops_client: TestClient) -> None:
    org = str(_qid())
    created = ops_client.post(
        "/api/v1/queues",
        json={"organizationId": org, "name": "OpsHTTP"},
    )
    assert created.status_code == 201, created.text
    queue_id = created.json()["data"]["queueId"]

    closed_issue = ops_client.post(
        f"/api/v1/queues/{queue_id}/issue-ticket",
        json={"priority": "NORMAL"},
    )
    assert closed_issue.status_code == 409

    opened = ops_client.post(f"/api/v1/queues/{queue_id}/open")
    assert opened.status_code == 200
    assert opened.json()["data"]["status"] == "OPEN"

    issued = ops_client.post(
        f"/api/v1/queues/{queue_id}/issue-ticket",
        json={"priority": "NORMAL"},
    )
    assert issued.status_code == 201, issued.text
    ticket = issued.json()["data"]
    assert ticket["ticketNumber"] == "A001"
    assert ticket["status"] == "WAITING"

    second = ops_client.post(
        f"/api/v1/queues/{queue_id}/issue-ticket",
        json={},
    ).json()["data"]

    called = ops_client.post(f"/api/v1/queues/{queue_id}/call-next")
    assert called.status_code == 200
    assert called.json()["data"]["ticketId"] == ticket["ticketId"]
    assert called.json()["data"]["status"] == "CALLED"

    recalled = ops_client.post(f"/api/v1/tickets/{ticket['ticketId']}/recall")
    assert recalled.status_code == 200
    assert recalled.json()["data"]["status"] == "CALLED"

    completed = ops_client.post(f"/api/v1/tickets/{ticket['ticketId']}/complete")
    assert completed.status_code == 200
    assert completed.json()["data"]["status"] == "COMPLETED"

    skipped = ops_client.post(f"/api/v1/tickets/{second['ticketId']}/skip")
    assert skipped.status_code == 200
    assert skipped.json()["data"]["status"] == "SKIPPED"

    third = ops_client.post(
        f"/api/v1/queues/{queue_id}/issue-ticket",
        json={},
    ).json()["data"]
    cancelled = ops_client.post(f"/api/v1/tickets/{third['ticketId']}/cancel")
    assert cancelled.status_code == 200
    assert cancelled.json()["data"]["status"] == "CANCELLED"

    empty = ops_client.post(f"/api/v1/queues/{queue_id}/call-next")
    assert empty.status_code == 204

    closed = ops_client.post(f"/api/v1/queues/{queue_id}/close")
    assert closed.status_code == 200
    assert closed.json()["data"]["status"] == "CLOSED"


def test_http_invalid_transition_via_complete(ops_client: TestClient) -> None:
    org = str(_qid())
    queue_id = ops_client.post(
        "/api/v1/queues",
        json={"organizationId": org, "name": "BadX", "status": "OPEN"},
    ).json()["data"]["queueId"]
    ticket_id = ops_client.post(
        f"/api/v1/queues/{queue_id}/issue-ticket",
        json={},
    ).json()["data"]["ticketId"]

    bad = ops_client.post(f"/api/v1/tickets/{ticket_id}/complete")
    assert bad.status_code == 409
    assert bad.json()["code"] == "INVALID_STATE"
