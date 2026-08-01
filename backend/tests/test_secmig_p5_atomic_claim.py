"""TASK-PLATFORM-SECMIG-P5-001A — Atomic Claim concurrency tests."""

from __future__ import annotations

import itertools
import threading
import uuid
from collections.abc import Generator
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

import pytest
from sqlalchemy import create_engine, select
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.ext.compiler import compiles
from sqlalchemy.orm import Session, sessionmaker
from tests.cm_batch1_helpers import confirmed_create

from app.db.base import Base
from app.integrations.customer import StubCustomerProvider
from app.modules.audit.models import SystemAuditLog
from app.modules.cm_batch1.duplicate_config import DuplicateConfig
from app.modules.cm_batch1.enumeration import EnumerationGuard
from app.modules.cm_batch1.exceptions import ReplayConflict
from app.modules.cm_batch1.models import (
    CmBatch1ChannelMessageORM,
    CmBatch1ComplaintORM,
    CmBatch1CustomerLockORM,
    CmBatch1DuplicateDecisionORM,
    CmBatch1IdempotencyORM,
    CmBatch1LaterReviewItemORM,
    CmBatch1NumberCounterORM,
    CmBatch1OutboxORM,
)
from app.modules.cm_batch1.outbox_repository import OutboxRepository
from app.modules.cm_batch1.repository import CmBatch1Repository
from app.modules.cm_batch1.schemas import CreateComplaintBatch1Request
from app.modules.cm_batch1.service import CmBatch1Service
from app.modules.cm_batch1.side_effects import CmBatch1SideEffectRecorder
from app.modules.cm_batch1.store import Batch1Store
from app.modules.timeline.models import TimelineEntryORM

pytestmark = pytest.mark.security


@compiles(JSONB, "sqlite")
def _compile_jsonb_sqlite(_type, _compiler, **_kw):  # type: ignore[no-untyped-def]
    return "TEXT"


_BATCH1_TABLES = [
    CmBatch1ComplaintORM.__table__,
    CmBatch1IdempotencyORM.__table__,
    CmBatch1ChannelMessageORM.__table__,
    CmBatch1CustomerLockORM.__table__,
    CmBatch1NumberCounterORM.__table__,
    CmBatch1DuplicateDecisionORM.__table__,
    CmBatch1LaterReviewItemORM.__table__,
    CmBatch1OutboxORM.__table__,
    SystemAuditLog.__table__,
    TimelineEntryORM.__table__,
]


def _body(**overrides: Any) -> CreateComplaintBatch1Request:
    payload = {
        "customerId": "CUST-10001",
        "category": "BILLING",
        "channel": "BRANCH",
        "subject": "Sub",
        "description": "Desc",
    }
    payload.update(overrides)
    return CreateComplaintBatch1Request(**payload)


@pytest.fixture()
def db_session() -> Generator[Session, None, None]:
    engine = create_engine("sqlite:///:memory:", future=True)
    Base.metadata.create_all(engine, tables=_BATCH1_TABLES)
    factory = sessionmaker(bind=engine, autoflush=False, autocommit=False, future=True)
    session = factory()
    try:
        yield session
    finally:
        session.close()
        engine.dispose()


@pytest.fixture()
def repo(db_session: Session) -> CmBatch1Repository:
    return CmBatch1Repository(db_session)


@pytest.fixture()
def service(db_session: Session) -> CmBatch1Service:
    return CmBatch1Service(
        customer_provider=StubCustomerProvider(),
        guard=EnumerationGuard(max_failures=3, window_seconds=60, block_seconds=30),
        store=CmBatch1Repository(db_session),
        side_effects=CmBatch1SideEffectRecorder(db_session),
    )


