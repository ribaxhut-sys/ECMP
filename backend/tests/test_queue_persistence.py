"""Queue Persistence Foundation tests (TASK-063).

Mapper · ORM · Repository · Migration · Docker · Regression.
"""

from __future__ import annotations

import ast
import asyncio
import importlib
import uuid
from collections.abc import AsyncIterator
from contextlib import asynccontextmanager
from datetime import datetime, timezone
from pathlib import Path

import pytest
import yaml
from sqlalchemy import create_engine, inspect, text
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from app.core.config import get_settings
from app.db.async_session import _to_async_url
from app.db.base import Base
from app.modules.provider_contract import ProviderResponse, ProviderStatus
from app.modules.queue.infrastructure import (
    get_queue_counter_repository,
    get_queue_repository,
    get_queue_ticket_repository,
)
from app.modules.queue.interfaces import (
    QueueCounterRepository,
    QueueRepository,
    QueueTicketRepository,
)
from app.modules.queue.mappers import QueueCounterMapper, QueueMapper, QueueTicketMapper
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
from app.modules.queue.repositories import (
    SqlAlchemyQueueCounterRepository,
    SqlAlchemyQueueRepository,
    SqlAlchemyQueueTicketRepository,
)


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


def _qid() -> uuid.UUID:
    return uuid.uuid4()


def _sample_queue(**overrides: object) -> Queue:
    data: dict[str, object] = {
        "queue_id": _qid(),
        "organization_id": _qid(),
        "name": "Lobby A",
        "description": "Main lobby",
        "status": QueueStatus.OPEN,
        "policy": QueuePolicy.FIFO,
    }
    data.update(overrides)
    return Queue(**data)  # type: ignore[arg-type]


def _sample_ticket(queue_id: uuid.UUID, **overrides: object) -> QueueTicket:
    data: dict[str, object] = {
        "ticket_id": _qid(),
        "queue_id": queue_id,
        "ticket_number": "A001",
        "priority": QueuePriority.NORMAL,
        "status": QueueTicketStatus.WAITING,
        "created_at": datetime(2026, 7, 24, 10, 0, 0, tzinfo=timezone.utc),
    }
    data.update(overrides)
    return QueueTicket(**data)  # type: ignore[arg-type]


def _sample_counter(**overrides: object) -> QueueCounter:
    data: dict[str, object] = {
        "counter_id": _qid(),
        "name": "Counter 1",
        "status": QueueStatus.OPEN,
    }
    data.update(overrides)
    return QueueCounter(**data)  # type: ignore[arg-type]


@asynccontextmanager
async def _async_session() -> AsyncIterator[AsyncSession]:
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
                text("DELETE FROM queue_tickets WHERE ticket_number LIKE 'T063-%'")
            )
            await conn.execute(
                text("DELETE FROM queue_counters WHERE name LIKE 'T063-%'")
            )
            await conn.execute(text("DELETE FROM queues WHERE name LIKE 'T063-%'"))
        await engine.dispose()


def _run(coro):  # type: ignore[no-untyped-def]
    return asyncio.run(coro)


# --- Mapper ---


def test_queue_mapper_roundtrip() -> None:
    domain = _sample_queue()
    row = QueueMapper.to_orm(domain)
    assert isinstance(row, QueueORM)
    assert row.status == "OPEN"
    restored = QueueMapper.to_domain(row)
    assert restored == domain
    assert type(restored) is Queue


def test_ticket_mapper_roundtrip() -> None:
    domain = _sample_ticket(_qid(), priority=QueuePriority.VIP)
    row = QueueTicketMapper.to_orm(domain)
    assert row.priority == "VIP"
    assert QueueTicketMapper.to_domain(row) == domain


def test_counter_mapper_roundtrip_keeps_queue_id_out_of_domain() -> None:
    qid = _qid()
    domain = _sample_counter()
    row = QueueCounterMapper.to_orm(qid, domain)
    assert row.queue_id == qid
    restored = QueueCounterMapper.to_domain(row)
    assert restored == domain
    assert not hasattr(restored, "queue_id")


