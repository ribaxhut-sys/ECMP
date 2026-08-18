"""One vocabulary for OPEN / ESCALATED across list, KPI, dashboard, report.

Pins DEC-025 §3.3 read semantics so the call sites cannot drift apart again:
before this, ``escalated`` meant 2 dispositions on the dashboard, 6 on the
SQL list filter, 4 on the in-memory Users-directory counter, and 1 (mismapped)
in the report donut.
"""

from __future__ import annotations

import uuid
from collections.abc import Generator
from datetime import UTC, datetime

import pytest
from sqlalchemy import create_engine, delete
from sqlalchemy.orm import Session, sessionmaker

from app.core.config import get_settings
from app.modules.cm_batch1.entities import ComplaintAggregate
from app.modules.cm_batch1.models import CmBatch1ComplaintORM
from app.modules.cm_batch1.predicates import (
    ESCALATION_ACTIVE,
    ESCALATION_FAMILY,
    in_escalation_family,
    is_escalation_active,
    is_open,
)
from app.modules.cm_batch1.repository import CmBatch1Repository
from app.modules.cm_batch1.store import Batch1Store
from app.modules.dashboard.domain.dto import DashboardFilters
from app.modules.dashboard.providers.cm_batch1_activity_provider import (
    CmBatch1ActivityDashboardProvider,
)
from app.modules.dashboard.providers.complaint_provider import (
    ComplaintDashboardProvider,
)
from app.modules.kpi.repository import KpiRepository
from app.modules.reports.repository import ReportRepository


def test_open_is_everything_not_closed() -> None:
    assert is_open("REGISTERED")
    assert is_open("IN_PROGRESS")
    assert not is_open("CLOSED")
    # An out-of-set stored value stays visible as open — ``_aggregate_status``
    # exposes it as REGISTERED, so it must not vanish from both buckets.
    assert is_open("LEGACY_UNKNOWN")
    assert is_open(None)


def test_active_escalation_is_a_subset_of_the_family() -> None:
    assert set(ESCALATION_ACTIVE) < set(ESCALATION_FAMILY)
    assert is_escalation_active("HQ_SCHEDULED")
    assert not is_escalation_active("ESCALATE_REJECTED")
    assert not is_escalation_active(None)
    # Rejected/cancelled left the escalation path but still belong to the
    # "ever escalated" drill-down.
    assert in_escalation_family("ESCALATE_REJECTED")
    assert in_escalation_family("ESCALATE_CANCELLED")
    assert not in_escalation_family("BRANCH_CLOSED")


def test_store_work_stats_matches_sql_family_not_the_old_4value_set() -> None:
    """Batch1Store (Mode A in-memory path) must count the same family as the
    SQL repository (repository.py:work_stats_for_user) and the list
    drill-down — HQ_SCHEDULED and RETURNED_TO_BRANCH used to be silently
    dropped here even though they count on the SQL path.
    """
    store = Batch1Store()
    actor = "store-parity-actor"
    dispositions = [
        "ESCALATE_PENDING_APPROVAL",
        "ESCALATE_APPROVED",
        "ESCALATE_REJECTED",
        "ESCALATE_CANCELLED",
        "RETURNED_TO_BRANCH",
        "HQ_SCHEDULED",
        "BRANCH_CLOSED",  # not in the family — must not be counted
        None,
    ]
    for i, disp in enumerate(dispositions):
        row = ComplaintAggregate(
            complaint_id=str(uuid.uuid4()),
            complaint_number=f"STORE-PARITY-{i}",
            customer_id="CUST-STORE",
            category="BILLING",
            channel="WEB",
            subject=f"store parity {disp}",
            description="store parity seed",
            priority="HIGH",
            status="REGISTERED",
            intake_disposition=disp,
            created_by=actor,
        )
        store._complaints[row.complaint_id] = row  # noqa: SLF001 — unit test seed

    stats = store.work_stats_for_user(actor)
    assert stats["escalation_requested_count"] == len(ESCALATION_FAMILY)


def _postgres_available() -> bool:
    from sqlalchemy import text

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


_PG = pytest.mark.skipif(
    not _postgres_available(),
    reason="PostgreSQL not available for predicate integration tests",
)

_ACTOR = f"predicate-actor-{uuid.uuid4().hex[:8]}"

# (status, intake_disposition) — one row per bucket the predicates must sort.
_SEED: tuple[tuple[str, str | None], ...] = (
    ("CLOSED", "BRANCH_CLOSED"),
    ("IN_PROGRESS", None),
    # Production shape: an HQ visit binds a Case, so the row is IN_PROGRESS
    # while still travelling the escalation path.
    ("IN_PROGRESS", "HQ_SCHEDULED"),
    ("REGISTERED", "ESCALATE_PENDING_APPROVAL"),
    ("REGISTERED", "HQ_SCHEDULED"),
    ("REGISTERED", "ESCALATE_REJECTED"),
    ("REGISTERED", None),
    ("LEGACY_UNKNOWN", None),
)


@pytest.fixture()
def seeded() -> Generator[Session, None, None]:
    settings = get_settings()
    eng = create_engine(settings.database_url, pool_pre_ping=True, future=True)
    SessionLocal = sessionmaker(
        bind=eng, autoflush=False, autocommit=False, future=True
    )
    session = SessionLocal()
    now = datetime.now(UTC)
    for status, disposition in _SEED:
        session.add(
            CmBatch1ComplaintORM(
                id=uuid.uuid4(),
                complaint_number=f"PRED-2608-{uuid.uuid4().hex[:6].upper()}",
                customer_id="CUST-PRED",
                category="BILLING",
                channel="WEB",
                subject=f"predicate {status} {disposition}",
                description="predicate seed",
                priority="HIGH",
                status=status,
                intake_disposition=disposition,
                case_created=False,
                created_by=_ACTOR,
                created_at=now,
                updated_at=now,
            )
        )
    session.commit()
    try:
        yield session
    finally:
        session.execute(
            delete(CmBatch1ComplaintORM).where(
                CmBatch1ComplaintORM.created_by == _ACTOR
            )
        )
        session.commit()
        session.close()
        eng.dispose()


