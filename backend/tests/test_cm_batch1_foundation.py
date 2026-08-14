"""CM Batch 1 S2 Task 04 — Audit + Timeline + Outbox foundation tests."""

from __future__ import annotations

import uuid
from collections.abc import Generator
from pathlib import Path
from unittest.mock import MagicMock

import pytest
from alembic.config import Config
from alembic.script import ScriptDirectory
from sqlalchemy import create_engine, select
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.ext.compiler import compiles
from sqlalchemy.orm import Session, sessionmaker

from app.core.errors import ValidationAppError
from app.db.base import Base
from app.integrations.customer import StubCustomerProvider
from app.modules.audit.models import SystemAuditLog
from app.modules.cm_batch1 import event_factory as events
from app.modules.cm_batch1.domain_events import DomainEvent
from app.modules.cm_batch1.enumeration import EnumerationGuard
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
from app.modules.cm_batch1.schemas import (
    CreateComplaintBatch1Request,
    DuplicateDecisionRequest,
)
from app.modules.cm_batch1.service import CmBatch1Service
from app.modules.cm_batch1.side_effects import (
    CmBatch1SideEffectRecorder,
    NoOpSideEffectRecorder,
)
from app.modules.timeline.models import TimelineEntryORM
from cm_batch1_helpers import confirmed_create


@compiles(JSONB, "sqlite")
def _compile_jsonb_sqlite(_type, _compiler, **_kw):  # type: ignore[no-untyped-def]
    return "JSON"