def _seed_complaint(
    session: Session,
    *,
    request_id: str | None = None,
    channel_message_id: str | None = None,
) -> str:
    cid = uuid.uuid4()
    now = datetime.now(UTC)
    session.add(
        CmBatch1ComplaintORM(
            id=cid,
            complaint_number=f"CM-{cid.hex[:8].upper()}",
            customer_id="CUST-10001",
            category="BILLING",
            channel="BRANCH",
            subject="seed",
            description="seed",
            priority="MEDIUM",
            status="REGISTERED",
            case_created=False,
            created_by=None,
            created_at=now,
            updated_at=now,
        )
    )
    if request_id is not None:
        session.add(
            CmBatch1IdempotencyORM(
                request_id=request_id,
                complaint_id=cid,
                created_at=now,
            )
        )
    if channel_message_id is not None:
        session.add(
            CmBatch1ChannelMessageORM(
                channel_message_id=channel_message_id,
                complaint_id=cid,
                created_at=now,
            )
        )
    session.flush()
    return str(cid)


def test_regression_request_id_replay(
    service: CmBatch1Service, db_session: Session
) -> None:
    first = confirmed_create(
        service, _body(), request_id="p5-reg-1", channel_message_id=None, actor_id="a"
    )
    second = confirmed_create(
        service,
        _body(subject="changed"),
        request_id="p5-reg-1",
        channel_message_id=None,
        actor_id="a",
    )
    assert first.replayed is False
    assert second.replayed is True
    assert second.complaint_id == first.complaint_id
    outbox = OutboxRepository(db_session).list_unpublished(limit=50)
    assert sum(1 for r in outbox if r.event_id == "EVT-CM-001") == 1
    assert sum(1 for r in outbox if r.event_id == "EVT-CM-002") == 1


def test_regression_channel_message_replay(service: CmBatch1Service) -> None:
    first = confirmed_create(
        service,
        _body(channel="CHANNEL"),
        request_id="p5-ch-1",
        channel_message_id="MSG-P5",
        actor_id="a",
    )
    second = confirmed_create(
        service,
        _body(channel="CHANNEL", subject="other"),
        request_id="p5-ch-2",
        channel_message_id="MSG-P5",
        actor_id="a",
    )
    assert second.replayed is True
    assert second.complaint_id == first.complaint_id


def test_dual_key_ownership_conflict(repo: CmBatch1Repository, db_session: Session) -> None:
    a = _seed_complaint(db_session, request_id="K-CONFLICT")
    b = _seed_complaint(db_session, channel_message_id="M-CONFLICT")
    assert a != b
    with pytest.raises(ReplayConflict) as exc:
        repo.resolve_create_keys("K-CONFLICT", "M-CONFLICT")
    assert exc.value.code == "REPLAY_CONFLICT"
    # R4 — public envelope must not disclose foreign ComplaintIds.
    assert exc.value.details == {"reason": "idempotency_channel_conflict"}
    assert a not in str(exc.value.details)
    assert b not in str(exc.value.details)
    assert exc.value.diagnostic_details["requestComplaintId"] == a
    assert exc.value.diagnostic_details["channelComplaintId"] == b


def test_dual_key_conflict_via_create(
    repo: CmBatch1Repository, db_session: Session
) -> None:
    _seed_complaint(db_session, request_id="K-C2")
    _seed_complaint(db_session, channel_message_id="M-C2")
    with pytest.raises(ReplayConflict):
        repo.create(
            customer_id="CUST-10001",
            category="BILLING",
            channel="BRANCH",
            subject="x",
            description="y",
            priority="MEDIUM",
            created_by=None,
            request_id="K-C2",
            channel_message_id="M-C2",
        )


def test_dual_key_conflict_in_memory_store() -> None:
    store = Batch1Store()
    store.reset()
    a, _ = store.create(
        customer_id="CUST-10001",
        category="BILLING",
        channel="BRANCH",
        subject="a",
        description="a",
        priority="MEDIUM",
        created_by=None,
        request_id="K-A",
        channel_message_id=None,
    )
    b, _ = store.create(
        customer_id="CUST-10001",
        category="BILLING",
        channel="BRANCH",
        subject="b",
        description="b",
        priority="MEDIUM",
        created_by=None,
        request_id="K-B",
        channel_message_id="M-B",
    )
    # Force inconsistent mapping: K-A → A, M-B already → B; attach M-B lookup with K-A
    store._channel_msg["M-SHARED"] = store._idempotency["K-B"]
    store._idempotency["K-SHARED"] = store._idempotency["K-A"]
    _ = a, b
    with pytest.raises(ReplayConflict):
        store.resolve_create_keys("K-SHARED", "M-SHARED")


