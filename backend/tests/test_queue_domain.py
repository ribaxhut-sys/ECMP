"""Queue Domain Foundation tests (TASK-061 / TASK-062)."""

from __future__ import annotations

import ast
import uuid
from datetime import datetime, timezone
from pathlib import Path

import pytest

from app.modules.provider_contract import ProviderResponse, ProviderStatus
from app.modules.queue import (
    Queue,
    QueueCounter,
    QueuePolicy,
    QueuePriority,
    QueueStatus,
    QueueTicket,
    QueueTicketStatus,
)


def _qid() -> uuid.UUID:
    return uuid.uuid4()


def test_queue_pass() -> None:
    q = Queue(
        queue_id=_qid(),
        organization_id=_qid(),
        name="Branch Lobby",
        description="Main lobby queue",
        status=QueueStatus.OPEN,
        policy=QueuePolicy.FIFO,
    )
    assert q.name == "Branch Lobby"
    assert q.status is QueueStatus.OPEN
    assert q.policy is QueuePolicy.FIFO
    data = q.as_dict()
    assert data["name"] == "Branch Lobby"
    assert data["status"] == "OPEN"
    assert data["policy"] == "FIFO"


def test_queue_rejects_blank_name() -> None:
    with pytest.raises(ValueError, match="name"):
        Queue(
            queue_id=_qid(),
            organization_id=_qid(),
            name="  ",
            description="",
            status=QueueStatus.OPEN,
            policy=QueuePolicy.FIFO,
        )


def test_ticket_pass() -> None:
    qid = _qid()
    created = datetime(2026, 7, 24, 10, 0, 0, tzinfo=timezone.utc)
    ticket = QueueTicket(
        ticket_id=_qid(),
        queue_id=qid,
        ticket_number="A001",
        priority=QueuePriority.VIP,
        status=QueueTicketStatus.WAITING,
        created_at=created,
    )
    assert ticket.ticket_number == "A001"
    assert ticket.priority is QueuePriority.VIP
    assert ticket.status is QueueTicketStatus.WAITING
    assert ticket.created_at.tzinfo is not None
    data = ticket.as_dict()
    assert data["ticketNumber"] == "A001"
    assert data["priority"] == "VIP"
    assert data["status"] == "WAITING"


def test_ticket_rejects_queue_status() -> None:
    with pytest.raises(TypeError, match="QueueTicketStatus"):
        QueueTicket(
            ticket_id=_qid(),
            queue_id=_qid(),
            ticket_number="X001",
            priority=QueuePriority.NORMAL,
            status=QueueStatus.OPEN,  # type: ignore[arg-type]
            created_at=datetime.now(timezone.utc),
        )


def test_ticket_naive_datetime_normalized_to_utc() -> None:
    ticket = QueueTicket(
        ticket_id=_qid(),
        queue_id=_qid(),
        ticket_number="B002",
        priority=QueuePriority.NORMAL,
        status=QueueTicketStatus.WAITING,
        created_at=datetime(2026, 7, 24, 12, 0, 0),
    )
    assert ticket.created_at.tzinfo == timezone.utc


def test_counter_pass() -> None:
    counter = QueueCounter(
        counter_id=_qid(),
        name="Counter 1",
        status=QueueStatus.OPEN,
    )
    assert counter.name == "Counter 1"
    assert counter.status is QueueStatus.OPEN
    assert counter.as_dict()["status"] == "OPEN"


def test_policy_pass() -> None:
    values = {p.value for p in QueuePolicy}
    assert values == {"FIFO", "PRIORITY_QUEUE"}
    q = Queue(
        queue_id=_qid(),
        organization_id=_qid(),
        name="Priority Desk",
        description="",
        status=QueueStatus.OPEN,
        policy=QueuePolicy.PRIORITY_QUEUE,
    )
    assert q.policy is QueuePolicy.PRIORITY_QUEUE


def test_priority_pass() -> None:
    values = {p.value for p in QueuePriority}
    assert values == {"NORMAL", "PRIORITY", "VIP"}


def test_status_pass() -> None:
    values = {s.value for s in QueueStatus}
    assert values == {"OPEN", "PAUSED", "CLOSED"}


def test_ticket_status_pass() -> None:
    values = {s.value for s in QueueTicketStatus}
    assert values == {
        "WAITING",
        "CALLED",
        "SERVING",
        "COMPLETED",
        "CANCELLED",
        "SKIPPED",
    }