_TABLES = [
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


@pytest.fixture()
def db_session(tmp_path: Path) -> Generator[Session, None, None]:
    db_path = tmp_path / "cm_batch1_foundation.sqlite"
    engine = create_engine(
        f"sqlite:///{db_path}",
        future=True,
        connect_args={"check_same_thread": False},
    )
    Base.metadata.create_all(engine, tables=_TABLES)
    factory = sessionmaker(bind=engine, autoflush=False, autocommit=False, future=True)
    session = factory()
    try:
        yield session
    finally:
        session.close()
        engine.dispose()


@pytest.fixture()
def recorder(db_session: Session) -> CmBatch1SideEffectRecorder:
    return CmBatch1SideEffectRecorder(db_session)


@pytest.fixture()
def service(db_session: Session, recorder: CmBatch1SideEffectRecorder) -> CmBatch1Service:
    return CmBatch1Service(
        customer_provider=StubCustomerProvider(),
        guard=EnumerationGuard(max_failures=3, window_seconds=60, block_seconds=30),
        store=CmBatch1Repository(db_session),
        side_effects=recorder,
    )


def _create_body(**overrides) -> CreateComplaintBatch1Request:
    base = {
        "customerId": "CUST-10001",
        "category": "BILLING",
        "channel": "WEB",
        "subject": "Incorrect billing amount on invoice",
        "description": "Please review my latest bill statement.",
        "priority": "MEDIUM",
    }
    base.update(overrides)
    return CreateComplaintBatch1Request(**base)


# --- Unit: domain events / factory ---


def test_factory_create_maps_evt_cm_001() -> None:
    evt = events.complaint_created(
        complaint_id=str(uuid.uuid4()),
        complaint_number="CM-0001",
        customer_id="CUST-10001",
        request_id="req-1",
        channel_message_id=None,
        actor_id=None,
    )
    assert evt.outbox_event_id == "EVT-CM-001"
    assert evt.timeline_event_type == "ComplaintRegistered"
    assert "justification" not in evt.timeline_metadata
    assert "priority" not in evt.timeline_metadata


def test_factory_link_existing_emits_022_and_023() -> None:
    evts = events.duplicate_decision_events(
        decision="link_existing",
        customer_id="CUST-10001",
        surviving_complaint_id=str(uuid.uuid4()),
        actor_id=None,
        decision_id=str(uuid.uuid4()),
        justification_present=False,
    )
    assert [e.outbox_event_id for e in evts] == ["EVT-CM-022", "EVT-CM-023"]


def test_factory_override_keeps_justification_off_timeline() -> None:
    evt = events.duplicate_decision(
        decision="override",
        customer_id="CUST-10001",
        surviving_complaint_id=str(uuid.uuid4()),
        actor_id=None,
        decision_id=str(uuid.uuid4()),
        justification_present=True,
    )
    assert evt.outbox_event_id == "EVT-CM-021"
    assert "justification" not in (evt.timeline_metadata or {})
    assert evt.payload.get("justificationRef")


def test_noop_recorder_accepts_events() -> None:
    rec = NoOpSideEffectRecorder()
    assert rec.record(
        DomainEvent(
            name="X",
            aggregate_type="Complaint",
            aggregate_id=str(uuid.uuid4()),
            actor_id=None,
            payload={},
            idempotency_key="k1",
            audit_operation="X",
        )
    )


# --- Outbox repository ---


def test_outbox_enqueue_and_idempotent(db_session: Session) -> None:
    repo = OutboxRepository(db_session)
    first = repo.enqueue(
        event_id="EVT-CM-001",
        event_name="ComplaintCreated",
        aggregate_type="Complaint",
        aggregate_id=str(uuid.uuid4()),
        idempotency_key="EVT-CM-001:demo",
        payload={"complaintId": "x"},
    )
    assert first is not None
    second = repo.enqueue(
        event_id="EVT-CM-001",
        event_name="ComplaintCreated",
        aggregate_type="Complaint",
        aggregate_id=first.aggregate_id,
        idempotency_key="EVT-CM-001:demo",
        payload={"complaintId": "x"},
    )
    assert second is None
    db_session.commit()
    unpublished = repo.list_unpublished()
    assert len(unpublished) == 1
    assert unpublished[0].event_id == "EVT-CM-001"
    assert unpublished[0].status == "UNPUBLISHED"


def test_outbox_no_publish_marker_excluded_from_unpublished(
    db_session: Session,
) -> None:
    repo = OutboxRepository(db_session)
    repo.enqueue(
        event_id="NO-PUBLISH",
        event_name="AttachmentBound",
        aggregate_type="Complaint",
        aggregate_id=str(uuid.uuid4()),
        idempotency_key="AttachmentBound:a:b",
        payload={},
    )
    db_session.commit()
    assert repo.list_unpublished() == []


# --- Recorder + create path persistence ---


def test_create_commits_audit_timeline_outbox(
    service: CmBatch1Service, db_session: Session
) -> None:
    created = confirmed_create(service,
        _create_body(),
        request_id="foundation-create-1",
        channel_message_id=None,
        actor_id=None,
    )
    assert created.replayed is False

    outbox = OutboxRepository(db_session).list_by_aggregate(
        aggregate_type="Complaint", aggregate_id=created.complaint_id
    )
    assert any(r.event_id == "EVT-CM-001" for r in outbox)

    audits = db_session.scalars(
        select(SystemAuditLog).where(SystemAuditLog.event_type == "ComplaintCreated")
    ).all()
    assert len(audits) == 1

    timelines = db_session.scalars(
        select(TimelineEntryORM).where(
            TimelineEntryORM.event_type == "ComplaintRegistered"
        )
    ).all()
    assert len(timelines) == 1


def test_idempotent_replay_emits_evt_cm_002_once(
    service: CmBatch1Service, db_session: Session
) -> None:
    first = confirmed_create(service,
        _create_body(),
        request_id="foundation-replay-1",
        channel_message_id=None,
        actor_id=None,
    )
    second = confirmed_create(service,
        _create_body(),
        request_id="foundation-replay-1",
        channel_message_id=None,
        actor_id=None,
    )
    third = confirmed_create(service,
        _create_body(),
        request_id="foundation-replay-1",
        channel_message_id=None,
        actor_id=None,
    )
    assert first.replayed is False
    assert second.replayed is True
    assert third.replayed is True

    rows = [
        r
        for r in OutboxRepository(db_session).list_unpublished(limit=50)
        if r.event_id in {"EVT-CM-001", "EVT-CM-002"}
    ]
    assert sum(1 for r in rows if r.event_id == "EVT-CM-001") == 1
    assert sum(1 for r in rows if r.event_id == "EVT-CM-002") == 1

    audits = db_session.scalars(select(SystemAuditLog)).all()
    assert sum(1 for a in audits if a.event_type == "ComplaintCreated") == 1
    assert sum(1 for a in audits if a.event_type == "CreateReplayed") == 1


def test_rejected_create_leaves_no_side_effects(
    service: CmBatch1Service, db_session: Session
) -> None:
    with pytest.raises(ValidationAppError):
        service.create_complaint(
            _create_body(customerId=""),
            request_id="foundation-reject-1",
            channel_message_id=None,
            actor_id="actor-1",
            principal_key="actor-1",
        )
    assert db_session.scalars(select(CmBatch1OutboxORM)).all() == []
    assert db_session.scalars(select(SystemAuditLog)).all() == []
    assert db_session.scalars(select(TimelineEntryORM)).all() == []


def test_duplicate_decision_side_effects(
    service: CmBatch1Service, db_session: Session
) -> None:
    created = confirmed_create(service,
        _create_body(),
        request_id="foundation-dup-1",
        channel_message_id=None,
        actor_id=None,
    )
    decision = service.record_duplicate_decision(
        DuplicateDecisionRequest(
            decision="recommend_only",
            customerId="CUST-10001",
            survivingComplaintId=created.complaint_id,
        ),
        actor_id=None,
    )
    outbox = [
        r
        for r in OutboxRepository(db_session).list_unpublished(limit=50)
        if r.event_id == "EVT-CM-024"
    ]
    assert len(outbox) == 1
    assert outbox[0].payload.get("decisionId") == decision.decision_id

    audits = db_session.scalars(
        select(SystemAuditLog).where(
            SystemAuditLog.event_type == "DuplicateDecision:recommend_only"
        )
    ).all()
    assert len(audits) == 1


def test_side_effect_failure_rolls_back_aggregate(
    db_session: Session,
) -> None:
    """If outbox claim fails closed after aggregate flush, whole TX rolls back."""
    boom = MagicMock()
    boom.enqueue.side_effect = RuntimeError("outbox unavailable")
    boom.exists_idempotency_key.return_value = False

    recorder = CmBatch1SideEffectRecorder(
        db_session,
        outbox=boom,
    )
    svc = CmBatch1Service(
        customer_provider=StubCustomerProvider(),
        store=CmBatch1Repository(db_session),
        side_effects=recorder,
    )
    with pytest.raises(RuntimeError, match="outbox unavailable"):
        confirmed_create(svc,
            _create_body(),
            request_id="foundation-tx-fail",
            channel_message_id=None,
            actor_id=None,
        )
    db_session.rollback()
    assert (
        db_session.scalars(select(CmBatch1ComplaintORM)).all() == []
    )
    assert db_session.scalars(select(SystemAuditLog)).all() == []


def test_s3_migration_0043_chain() -> None:
    """S3 readiness — 0043 continues 0042; head may advance with later repairs."""
    backend_root = Path(__file__).resolve().parents[1]
    path = backend_root / "alembic" / "versions" / "0043_cm_batch1_foundation.py"
    ns: dict[str, object] = {}
    exec(compile(path.read_text(encoding="utf-8"), str(path), "exec"), ns)
    assert ns["revision"] == "0043_cm_batch1_foundation"
    assert ns["down_revision"] == "0042_cm_batch1_attachment"
    assert callable(ns["upgrade"])
    assert callable(ns["downgrade"])

    cfg = Config(str(backend_root / "alembic.ini"))
    cfg.set_main_option("script_location", str(backend_root / "alembic"))
    script = ScriptDirectory.from_config(cfg)
    assert script.get_heads() == ["0078_cm_case_handling_claimed_by"]
    revs = {r.revision: r.down_revision for r in script.walk_revisions()}
    assert revs["0040_cm_batch1_persistence"] == "0039_admin_rbac_repair"
    assert revs["0041_cm_batch1_duplicate"] == "0040_cm_batch1_persistence"
    assert revs["0042_cm_batch1_attachment"] == "0041_cm_batch1_duplicate"
    assert revs["0043_cm_batch1_foundation"] == "0042_cm_batch1_attachment"
    assert revs["0044_admin_rbac_repair"] == "0043_cm_batch1_foundation"
    assert revs["0045_cm_b1_lr_complaint_id"] == "0044_admin_rbac_repair"
    assert revs["0046_cm_case_management"] == "0045_cm_b1_lr_complaint_id"


def test_td_ops_003_migration_0044_admin_repair_file() -> None:
    """TD-OPS-003 — ADMIN matrix repair revision exists and is reversible no-op."""
    backend_root = Path(__file__).resolve().parents[1]
    path = backend_root / "alembic" / "versions" / "0044_admin_rbac_repair.py"
    ns: dict[str, object] = {}
    exec(compile(path.read_text(encoding="utf-8"), str(path), "exec"), ns)
    assert ns["revision"] == "0044_admin_rbac_repair"
    assert ns["down_revision"] == "0043_cm_batch1_foundation"
    assert "ADMIN" in ns["_ADMIN_ROLE_CODES"]
    assert "complaints:read" in ns["_ADMIN_PERMS"]
    assert "complaints:create" in ns["_ADMIN_PERMS"]
    assert callable(ns["upgrade"])
    assert callable(ns["downgrade"])


def test_m3d_migration_0045_later_review_complaint_id() -> None:
    """M3d / EX-G — nullable complaint_id on later-review items."""
    backend_root = Path(__file__).resolve().parents[1]
    path = backend_root / "alembic" / "versions" / "0045_cm_b1_lr_complaint_id.py"
    ns: dict[str, object] = {}
    exec(compile(path.read_text(encoding="utf-8"), str(path), "exec"), ns)
    assert ns["revision"] == "0045_cm_b1_lr_complaint_id"
    assert ns["down_revision"] == "0044_admin_rbac_repair"
    assert callable(ns["upgrade"])
    assert callable(ns["downgrade"])
    assert len(str(ns["revision"])) <= 32
