"""FR-030 / DEC-031 Fase 2 — SLA sweep, outbox drain, threshold predicates (TC-030+)."""

from __future__ import annotations

import importlib.util
import sys
import uuid
from collections.abc import Generator
from datetime import UTC, datetime, timedelta
from pathlib import Path
from types import ModuleType
from unittest.mock import patch

import pytest
from sqlalchemy import create_engine, select
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.ext.compiler import compiles
from sqlalchemy.orm import Session, sessionmaker

from app.db.base import Base
from app.modules.audit.models import SystemAuditLog
from app.modules.cm_batch1.models import CmBatch1ComplaintORM, CmBatch1OutboxORM
from app.modules.cm_batch1.ops_hygiene import exclusive_lock, write_heartbeat_marker
from app.modules.cm_batch1.outbox_repository import OutboxRepository
from app.modules.cm_batch1.side_effects import CmBatch1SideEffectRecorder
from app.modules.cm_batch1.sla import resolve_complaint_sla
from app.modules.cm_batch1.sla_sweep import (
    CmBatch1OutboxDrainService,
    CmBatch1SlaSweepService,
)
from app.modules.cm_batch1.sla_thresholds import (
    classify_in_app_threshold,
    crossed_thresholds,
    sla_idempotency_key,
    threshold_at,
)
from app.modules.timeline.models import TimelineEntryORM


def _load_hygiene_cli() -> ModuleType:
    path = Path(__file__).resolve().parents[1] / "scripts" / "cm_batch1_ops_hygiene.py"
    spec = importlib.util.spec_from_file_location("cm_batch1_ops_hygiene_cli", path)
    assert spec is not None and spec.loader is not None
    mod = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = mod
    spec.loader.exec_module(mod)
    return mod


hygiene_cli = _load_hygiene_cli()


@compiles(JSONB, "sqlite")
def _compile_jsonb_sqlite(_type, _compiler, **_kw):  # type: ignore[no-untyped-def]
    return "JSON"


_TABLES = [
    CmBatch1ComplaintORM.__table__,
    CmBatch1OutboxORM.__table__,
    SystemAuditLog.__table__,
    TimelineEntryORM.__table__,
]


@pytest.fixture()
def db_session(tmp_path: Path) -> Generator[Session, None, None]:
    db_path = tmp_path / "cm_batch1_sla_sweep.sqlite"
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


def _seed_open(
    session: Session,
    *,
    created_at: datetime,
    complaint_number: str = "CM-SLA-001",
) -> CmBatch1ComplaintORM:
    now = created_at
    row = CmBatch1ComplaintORM(
        id=uuid.uuid4(),
        complaint_number=complaint_number,
        customer_id="CUST-SLA",
        category="BILLING",
        channel="BRANCH",
        subject="SLA seed",
        description="SLA seed",
        priority="MEDIUM",
        status="REGISTERED",
        case_created=False,
        created_by="test",
        created_at=now,
        updated_at=now,
    )
    session.add(row)
    session.commit()
    session.refresh(row)
    return row


# --- Pure predicates (G4.4 / G3.2) ---


def test_threshold_instants_relative_to_due() -> None:
    due = datetime(2026, 8, 30, 12, 0, tzinfo=UTC)
    assert threshold_at(due_at=due, threshold="H7") == due - timedelta(days=7)
    assert threshold_at(due_at=due, threshold="H3") == due - timedelta(days=3)
    assert threshold_at(due_at=due, threshold="H1") == due - timedelta(days=1)
    assert threshold_at(due_at=due, threshold="BREACH") == due


def test_crossed_thresholds_h7_only() -> None:
    due = datetime(2026, 8, 30, 12, 0, tzinfo=UTC)
    now = due - timedelta(days=7)
    assert crossed_thresholds(due_at=due, now=now) == ["H7"]


def test_crossed_thresholds_all_at_breach() -> None:
    due = datetime(2026, 8, 30, 12, 0, tzinfo=UTC)
    assert crossed_thresholds(due_at=due, now=due) == ["H7", "H3", "H1", "BREACH"]


def test_classify_in_app_threshold_from_resolve() -> None:
    created = datetime(2026, 8, 1, 0, 0, tzinfo=UTC)
    sla = resolve_complaint_sla(
        created_at=created,
        closed_at=None,
        status="REGISTERED",
        target_days=30,
        now=created + timedelta(days=24),
    )
    assert sla is not None
    assert classify_in_app_threshold(sla) == "H7"

    breached = resolve_complaint_sla(
        created_at=created,
        closed_at=None,
        status="REGISTERED",
        target_days=30,
        now=created + timedelta(days=31),
    )
    assert breached is not None
    assert classify_in_app_threshold(breached) == "BREACH"


def test_idempotency_key_shape() -> None:
    cid = "11111111-1111-1111-1111-111111111111"
    assert sla_idempotency_key(complaint_id=cid, threshold="BREACH") == (
        f"cm-sla:{cid}:RESOLUTION:BREACH"
    )


