"""Queue Application Foundation tests (TASK-062).

Domain service · commands · queries · policy · ticket lifecycle · regression.
"""

from __future__ import annotations

import uuid
from datetime import datetime, timedelta, timezone

import pytest

from app.modules.provider_contract import ProviderResponse, ProviderStatus
from app.modules.queue.application import (
    CallNextTicketCommand,
    CallNextTicketHandler,
    CancelTicketCommand,
    CancelTicketHandler,
    CloseQueueCommand,
    CloseQueueHandler,
    CompleteTicketCommand,
    CompleteTicketHandler,
    CreateQueueCommand,
    CreateQueueHandler,
    GetQueueHandler,
    GetQueueQuery,
    GetQueueTicketsHandler,
    GetQueueTicketsQuery,
    GetWaitingTicketsHandler,
    GetWaitingTicketsQuery,
    InMemoryQueueState,
    IssueTicketCommand,
    IssueTicketHandler,
    OpenQueueCommand,
    OpenQueueHandler,
    PauseQueueCommand,
    PauseQueueHandler,
    QueueApplicationError,
    QueueDomainService,
    QueueDto,
    QueueTicketDto,
    RecallTicketCommand,
    RecallTicketHandler,
    SkipTicketCommand,
    SkipTicketHandler,
)
from app.modules.queue.models import (
    Queue,
    QueuePolicy,
    QueuePriority,
    QueueStatus,
    QueueTicket,
    QueueTicketStatus,
)


@pytest.fixture()
def state() -> InMemoryQueueState:
    return InMemoryQueueState()


@pytest.fixture()
def domain() -> QueueDomainService:
    return QueueDomainService()


@pytest.fixture()
def handlers(state: InMemoryQueueState, domain: QueueDomainService) -> dict:
    return {
        "create": CreateQueueHandler(state=state, domain=domain),
        "open": OpenQueueHandler(state=state, domain=domain),
        "pause": PauseQueueHandler(state=state, domain=domain),
        "close": CloseQueueHandler(state=state, domain=domain),
        "issue": IssueTicketHandler(state=state, domain=domain),
        "call": CallNextTicketHandler(state=state, domain=domain),
        "complete": CompleteTicketHandler(state=state, domain=domain),
        "cancel": CancelTicketHandler(state=state, domain=domain),
        "skip": SkipTicketHandler(state=state, domain=domain),
        "recall": RecallTicketHandler(state=state, domain=domain),
        "get_queue": GetQueueHandler(state=state),
        "get_tickets": GetQueueTicketsHandler(state=state),
        "get_waiting": GetWaitingTicketsHandler(state=state, domain=domain),
    }


def _open_queue(
    handlers: dict,
    *,
    policy: QueuePolicy = QueuePolicy.FIFO,
) -> QueueDto:
    created = handlers["create"].handle(
        CreateQueueCommand(
            organization_id=uuid.uuid4(),
            name="Lobby",
            description="test",
            policy=policy,
        )
    )
    return handlers["open"].handle(OpenQueueCommand(queue_id=created.queue_id))


# ---------------------------------------------------------------------------
# Domain service
# ---------------------------------------------------------------------------


def test_domain_generate_ticket_number(domain: QueueDomainService) -> None:
    assert domain.generate_ticket_number(1) == "A001"
    assert domain.generate_ticket_number(42) == "A042"
    with pytest.raises(QueueApplicationError) as exc:
        domain.generate_ticket_number(0)
    assert exc.value.code == "INVALID_TICKET_SEQUENCE"


def test_domain_select_next_fifo(domain: QueueDomainService) -> None:
    qid = uuid.uuid4()
    base = datetime(2026, 7, 24, 10, 0, 0, tzinfo=timezone.utc)
    t1 = QueueTicket(
        ticket_id=uuid.uuid4(),
        queue_id=qid,
        ticket_number="A001",
        priority=QueuePriority.VIP,
        status=QueueTicketStatus.WAITING,
        created_at=base + timedelta(seconds=10),
    )
    t2 = QueueTicket(
        ticket_id=uuid.uuid4(),
        queue_id=qid,
        ticket_number="A002",
        priority=QueuePriority.NORMAL,
        status=QueueTicketStatus.WAITING,
        created_at=base,
    )
    queue = Queue(
        queue_id=qid,
        organization_id=uuid.uuid4(),
        name="F",
        description="",
        status=QueueStatus.OPEN,
        policy=QueuePolicy.FIFO,
    )
    selected = domain.select_next_ticket(queue, (t1, t2))
    assert selected is not None
    assert selected.ticket_number == "A002"