def test_conflict_recovery_preserves_outer_work(
    repo: CmBatch1Repository, db_session: Session
) -> None:
    """Lost Atomic Claim must not wipe unrelated rows (no full-session rollback)."""
    survivor_id = _seed_complaint(db_session, request_id="outer-survivor")
    # Pre-claim the target key so the Atomic Claim misses.
    _seed_complaint(db_session, request_id="race-key")

    row, created = repo.create(
        customer_id="CUST-10001",
        category="BILLING",
        channel="BRANCH",
        subject="loser",
        description="loser",
        priority="MEDIUM",
        created_by=None,
        request_id="race-key",
        channel_message_id=None,
    )
    assert created is False
    assert row.complaint_id != survivor_id

    # Outer session still sees the unrelated survivor.
    survivor = db_session.get(CmBatch1ComplaintORM, uuid.UUID(survivor_id))
    assert survivor is not None
    assert (
        db_session.scalar(
            select(CmBatch1IdempotencyORM).where(
                CmBatch1IdempotencyORM.request_id == "outer-survivor"
            )
        )
        is not None
    )


def test_winner_loser_unified_replay_emits_evt_cm_002(
    service: CmBatch1Service, db_session: Session
) -> None:
    """created=False path uses the same CreateReplayed pipeline as early replay."""
    winner = confirmed_create(
        service, _body(), request_id="p5-wl-1", channel_message_id=None, actor_id="w"
    )
    # Bypass service early resolve by calling repository create directly after commit.
    repo = CmBatch1Repository(db_session)
    row, created = repo.create(
        customer_id="CUST-10001",
        category="BILLING",
        channel="BRANCH",
        subject="x",
        description="y",
        priority="MEDIUM",
        created_by="l",
        request_id="p5-wl-1",
        channel_message_id=None,
    )
    assert created is False
    assert row.complaint_id == winner.complaint_id

    # Service-level loser (post-validate claim miss) must still emit EVT-CM-002.
    # Simulate by creating via service again (early resolve → replay pipeline).
    loser = confirmed_create(
        service, _body(), request_id="p5-wl-1", channel_message_id=None, actor_id="l"
    )
    assert loser.replayed is True
    assert loser.complaint_id == winner.complaint_id

    outbox = OutboxRepository(db_session).list_unpublished(limit=50)
    assert sum(1 for r in outbox if r.event_id == "EVT-CM-001") == 1
    # Stable outbox idempotency key EVT-CM-002:{request_id} → single row
    assert sum(1 for r in outbox if r.event_id == "EVT-CM-002") == 1