def test_mapper_apply_to_orm() -> None:
    domain = _sample_queue()
    row = QueueMapper.to_orm(domain)
    updated = _sample_queue(
        queue_id=domain.queue_id,
        organization_id=domain.organization_id,
        name="Renamed",
        status=QueueStatus.PAUSED,
        policy=QueuePolicy.PRIORITY_QUEUE,
        description="x",
    )
    QueueMapper.apply_to_orm(updated, row)
    assert row.name == "Renamed"
    assert QueueMapper.to_domain(row).status is QueueStatus.PAUSED


# --- ORM ---


def test_orm_table_names() -> None:
    assert QueueORM.__tablename__ == "queues"
    assert QueueTicketORM.__tablename__ == "queue_tickets"
    assert QueueCounterORM.__tablename__ == "queue_counters"


def test_orm_columns_present() -> None:
    queue_cols = {c.name for c in QueueORM.__table__.columns}
    assert {
        "queue_id",
        "organization_id",
        "name",
        "description",
        "status",
        "policy",
        "created_at",
        "updated_at",
    } <= queue_cols
    ticket_cols = {c.name for c in QueueTicketORM.__table__.columns}
    assert {
        "ticket_id",
        "queue_id",
        "ticket_number",
        "priority",
        "status",
        "created_at",
    } <= ticket_cols
    counter_cols = {c.name for c in QueueCounterORM.__table__.columns}
    assert {"counter_id", "queue_id", "name", "status"} <= counter_cols


def test_orm_not_exported_from_queue_package() -> None:
    pkg = importlib.import_module("app.modules.queue")
    assert not hasattr(pkg, "QueueORM")
    assert "QueueORM" not in getattr(pkg, "__all__", [])


def test_orm_fk_and_unique_constraints() -> None:
    ticket_fks = {fk.target_fullname for fk in QueueTicketORM.__table__.foreign_keys}
    assert any(ref.startswith("queues") for ref in ticket_fks)
    uq_names = {c.name for c in QueueTicketORM.__table__.constraints if c.name}
    assert "uq_queue_tickets_queue_id_ticket_number" in uq_names


# --- Interfaces / DI ---


def test_repository_interfaces_are_abstract() -> None:
    assert issubclass(SqlAlchemyQueueRepository, QueueRepository)
    assert issubclass(SqlAlchemyQueueTicketRepository, QueueTicketRepository)
    assert issubclass(SqlAlchemyQueueCounterRepository, QueueCounterRepository)
    with pytest.raises(TypeError):
        QueueRepository()  # type: ignore[misc]


def test_infrastructure_di_returns_interfaces() -> None:
    class _Dummy:
        pass

    session = _Dummy()
    assert isinstance(get_queue_repository(session), QueueRepository)  # type: ignore[arg-type]
    assert isinstance(
        get_queue_ticket_repository(session), QueueTicketRepository  # type: ignore[arg-type]
    )
    assert isinstance(
        get_queue_counter_repository(session), QueueCounterRepository  # type: ignore[arg-type]
    )


# --- Repository (Postgres) ---


@pytest.mark.skipif(not _postgres_available(), reason="PostgreSQL not available")
def test_queue_repository_crud() -> None:
    async def _body() -> None:
        async with _async_session() as session:
            repo = SqlAlchemyQueueRepository(session)
            org = _qid()
            queue = _sample_queue(
                organization_id=org,
                name="T063-Lobby",
                description="persist",
            )
            saved = await repo.add(queue)
            assert saved.queue_id == queue.queue_id
            loaded = await repo.get_by_id(queue.queue_id)
            assert loaded is not None
            assert loaded.name == "T063-Lobby"
            paused = Queue(
                queue_id=queue.queue_id,
                organization_id=org,
                name="T063-Lobby",
                description="persist",
                status=QueueStatus.PAUSED,
                policy=QueuePolicy.FIFO,
            )
            updated = await repo.update(paused)
            assert updated.status is QueueStatus.PAUSED
            listed = await repo.list_by_organization(org)
            assert any(q.queue_id == queue.queue_id for q in listed)
            assert await repo.delete(queue.queue_id) is True
            assert await repo.get_by_id(queue.queue_id) is None

    _run(_body())