def test_domain_select_next_priority(domain: QueueDomainService) -> None:
    qid = uuid.uuid4()
    base = datetime(2026, 7, 24, 10, 0, 0, tzinfo=timezone.utc)
    normal = QueueTicket(
        ticket_id=uuid.uuid4(),
        queue_id=qid,
        ticket_number="A001",
        priority=QueuePriority.NORMAL,
        status=QueueTicketStatus.WAITING,
        created_at=base,
    )
    vip = QueueTicket(
        ticket_id=uuid.uuid4(),
        queue_id=qid,
        ticket_number="A002",
        priority=QueuePriority.VIP,
        status=QueueTicketStatus.WAITING,
        created_at=base + timedelta(seconds=30),
    )
    queue = Queue(
        queue_id=qid,
        organization_id=uuid.uuid4(),
        name="P",
        description="",
        status=QueueStatus.OPEN,
        policy=QueuePolicy.PRIORITY_QUEUE,
    )
    selected = domain.select_next_ticket(queue, (normal, vip))
    assert selected is not None
    assert selected.ticket_number == "A002"
    assert selected.priority is QueuePriority.VIP


def test_domain_cancelled_cannot_be_called(domain: QueueDomainService) -> None:
    ticket = QueueTicket(
        ticket_id=uuid.uuid4(),
        queue_id=uuid.uuid4(),
        ticket_number="A001",
        priority=QueuePriority.NORMAL,
        status=QueueTicketStatus.CANCELLED,
        created_at=datetime.now(timezone.utc),
    )
    with pytest.raises(QueueApplicationError) as exc:
        domain.assert_ticket_callable(ticket)
    assert exc.value.code == "TICKET_CANCELLED"


def test_domain_completed_cannot_return_to_waiting(
    domain: QueueDomainService,
) -> None:
    ticket = QueueTicket(
        ticket_id=uuid.uuid4(),
        queue_id=uuid.uuid4(),
        ticket_number="A001",
        priority=QueuePriority.NORMAL,
        status=QueueTicketStatus.COMPLETED,
        created_at=datetime.now(timezone.utc),
    )
    with pytest.raises(QueueApplicationError) as exc:
        domain.transition_ticket(ticket, QueueTicketStatus.WAITING)
    assert exc.value.code in {"TICKET_COMPLETED", "INVALID_TICKET_TRANSITION"}


# ---------------------------------------------------------------------------
# Commands
# ---------------------------------------------------------------------------


def test_create_open_pause_close(handlers: dict) -> None:
    created = handlers["create"].handle(
        CreateQueueCommand(
            organization_id=uuid.uuid4(),
            name="Desk",
            policy=QueuePolicy.FIFO,
        )
    )
    assert created.status is QueueStatus.CLOSED
    opened = handlers["open"].handle(OpenQueueCommand(queue_id=created.queue_id))
    assert opened.status is QueueStatus.OPEN
    paused = handlers["pause"].handle(PauseQueueCommand(queue_id=created.queue_id))
    assert paused.status is QueueStatus.PAUSED
    closed = handlers["close"].handle(CloseQueueCommand(queue_id=created.queue_id))
    assert closed.status is QueueStatus.CLOSED


def test_issue_requires_open(handlers: dict) -> None:
    created = handlers["create"].handle(
        CreateQueueCommand(
            organization_id=uuid.uuid4(),
            name="Closed Desk",
        )
    )
    with pytest.raises(QueueApplicationError) as exc:
        handlers["issue"].handle(IssueTicketCommand(queue_id=created.queue_id))
    assert exc.value.code == "QUEUE_CLOSED"


def test_issue_and_call_fifo(handlers: dict) -> None:
    queue = _open_queue(handlers, policy=QueuePolicy.FIFO)
    t1 = handlers["issue"].handle(IssueTicketCommand(queue_id=queue.queue_id))
    t2 = handlers["issue"].handle(IssueTicketCommand(queue_id=queue.queue_id))
    assert t1.ticket_number == "A001"
    assert t2.ticket_number == "A002"
    assert t1.status is QueueTicketStatus.WAITING
    called = handlers["call"].handle(CallNextTicketCommand(queue_id=queue.queue_id))
    assert called is not None
    assert called.ticket_id == t1.ticket_id
    assert called.status is QueueTicketStatus.CALLED