# --- Sweep + drain (TC-030 + H-thresholds) ---


def test_sweep_emits_h7_h3_h1_breach_once(db_session: Session) -> None:
    created = datetime(2026, 7, 1, 10, 0, tzinfo=UTC)
    row = _seed_open(db_session, created_at=created)
    now = created + timedelta(days=30)

    svc = CmBatch1SlaSweepService(
        db_session,
        target_days=30,
        batch_limit=100,
    )
    first = svc.sweep(now=now)
    assert first.scanned == 1
    assert first.emitted == 4
    assert first.skipped_idempotent == 0

    outbox = OutboxRepository(db_session)
    keys = {
        sla_idempotency_key(complaint_id=str(row.id), threshold=t)
        for t in ("H7", "H3", "H1", "BREACH")
    }
    for key in keys:
        assert outbox.exists_idempotency_key(key)

    unpublished = outbox.list_unpublished()
    assert len(unpublished) == 1
    assert unpublished[0].event_id == "EVT-004"
    assert unpublished[0].event_name == "SLABreached"
    assert unpublished[0].payload["caseId"] == str(row.id)

    second = CmBatch1SlaSweepService(db_session, target_days=30).sweep(now=now)
    assert second.emitted == 0
    assert second.skipped_idempotent == 4


def test_sweep_h7_only_before_h3(db_session: Session) -> None:
    created = datetime(2026, 7, 1, 10, 0, tzinfo=UTC)
    row = _seed_open(db_session, created_at=created)
    now = created + timedelta(days=24)

    result = CmBatch1SlaSweepService(db_session, target_days=30).sweep(now=now)
    assert result.emitted == 1
    assert OutboxRepository(db_session).exists_idempotency_key(
        sla_idempotency_key(complaint_id=str(row.id), threshold="H7")
    )
    assert not OutboxRepository(db_session).exists_idempotency_key(
        sla_idempotency_key(complaint_id=str(row.id), threshold="H3")
    )


def test_drain_marks_evt004_published(db_session: Session) -> None:
    created = datetime(2026, 7, 1, 10, 0, tzinfo=UTC)
    _seed_open(db_session, created_at=created)
    now = created + timedelta(days=30)
    CmBatch1SlaSweepService(db_session, target_days=30).sweep(now=now)

    drain = CmBatch1OutboxDrainService(db_session).drain()
    assert drain.published == 1
    assert OutboxRepository(db_session).list_unpublished() == []

    second = CmBatch1OutboxDrainService(db_session).drain()
    assert second.published == 0


def test_heartbeat_marker_written(tmp_path: Path) -> None:
    marker = tmp_path / "cm-sla-sweep.last_ok"
    when = datetime(2026, 8, 23, 12, 0, tzinfo=UTC)
    write_heartbeat_marker(marker, when=when)
    assert marker.read_text(encoding="utf-8").strip() == "2026-08-23T12:00:00Z"


def test_cli_lock_held_exits_zero(tmp_path: Path) -> None:
    lock = tmp_path / "sweep.lock"
    marker = tmp_path / "sweep.last_ok"
    with exclusive_lock(lock):
        rc = hygiene_cli.cmd_sweep_sla_thresholds(
            lock_path=lock, marker_path=marker
        )
    assert rc == 0
    assert not marker.exists()


def test_cli_failure_exits_two(tmp_path: Path) -> None:
    lock = tmp_path / "sweep.lock"
    marker = tmp_path / "sweep.last_ok"

    class _Sess:
        def close(self) -> None:
            return None

    with (
        patch("app.db.session.get_session_factory", lambda: (lambda: _Sess())),
        patch(
            "app.core.config.get_settings",
            lambda: type(
                "Cfg",
                (),
                {
                    "complaint_resolution_target_days": 30,
                    "complaint_sla_warning_percent": 80,
                    "complaint_sla_sweep_batch_limit": 100,
                },
            )(),
        ),
        patch.object(
            CmBatch1SlaSweepService,
            "sweep",
            side_effect=RuntimeError("forced"),
        ),
    ):
        rc = hygiene_cli.cmd_sweep_sla_thresholds(
            lock_path=lock, marker_path=marker
        )
    assert rc == 2
    assert not marker.exists()


def test_side_effect_recorder_writes_outbox_h7(db_session: Session) -> None:
    created = datetime(2026, 7, 1, 10, 0, tzinfo=UTC)
    row = _seed_open(db_session, created_at=created)
    now = created + timedelta(days=24)
    CmBatch1SlaSweepService(
        db_session,
        side_effects=CmBatch1SideEffectRecorder(db_session),
        target_days=30,
    ).sweep(now=now)

    outbox_rows = list(db_session.scalars(select(CmBatch1OutboxORM)).all())
    assert len(outbox_rows) == 1
    assert outbox_rows[0].event_id == "NO-PUBLISH"
    assert "H7" in outbox_rows[0].idempotency_key
    assert str(row.id) in outbox_rows[0].idempotency_key