def _delta(before: dict[str, int], after: dict[str, int]) -> dict[str, int]:
    keys = set(before) | set(after)
    return {k: after.get(k, 0) - before.get(k, 0) for k in keys}


@_PG
def test_kpi_open_plus_closed_equals_total(seeded: Session) -> None:
    """No row may fall out of both buckets, whatever the stored status."""
    total, open_count, closed = KpiRepository(seeded).count_complaints()
    assert open_count + closed == total
    assert closed >= 1


@_PG
def test_dashboard_escalated_counts_the_active_path_only(seeded: Session) -> None:
    provider = ComplaintDashboardProvider(seeded)
    repo = CmBatch1Repository(seeded)
    _, family_total = repo.list_complaints(
        created_by=_ACTOR, intake_disposition="ESCALATED"
    )
    assert family_total == 4  # PENDING_APPROVAL + 2x HQ_SCHEDULED + REJECTED

    with_seed = provider.escalation_count(DashboardFilters())
    seeded.execute(
        delete(CmBatch1ComplaintORM).where(CmBatch1ComplaintORM.created_by == _ACTOR)
    )
    seeded.commit()
    baseline = provider.escalation_count(DashboardFilters())
    # Both HQ_SCHEDULED rows count (still at HQ); the rejected row does not.
    assert with_seed - baseline == 3


@_PG
def test_users_directory_counter_matches_its_drill_down(seeded: Session) -> None:
    repo = CmBatch1Repository(seeded)
    stats = repo.work_stats_for_user(_ACTOR)
    _, listed = repo.list_complaints(
        created_by=_ACTOR, intake_disposition="ESCALATED"
    )
    assert stats["escalation_requested_count"] == listed


@_PG
def test_list_open_filter_keeps_out_of_set_status(seeded: Session) -> None:
    repo = CmBatch1Repository(seeded)
    _, open_total = repo.list_complaints(created_by=_ACTOR, status="OPEN")
    _, closed_total = repo.list_complaints(created_by=_ACTOR, status="CLOSED")
    assert open_total == len(_SEED) - 1
    assert closed_total == 1


@_PG
def test_report_by_status_emits_aggregate_lifecycle_not_foundation_labels(
    seeded: Session,
) -> None:
    repo = ReportRepository(seeded)
    counts = dict(repo.count_by_status())
    seeded.execute(
        delete(CmBatch1ComplaintORM).where(CmBatch1ComplaintORM.created_by == _ACTOR)
    )
    seeded.commit()
    baseline = dict(repo.count_by_status())
    delta = _delta(baseline, counts)
    assert delta["CLOSED"] == 1
    # Status decides: IN_PROGRESS stays IN_PROGRESS even when HQ_SCHEDULED.
    assert delta["IN_PROGRESS"] == 2
    # REGISTERED + unknown open values; dispositions are not remapped to ESCALATED/NEW.
    assert delta["REGISTERED"] == 5
    assert delta.get("NEW", 0) == 0
    assert delta.get("ESCALATED", 0) == 0
    assert delta.get("ASSIGNED", 0) == 0


@_PG
def test_aggregate_kpi_slices_partition_and_count_hq_scheduled(
    seeded: Session,
) -> None:
    """The donut may not lose an escalation: HQ_SCHEDULED has its own slice.

    Before ``escalate_scheduled`` these rows fell into ``waiting_assignment``
    (REGISTERED) or ``in_progress`` (case bound), so /reports showed
    "0 dieskalasi" while every row sat on the escalation path.
    """
    provider = CmBatch1ActivityDashboardProvider(seeded)
    after = provider.complaint_kpis()
    seeded.execute(
        delete(CmBatch1ComplaintORM).where(CmBatch1ComplaintORM.created_by == _ACTOR)
    )
    seeded.commit()
    before = provider.complaint_kpis()

    assert after.escalate_scheduled - before.escalate_scheduled == 2
    assert after.escalate_pending - before.escalate_pending == 1
    # The plain IN_PROGRESS row only; the HQ-scheduled one moved to its slice.
    assert after.in_progress - before.in_progress == 1
    # REGISTERED+REJECTED, REGISTERED+None, and the out-of-set status row —
    # exposed as REGISTERED by the aggregate, so it needs a slice too.
    assert after.waiting_assignment - before.waiting_assignment == 3
    seed_total = after.total - before.total
    seed_sliced = (
        (after.waiting_assignment - before.waiting_assignment)
        + (after.escalate_pending - before.escalate_pending)
        + (after.escalate_approved - before.escalate_approved)
        + (after.escalate_scheduled - before.escalate_scheduled)
        + (after.in_progress - before.in_progress)
        + (after.closed - before.closed)
    )
    assert seed_total == len(_SEED)
    # No row falls out of the donut, whatever the stored status.
    assert seed_sliced == seed_total
    for kpis in (after, before):
        assert (
            kpis.waiting_assignment
            + kpis.escalate_pending
            + kpis.escalate_approved
            + kpis.escalate_scheduled
            + kpis.in_progress
            + kpis.closed
            == kpis.total
        )