@pytest.mark.skipif(not _postgres_available(), reason="PostgreSQL not available")
def test_ticket_and_counter_repositories() -> None:
    async def _body() -> None:
        async with _async_session() as session:
            queues = SqlAlchemyQueueRepository(session)
            tickets = SqlAlchemyQueueTicketRepository(session)
            counters = SqlAlchemyQueueCounterRepository(session)

            queue = _sample_queue(name="T063-Svc")
            await queues.add(queue)

            ticket = _sample_ticket(
                queue.queue_id,
                ticket_number="T063-0001",
                status=QueueTicketStatus.WAITING,
            )
            saved_ticket = await tickets.add(ticket)
            assert saved_ticket.ticket_number == "T063-0001"
            waiting = await tickets.list_by_queue_and_status(
                queue.queue_id, QueueTicketStatus.WAITING.value
            )
            assert len(waiting) == 1

            called = QueueTicket(
                ticket_id=ticket.ticket_id,
                queue_id=queue.queue_id,
                ticket_number="T063-0001",
                priority=QueuePriority.NORMAL,
                status=QueueTicketStatus.CALLED,
                created_at=ticket.created_at,
            )
            updated = await tickets.update(called)
            assert updated.status is QueueTicketStatus.CALLED

            counter = _sample_counter(name="T063-C1")
            saved_counter = await counters.add(queue.queue_id, counter)
            assert saved_counter.name == "T063-C1"
            listed = await counters.list_by_queue(queue.queue_id)
            assert len(listed) == 1

            assert await tickets.delete(ticket.ticket_id) is True
            assert await counters.delete(counter.counter_id) is True
            assert await queues.delete(queue.queue_id) is True

    _run(_body())


@pytest.mark.skipif(not _postgres_available(), reason="PostgreSQL not available")
def test_repository_returns_domain_not_orm() -> None:
    async def _body() -> None:
        async with _async_session() as session:
            repo = SqlAlchemyQueueRepository(session)
            queue = _sample_queue(name="T063-DomainOnly")
            saved = await repo.add(queue)
            assert type(saved) is Queue
            assert not isinstance(saved, QueueORM)
            loaded = await repo.get_by_id(queue.queue_id)
            assert type(loaded) is Queue
            await repo.delete(queue.queue_id)

    _run(_body())


# --- Migration ---


def test_migration_file_structure() -> None:
    path = (
        Path(__file__).resolve().parents[1]
        / "alembic"
        / "versions"
        / "0027_queue_persistence.py"
    )
    assert path.is_file()
    source = path.read_text(encoding="utf-8")
    assert 'revision: str = "0027_queue_persistence"' in source
    assert 'down_revision: Union[str, None] = "0026_complaint_source_target"' in source
    assert '"queues"' in source
    assert "queue_tickets" in source
    assert "queue_counters" in source
    assert "no seed" in source.lower()


def test_migration_module_callable() -> None:
    path = (
        Path(__file__).resolve().parents[1]
        / "alembic"
        / "versions"
        / "0027_queue_persistence.py"
    )
    ns: dict[str, object] = {}
    exec(compile(path.read_text(encoding="utf-8"), str(path), "exec"), ns)
    assert ns["revision"] == "0027_queue_persistence"
    assert ns["down_revision"] == "0026_complaint_source_target"
    assert callable(ns["upgrade"])
    assert callable(ns["downgrade"])