def test_paused_rejects_calling(handlers: dict) -> None:
    queue = _open_queue(handlers)
    handlers["issue"].handle(IssueTicketCommand(queue_id=queue.queue_id))
    handlers["pause"].handle(PauseQueueCommand(queue_id=queue.queue_id))
    with pytest.raises(QueueApplicationError) as exc:
        handlers["call"].handle(CallNextTicketCommand(queue_id=queue.queue_id))
    assert exc.value.code == "QUEUE_PAUSED"


def test_closed_rejects_new_ticket(handlers: dict) -> None:
    queue = _open_queue(handlers)
    handlers["close"].handle(CloseQueueCommand(queue_id=queue.queue_id))
    with pytest.raises(QueueApplicationError) as exc:
        handlers["issue"].handle(IssueTicketCommand(queue_id=queue.queue_id))
    assert exc.value.code == "QUEUE_CLOSED"


def test_complete_and_cancel(handlers: dict) -> None:
    queue = _open_queue(handlers)
    issued = handlers["issue"].handle(IssueTicketCommand(queue_id=queue.queue_id))
    called = handlers["call"].handle(CallNextTicketCommand(queue_id=queue.queue_id))
    assert called is not None
    completed = handlers["complete"].handle(
        CompleteTicketCommand(ticket_id=called.ticket_id)
    )
    assert completed.status is QueueTicketStatus.COMPLETED

    other = handlers["issue"].handle(IssueTicketCommand(queue_id=queue.queue_id))
    cancelled = handlers["cancel"].handle(
        CancelTicketCommand(ticket_id=other.ticket_id)
    )
    assert cancelled.status is QueueTicketStatus.CANCELLED
    # cancelled cannot be called via select (not WAITING) — issue another and call
    waiting = handlers["issue"].handle(IssueTicketCommand(queue_id=queue.queue_id))
    next_called = handlers["call"].handle(
        CallNextTicketCommand(queue_id=queue.queue_id)
    )
    assert next_called is not None
    assert next_called.ticket_id == waiting.ticket_id
    assert issued.ticket_id != waiting.ticket_id


def test_skip_and_recall(handlers: dict) -> None:
    queue = _open_queue(handlers)
    waiting = handlers["issue"].handle(IssueTicketCommand(queue_id=queue.queue_id))
    skipped = handlers["skip"].handle(SkipTicketCommand(ticket_id=waiting.ticket_id))
    assert skipped.status is QueueTicketStatus.SKIPPED

    other = handlers["issue"].handle(IssueTicketCommand(queue_id=queue.queue_id))
    called = handlers["call"].handle(CallNextTicketCommand(queue_id=queue.queue_id))
    assert called is not None
    assert called.ticket_id == other.ticket_id
    recalled = handlers["recall"].handle(RecallTicketCommand(ticket_id=called.ticket_id))
    assert recalled.status is QueueTicketStatus.CALLED
    assert recalled.ticket_id == called.ticket_id

    with pytest.raises(QueueApplicationError) as exc:
        handlers["recall"].handle(RecallTicketCommand(ticket_id=skipped.ticket_id))
    assert exc.value.code == "INVALID_TICKET_TRANSITION"


def test_invalid_transition_waiting_to_completed(
    domain: QueueDomainService,
) -> None:
    ticket = QueueTicket(
        ticket_id=uuid.uuid4(),
        queue_id=uuid.uuid4(),
        ticket_number="A001",
        priority=QueuePriority.NORMAL,
        status=QueueTicketStatus.WAITING,
        created_at=datetime.now(timezone.utc),
    )
    with pytest.raises(QueueApplicationError) as exc:
        domain.transition_ticket(ticket, QueueTicketStatus.COMPLETED)
    assert exc.value.code == "INVALID_TICKET_TRANSITION"


# ---------------------------------------------------------------------------
# Queries
# ---------------------------------------------------------------------------