def test_immutability_pass() -> None:
    q = Queue(
        queue_id=_qid(),
        organization_id=_qid(),
        name="Q",
        description="",
        status=QueueStatus.OPEN,
        policy=QueuePolicy.FIFO,
    )
    ticket = QueueTicket(
        ticket_id=_qid(),
        queue_id=q.queue_id,
        ticket_number="C003",
        priority=QueuePriority.PRIORITY,
        status=QueueTicketStatus.WAITING,
        created_at=datetime.now(timezone.utc),
    )
    counter = QueueCounter(counter_id=_qid(), name="C1", status=QueueStatus.CLOSED)
    with pytest.raises(Exception):
        q.status = QueueStatus.CLOSED  # type: ignore[misc]
    with pytest.raises(Exception):
        ticket.priority = QueuePriority.VIP  # type: ignore[misc]
    with pytest.raises(Exception):
        counter.name = "X"  # type: ignore[misc]


def _collect_imports(source: str) -> list[str]:
    tree = ast.parse(source)
    imports: list[str] = []
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            imports.extend(a.name for a in node.names)
        elif isinstance(node, ast.ImportFrom) and node.module:
            imports.append(node.module)
    return imports


def test_queue_modules_no_forbidden_imports() -> None:
    """Domain stays infra-free; api/ may use FastAPI; persistence may use SQLAlchemy.

    TASK-064 adds ``api/`` (HTTP) and ``application/services/crud_service.py``
    (repository ports). Cross-domain imports remain forbidden everywhere.
    """
    root = Path(__file__).resolve().parents[1] / "app" / "modules" / "queue"
    cross_domain = (
        "fastapi",
        "httpx",
        "requests",
        "smtplib",
        "aiohttp",
        "redis",
        "app.modules.complaints",
        "app.modules.complaint",
        "app.modules.workflow",
        "app.modules.execution",
        "app.modules.delivery",
        "app.modules.transport",
        "app.modules.provider_executor",
        "app.modules.provider_contract",
        "app.modules.notification",
        "app.modules.dashboard",
        "app.modules.kpi",
    )
    domain_forbidden = cross_domain + ("sqlalchemy",)
    persistence_dirs = {
        "orm",
        "mappers",
        "repositories",
        "infrastructure",
        "interfaces",
    }
    api_allowed_fastapi = {"api"}
    # Persistence-backed application services may import repository ports.
    repository_allowed = {
        Path("application") / "services" / "crud_service.py",
        Path("application") / "services" / "operations_service.py",
    }

    py_files = list(root.rglob("*.py"))
    assert py_files
    for path in py_files:
        rel = path.relative_to(root)
        parts = rel.parts
        is_persistence = bool(parts) and parts[0] in persistence_dirs
        is_api = bool(parts) and parts[0] in api_allowed_fastapi
        source = path.read_text(encoding="utf-8")
        imports = _collect_imports(source)
        if is_api:
            # API may import FastAPI + AsyncSession for DI; still forbid cross-domains.
            forbidden = cross_domain
            forbidden = tuple(f for f in forbidden if f != "fastapi")
        elif is_persistence:
            forbidden = cross_domain
        else:
            forbidden = domain_forbidden
        for mod in imports:
            assert not any(mod == f or mod.startswith(f + ".") for f in forbidden), (
                f"{rel} imports forbidden module {mod}"
            )
        if not is_api and not is_persistence:
            assert "APIRouter" not in source
        if not is_persistence and not is_api:
            lowered = source.lower()
            if "sqlalchemy" in lowered:
                assert (
                    "no sqlalchemy" in lowered or "not sqlalchemy" in lowered
                ), f"{rel} mentions SQLAlchemy without negation"
            assert "AsyncSession" not in source
            # Domain/application may document that state is "not a repository".
            if "repository" in lowered and rel not in repository_allowed:
                assert (
                    "no repository" in lowered
                    or "not a repository" in lowered
                    or "not repository" in lowered
                ), f"{rel} references repository without negation"
        elif is_persistence:
            # Interfaces must not import SQLAlchemy; ORM/mappers/repos may.
            if parts[0] == "interfaces":
                assert not any(
                    mod == "sqlalchemy" or mod.startswith("sqlalchemy.")
                    for mod in imports
                ), f"{rel} (interface) must not import SQLAlchemy"


def test_regression_provider_contract_untouched() -> None:
    """Provider contract remains independent of Queue domain."""
    response = ProviderResponse(
        provider_name="email-stub",
        status=ProviderStatus.READY,
        correlation_id="corr-1",
    )
    assert response.status is ProviderStatus.READY
    assert response.provider_name == "email-stub"