@pytest.mark.skipif(not _postgres_available(), reason="PostgreSQL not available")
def test_migration_tables_exist_or_creatable() -> None:
    settings = get_settings()
    eng = create_engine(settings.database_url, pool_pre_ping=True, future=True)
    try:
        insp = inspect(eng)
        if not insp.has_table("queues"):
            import app.modules.queue.orm  # noqa: F401

            Base.metadata.create_all(
                eng,
                tables=[
                    QueueORM.__table__,
                    QueueTicketORM.__table__,
                    QueueCounterORM.__table__,
                ],
            )
            insp = inspect(eng)
        assert insp.has_table("queues")
        assert insp.has_table("queue_tickets")
        assert insp.has_table("queue_counters")
        cols = {c["name"] for c in insp.get_columns("queues")}
        assert "queue_id" in cols and "organization_id" in cols
    finally:
        eng.dispose()


# --- Docker ---


def test_docker_compose_declares_postgres() -> None:
    compose_path = Path(__file__).resolve().parents[2] / "docker-compose.yml"
    assert compose_path.is_file()
    data = yaml.safe_load(compose_path.read_text(encoding="utf-8"))
    services = data.get("services") or {}
    assert "postgres" in services
    assert "postgres" in (services["postgres"].get("image") or "")
    assert "backend" in services


def test_docker_daemon_or_skip() -> None:
    import shutil
    import subprocess

    if shutil.which("docker") is None:
        pytest.skip("docker CLI not installed")
    result = subprocess.run(
        ["docker", "info"],
        capture_output=True,
        text=True,
        timeout=15,
    )
    if result.returncode != 0:
        pytest.skip("docker daemon not running")
    assert "Server Version" in result.stdout or "Containers" in result.stdout


# --- Layer / security / regression ---


def test_domain_and_application_have_no_orm_imports() -> None:
    root = Path(__file__).resolve().parents[1] / "app" / "modules" / "queue"
    targets = [root / "models.py", *(root / "application").rglob("*.py")]
    for path in targets:
        source = path.read_text(encoding="utf-8")
        tree = ast.parse(source)
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                names = [a.name for a in node.names]
            elif isinstance(node, ast.ImportFrom) and node.module:
                names = [node.module]
            else:
                continue
            for mod in names:
                assert "orm" not in mod.split("."), f"{path.name} imports {mod}"
                assert not mod.startswith("sqlalchemy")


def test_interfaces_have_no_sqlalchemy() -> None:
    root = (
        Path(__file__).resolve().parents[1]
        / "app"
        / "modules"
        / "queue"
        / "interfaces"
    )
    for path in root.rglob("*.py"):
        assert "sqlalchemy" not in path.read_text(encoding="utf-8")


def test_repositories_use_parameterized_sqlalchemy_api() -> None:
    root = (
        Path(__file__).resolve().parents[1]
        / "app"
        / "modules"
        / "queue"
        / "repositories"
    )
    for path in root.rglob("*.py"):
        source = path.read_text(encoding="utf-8")
        assert "text(f" not in source
        assert ".execute(f" not in source
        assert "raw_sql" not in source.lower()


def test_regression_domain_and_application_still_importable() -> None:
    from app.modules.queue.application import (
        CreateQueueCommand,
        CreateQueueHandler,
        InMemoryQueueState,
        QueueDomainService,
    )

    state = InMemoryQueueState()
    domain = QueueDomainService()
    handler = CreateQueueHandler(state=state, domain=domain)
    dto = handler.handle(
        CreateQueueCommand(
            organization_id=_qid(),
            name="Regression Queue",
            description="",
            policy=QueuePolicy.FIFO,
        )
    )
    assert dto.name == "Regression Queue"


def test_regression_provider_contract_untouched() -> None:
    response = ProviderResponse(
        provider_name="email-stub",
        status=ProviderStatus.READY,
        correlation_id="corr-063",
    )
    assert response.status is ProviderStatus.READY


def test_no_fastapi_routes_outside_queue_api() -> None:
    """REST lives under api/ only (TASK-064). Domain/app/persistence stay clean."""
    root = Path(__file__).resolve().parents[1] / "app" / "modules" / "queue"
    api_root = root / "api"
    for path in root.rglob("*.py"):
        if api_root in path.parents or path.parent == api_root:
            continue
        source = path.read_text(encoding="utf-8")
        assert "APIRouter" not in source
        assert "@router." not in source