def test_concurrent_replay_single_winner(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    """Two sessions racing the same Idempotency-Key → one create, one replay."""
    db_path = tmp_path / "p5_concurrent.sqlite"
    engine = create_engine(
        f"sqlite:///{db_path}",
        connect_args={"check_same_thread": False, "timeout": 30},
        future=True,
    )
    Base.metadata.create_all(engine, tables=_BATCH1_TABLES)
    factory = sessionmaker(bind=engine, autoflush=False, autocommit=False, future=True)

    # Isolate the Idempotency-Key claim race from SQLite counter isolation limits.
    seq = itertools.count(1)
    seq_lock = threading.Lock()

    def _local_next(self: CmBatch1Repository) -> str:
        with seq_lock:
            return f"CM-{next(seq):08d}"

    monkeypatch.setattr(CmBatch1Repository, "_next_complaint_number", _local_next)

    barrier = threading.Barrier(2)
    results: list[tuple[str, bool]] = []
    errors: list[BaseException] = []
    lock = threading.Lock()

    def worker() -> None:
        session = factory()
        try:
            repo = CmBatch1Repository(session)
            barrier.wait(timeout=5)
            row, created = repo.create(
                customer_id="CUST-10001",
                category="BILLING",
                channel="BRANCH",
                subject="race",
                description="race",
                priority="MEDIUM",
                created_by=None,
                request_id="p5-concurrent",
                channel_message_id=None,
            )
            session.commit()
            with lock:
                results.append((row.complaint_id, created))
        except BaseException as exc:  # noqa: BLE001 — collect for assertion
            with lock:
                errors.append(exc)
            session.rollback()
        finally:
            session.close()

    t1 = threading.Thread(target=worker)
    t2 = threading.Thread(target=worker)
    t1.start()
    t2.start()
    t1.join(timeout=10)
    t2.join(timeout=10)

    assert errors == [], f"worker errors: {errors!r}"
    assert len(results) == 2
    ids = {r[0] for r in results}
    created_flags = sorted(r[1] for r in results)
    assert len(ids) == 1
    assert created_flags == [False, True]

    verify = factory()
    try:
        rows = verify.scalars(select(CmBatch1ComplaintORM)).all()
        assert len(rows) == 1
        keys = verify.scalars(select(CmBatch1IdempotencyORM)).all()
        assert len(keys) == 1
        assert keys[0].request_id == "p5-concurrent"
    finally:
        verify.close()
        engine.dispose()


def test_race_loser_service_pipeline_without_early_hit(
    db_session: Session,
) -> None:
    """If create returns created=False, service still commits CreateReplayed."""

    class _ClaimMissThenHit(CmBatch1Repository):
        def __init__(self, session: Session) -> None:
            super().__init__(session)
            self._missed_once = False

        def resolve_create_keys(
            self,
            request_id: str,
            channel_message_id: str | None,
        ):
            # First service peek misses so validation + create run; create hits.
            if not self._missed_once:
                self._missed_once = True
                return None
            return super().resolve_create_keys(request_id, channel_message_id)

    # Seed winning aggregate under the key for a different customer to avoid
    # FR-003 duplicate warning on the forced create path.
    cid = uuid.uuid4()
    now = datetime.now(UTC)
    db_session.add(
        CmBatch1ComplaintORM(
            id=cid,
            complaint_number="CM-LOSERSEED",
            customer_id="CUST-10002",
            category="BILLING",
            channel="BRANCH",
            subject="seed",
            description="seed",
            priority="MEDIUM",
            status="REGISTERED",
            case_created=False,
            created_by=None,
            created_at=now,
            updated_at=now,
        )
    )
    db_session.add(
        CmBatch1IdempotencyORM(
            request_id="p5-forced-loser",
            complaint_id=cid,
            created_at=now,
        )
    )
    db_session.commit()

    svc = CmBatch1Service(
        customer_provider=StubCustomerProvider(),
        guard=EnumerationGuard(max_failures=3, window_seconds=60, block_seconds=30),
        store=_ClaimMissThenHit(db_session),
        side_effects=CmBatch1SideEffectRecorder(db_session),
        duplicate_config=DuplicateConfig(enforce_on_create=False),
    )
    result = confirmed_create(
        svc,
        _body(customerId="CUST-10002"),
        request_id="p5-forced-loser",
        channel_message_id=None,
        actor_id="loser",
    )
    assert result.replayed is True
    assert result.complaint_id == str(cid)
    outbox = OutboxRepository(db_session).list_unpublished(limit=20)
    assert any(r.event_id == "EVT-CM-002" for r in outbox)
    assert not any(r.event_id == "EVT-CM-001" for r in outbox)


def test_no_full_session_rollback_on_claim_conflict(
    repo: CmBatch1Repository, db_session: Session
) -> None:
    """Guardrail: create path must not call session.rollback() on claim miss."""
    rolled_back = {"count": 0}
    original = db_session.rollback

    def _counting_rollback() -> None:
        rolled_back["count"] += 1
        return original()

    db_session.rollback = _counting_rollback  # type: ignore[method-assign]
    _seed_complaint(db_session, request_id="p5-no-full-rb")
    row, created = repo.create(
        customer_id="CUST-10001",
        category="BILLING",
        channel="BRANCH",
        subject="x",
        description="y",
        priority="MEDIUM",
        created_by=None,
        request_id="p5-no-full-rb",
        channel_message_id=None,
    )
    assert created is False
    assert row is not None
    assert rolled_back["count"] == 0


# --- P5-001A rework R1–R4 ---


def test_r1_lost_request_claim_never_phantom_new(
    repo: CmBatch1Repository, db_session: Session, monkeypatch: pytest.MonkeyPatch
) -> None:
    """Lost request claim must raise — never return created=True for deleted ORM."""

    def _always_lose(self: CmBatch1Repository, *args: Any, **kwargs: Any) -> bool:
        return False

    monkeypatch.setattr(CmBatch1Repository, "_claim_insert", _always_lose)

    with pytest.raises(RuntimeError, match="Atomic claim lost without a visible winner"):
        repo.create(
            customer_id="CUST-10001",
            category="BILLING",
            channel="BRANCH",
            subject="phantom",
            description="phantom",
            priority="MEDIUM",
            created_by=None,
            request_id="p5-r1-lost",
            channel_message_id=None,
        )
    assert db_session.scalars(select(CmBatch1ComplaintORM)).all() == []
    assert (
        db_session.scalar(
            select(CmBatch1IdempotencyORM).where(
                CmBatch1IdempotencyORM.request_id == "p5-r1-lost"
            )
        )
        is None
    )


def test_r2_race_loser_replay_authorizes_actual_resource(
    db_session: Session,
) -> None:
    """created=False replay must authorize the actual Complaint before side effects."""
    from app.core.errors import OrgScopeDeniedError

    winner_id = _seed_complaint(db_session, request_id="p5-r2-race")
    db_session.commit()

    class _ClaimMissThenHit(CmBatch1Repository):
        def __init__(self, session: Session) -> None:
            super().__init__(session)
            self._missed_once = False

        def resolve_create_keys(
            self,
            request_id: str,
            channel_message_id: str | None,
        ):
            if not self._missed_once:
                self._missed_once = True
                return None
            return super().resolve_create_keys(request_id, channel_message_id)

    authorized: list[str] = []

    def _deny_wrong_org(complaint_id: str) -> None:
        authorized.append(complaint_id)
        raise OrgScopeDeniedError("Organization scope denied")

    svc = CmBatch1Service(
        customer_provider=StubCustomerProvider(),
        guard=EnumerationGuard(max_failures=3, window_seconds=60, block_seconds=30),
        store=_ClaimMissThenHit(db_session),
        side_effects=CmBatch1SideEffectRecorder(db_session),
        duplicate_config=DuplicateConfig(enforce_on_create=False),
    )
    svc.confirm_customer("CUST-10001", principal_key="loser")
    with pytest.raises(OrgScopeDeniedError):
        svc.create_complaint(
            _body(),
            request_id="p5-r2-race",
            channel_message_id=None,
            actor_id="loser",
            authorize_replay=_deny_wrong_org,
        )
    assert authorized == [winner_id]
    assert OutboxRepository(db_session).list_unpublished(limit=20) == []


def test_r3_channel_winner_preserves_request_id_alias(
    repo: CmBatch1Repository, db_session: Session
) -> None:
    """After channel ownership wins, request_id must resolve to the same ComplaintId."""
    canonical = _seed_complaint(db_session, channel_message_id="M-R3-WIN")
    row, created = repo.create(
        customer_id="CUST-10001",
        category="BILLING",
        channel="CHANNEL",
        subject="alias",
        description="alias",
        priority="MEDIUM",
        created_by=None,
        request_id="K-R3-NEW",
        channel_message_id="M-R3-WIN",
    )
    assert created is False
    assert row.complaint_id == canonical
    aliased = repo.get_idempotent("K-R3-NEW")
    assert aliased is not None
    assert aliased.complaint_id == canonical
    again, created_again = repo.create(
        customer_id="CUST-10001",
        category="BILLING",
        channel="CHANNEL",
        subject="alias-2",
        description="alias-2",
        priority="MEDIUM",
        created_by=None,
        request_id="K-R3-NEW",
        channel_message_id=None,
    )
    assert created_again is False
    assert again.complaint_id == canonical


def test_r3_request_replay_binds_channel_alias(
    service: CmBatch1Service, db_session: Session
) -> None:
    """POST(K) → X; POST(K, M) replay must permanently bind M → X.

    Subsequent POST(K2, M) must replay X — never create Y.
    """
    first = confirmed_create(
        service,
        _body(),
        request_id="K-CONV",
        channel_message_id=None,
        actor_id="a",
    )
    assert first.replayed is False
    x = first.complaint_id

    second = confirmed_create(
        service,
        _body(subject="replay-with-channel"),
        request_id="K-CONV",
        channel_message_id="M-CONV",
        actor_id="a",
    )
    assert second.replayed is True
    assert second.complaint_id == x

    third = confirmed_create(
        service,
        _body(subject="new-request-same-channel"),
        request_id="K2-CONV",
        channel_message_id="M-CONV",
        actor_id="a",
    )
    assert third.replayed is True
    assert third.complaint_id == x

    repo = CmBatch1Repository(db_session)
    by_req = repo.get_idempotent("K-CONV")
    by_ch = repo.get_by_channel_message("M-CONV")
    by_k2 = repo.get_idempotent("K2-CONV")
    assert by_req is not None and by_req.complaint_id == x
    assert by_ch is not None and by_ch.complaint_id == x
    assert by_k2 is not None and by_k2.complaint_id == x
    assert len(db_session.scalars(select(CmBatch1ComplaintORM)).all()) == 1


def test_r3_in_memory_channel_replay_binds_request_id() -> None:
    store = Batch1Store()
    store.reset()
    first, _ = store.create(
        customer_id="CUST-10001",
        category="BILLING",
        channel="CHANNEL",
        subject="a",
        description="a",
        priority="MEDIUM",
        created_by=None,
        request_id="K-MEM-1",
        channel_message_id="M-MEM",
    )
    second, created = store.create(
        customer_id="CUST-10001",
        category="BILLING",
        channel="CHANNEL",
        subject="b",
        description="b",
        priority="MEDIUM",
        created_by=None,
        request_id="K-MEM-2",
        channel_message_id="M-MEM",
    )
    assert created is False
    assert second.complaint_id == first.complaint_id
    assert store.get_idempotent("K-MEM-2") is not None
    assert store.get_idempotent("K-MEM-2").complaint_id == first.complaint_id  # type: ignore[union-attr]


def test_r3_in_memory_request_replay_binds_channel() -> None:
    store = Batch1Store()
    store.reset()
    first, _ = store.create(
        customer_id="CUST-10001",
        category="BILLING",
        channel="BRANCH",
        subject="a",
        description="a",
        priority="MEDIUM",
        created_by=None,
        request_id="K-MEM-REQ",
        channel_message_id=None,
    )
    second, created = store.create(
        customer_id="CUST-10001",
        category="BILLING",
        channel="BRANCH",
        subject="b",
        description="b",
        priority="MEDIUM",
        created_by=None,
        request_id="K-MEM-REQ",
        channel_message_id="M-MEM-BIND",
    )
    assert created is False
    assert second.complaint_id == first.complaint_id
    assert store.get_by_channel_message("M-MEM-BIND") is not None
    assert (
        store.get_by_channel_message("M-MEM-BIND").complaint_id  # type: ignore[union-attr]
        == first.complaint_id
    )
    third, created_third = store.create(
        customer_id="CUST-10001",
        category="BILLING",
        channel="BRANCH",
        subject="c",
        description="c",
        priority="MEDIUM",
        created_by=None,
        request_id="K-MEM-REQ-2",
        channel_message_id="M-MEM-BIND",
    )
    assert created_third is False
    assert third.complaint_id == first.complaint_id


def test_r4_replay_conflict_response_hides_complaint_ids(
    repo: CmBatch1Repository, db_session: Session
) -> None:
    a = _seed_complaint(db_session, request_id="K-R4")
    b = _seed_complaint(db_session, channel_message_id="M-R4")
    with pytest.raises(ReplayConflict) as exc:
        repo.create(
            customer_id="CUST-10001",
            category="BILLING",
            channel="BRANCH",
            subject="x",
            description="y",
            priority="MEDIUM",
            created_by=None,
            request_id="K-R4",
            channel_message_id="M-R4",
        )
    public = exc.value.details or {}
    blob = str(public)
    assert a not in blob
    assert b not in blob
    assert "requestComplaintId" not in public
    assert "channelComplaintId" not in public
    assert public.get("reason") == "idempotency_channel_conflict"
    assert exc.value.diagnostic_details["requestComplaintId"] == a
    assert exc.value.diagnostic_details["channelComplaintId"] == b