def test_queries(handlers: dict) -> None:
    queue = _open_queue(handlers)
    handlers["issue"].handle(
        IssueTicketCommand(queue_id=queue.queue_id, priority=QueuePriority.NORMAL)
    )
    handlers["issue"].handle(
        IssueTicketCommand(queue_id=queue.queue_id, priority=QueuePriority.VIP)
    )
    got = handlers["get_queue"].handle(GetQueueQuery(queue_id=queue.queue_id))
    assert got.queue_id == queue.queue_id
    all_tickets = handlers["get_tickets"].handle(
        GetQueueTicketsQuery(queue_id=queue.queue_id)
    )
    assert len(all_tickets) == 2
    waiting = handlers["get_waiting"].handle(
        GetWaitingTicketsQuery(queue_id=queue.queue_id)
    )
    assert len(waiting) == 2
    handlers["call"].handle(CallNextTicketCommand(queue_id=queue.queue_id))
    waiting_after = handlers["get_waiting"].handle(
        GetWaitingTicketsQuery(queue_id=queue.queue_id)
    )
    assert len(waiting_after) == 1


# ---------------------------------------------------------------------------
# Policy
# ---------------------------------------------------------------------------


def test_priority_queue_policy_call_order(handlers: dict) -> None:
    queue = _open_queue(handlers, policy=QueuePolicy.PRIORITY_QUEUE)
    base = datetime(2026, 7, 24, 9, 0, 0, tzinfo=timezone.utc)
    normal = handlers["issue"].handle(
        IssueTicketCommand(
            queue_id=queue.queue_id,
            priority=QueuePriority.NORMAL,
            created_at=base,
        )
    )
    vip = handlers["issue"].handle(
        IssueTicketCommand(
            queue_id=queue.queue_id,
            priority=QueuePriority.VIP,
            created_at=base + timedelta(minutes=5),
        )
    )
    called = handlers["call"].handle(CallNextTicketCommand(queue_id=queue.queue_id))
    assert called is not None
    assert called.ticket_id == vip.ticket_id
    assert called.priority is QueuePriority.VIP
    second = handlers["call"].handle(CallNextTicketCommand(queue_id=queue.queue_id))
    assert second is not None
    assert second.ticket_id == normal.ticket_id


# ---------------------------------------------------------------------------
# Ticket lifecycle
# ---------------------------------------------------------------------------


def test_ticket_lifecycle_happy_path(handlers: dict) -> None:
    queue = _open_queue(handlers)
    ticket = handlers["issue"].handle(IssueTicketCommand(queue_id=queue.queue_id))
    assert ticket.status is QueueTicketStatus.WAITING
    called = handlers["call"].handle(CallNextTicketCommand(queue_id=queue.queue_id))
    assert called is not None
    assert called.status is QueueTicketStatus.CALLED
    done = handlers["complete"].handle(
        CompleteTicketCommand(ticket_id=called.ticket_id)
    )
    assert done.status is QueueTicketStatus.COMPLETED
    with pytest.raises(QueueApplicationError):
        handlers["complete"].handle(CompleteTicketCommand(ticket_id=done.ticket_id))


def test_dto_immutability(handlers: dict) -> None:
    queue = _open_queue(handlers)
    ticket = handlers["issue"].handle(IssueTicketCommand(queue_id=queue.queue_id))
    assert isinstance(queue, QueueDto)
    assert isinstance(ticket, QueueTicketDto)
    with pytest.raises(Exception):
        queue.name = "hacked"  # type: ignore[misc]
    with pytest.raises(Exception):
        ticket.status = QueueTicketStatus.COMPLETED  # type: ignore[misc]


def test_no_duplicate_ticket_numbers(
    state: InMemoryQueueState,
    domain: QueueDomainService,
    handlers: dict,
) -> None:
    queue = _open_queue(handlers)
    handlers["issue"].handle(IssueTicketCommand(queue_id=queue.queue_id))
    # Force sequence collision check via domain
    with pytest.raises(QueueApplicationError) as exc:
        domain.validate_no_duplicate_ticket_number(
            "A001", state.ticket_numbers(queue.queue_id)
        )
    assert exc.value.code == "DUPLICATE_TICKET_NUMBER"


# ---------------------------------------------------------------------------
# Regression
# ---------------------------------------------------------------------------


def test_regression_provider_contract_independent() -> None:
    response = ProviderResponse(
        provider_name="email-stub",
        status=ProviderStatus.READY,
        correlation_id="corr-queue-app",
    )
    assert response.status is ProviderStatus.READY


def test_call_next_empty_returns_none(handlers: dict) -> None:
    queue = _open_queue(handlers)
    result = handlers["call"].handle(CallNextTicketCommand(queue_id=queue.queue_id))
    assert result is None
