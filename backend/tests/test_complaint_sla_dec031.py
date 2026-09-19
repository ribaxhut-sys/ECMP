"""DEC-031 — 30 calendar-day resolution SLA.

Two layers:

* ``resolve_complaint_sla`` / ``apply_complaint_status`` — pure logic, no DB.
* the dashboard rollup — executed against real PostgreSQL, because the slices
  are SQL (``closed_at <= created_at + interval``) and a stubbed session would
  only prove that the mapping code runs, not that the query is right.
"""

from __future__ import annotations

import uuid
from collections.abc import Generator
from datetime import UTC, datetime, timedelta

import pytest
from sqlalchemy import create_engine, text
from sqlalchemy.orm import Session, sessionmaker

from app.core.config import get_settings
from app.modules.cm_batch1.models import CmBatch1ComplaintORM
from app.modules.cm_batch1.sla import (
    SLA_MET,
    SLA_MISSED,
    SLA_ON_TRACK,
    SLA_OVERDUE,
    apply_complaint_status,
    resolve_complaint_sla,
)
from app.modules.dashboard.providers.cm_batch1_activity_provider import (
    CmBatch1ActivityDashboardProvider,
)

TARGET = 30
START = datetime(2026, 1, 1, tzinfo=UTC)


def _sla(day: float, *, closed_on: float | None = None, target: int = TARGET):
    """SLA position observed ``day`` days after registration."""
    closed_at = START + timedelta(days=closed_on) if closed_on is not None else None
    return resolve_complaint_sla(
        created_at=START,
        closed_at=closed_at,
        status="CLOSED" if closed_on is not None else "IN_PROGRESS",
        target_days=target,
        now=START + timedelta(days=day),
    )


# --------------------------------------------------------------------------
# Pure computation
# --------------------------------------------------------------------------


def test_open_complaint_inside_target_is_on_track() -> None:
    sla = _sla(1)
    assert sla is not None
    assert sla.status == SLA_ON_TRACK
    assert sla.elapsed_days == 1
    assert sla.remaining_days == 29
    assert sla.overdue_days is None
    assert sla.is_warning is False


def test_warning_starts_at_eighty_percent_of_the_target() -> None:
    # 80% of 30 days is day 24 — the boundary itself already warns.
    assert _sla(23.9).is_warning is False  # type: ignore[union-attr]
    assert _sla(24).is_warning is True  # type: ignore[union-attr]
    # Still ON_TRACK: warning is an approaching flag, not a breach.
    assert _sla(24).status == SLA_ON_TRACK  # type: ignore[union-attr]


def test_due_day_itself_is_not_yet_overdue() -> None:
    """The promise is "within 30 days"; day 30 is still inside it."""
    on_due = _sla(30)
    assert on_due is not None
    assert on_due.status == SLA_ON_TRACK
    assert on_due.remaining_days == 0

    past_due = _sla(30.001)
    assert past_due is not None
    assert past_due.status == SLA_OVERDUE
    assert past_due.remaining_days is None
    # A breach stops being a "warning" — it is no longer approaching.
    assert past_due.is_warning is False


def test_overdue_counts_days_past_the_target() -> None:
    sla = _sla(45)
    assert sla is not None
    assert sla.status == SLA_OVERDUE
    assert sla.overdue_days == 15
    assert sla.needs_attention is True


def test_closed_within_target_is_met_and_stops_the_clock() -> None:
    # Observed long after closure — the verdict must not drift with "now".
    sla = _sla(999, closed_on=10)
    assert sla is not None
    assert sla.status == SLA_MET
    assert sla.elapsed_days == 10
    assert sla.overdue_days is None
    assert sla.needs_attention is False


def test_closed_after_target_is_missed() -> None:
    sla = _sla(999, closed_on=45)
    assert sla is not None
    assert sla.status == SLA_MISSED
    assert sla.elapsed_days == 45
    assert sla.overdue_days == 15


def test_escalation_does_not_reset_the_clock() -> None:
    """DEC-031 §2.4 — Pusat continues the work, it does not restart it.

    Nothing in the computation reads disposition or owning unit, so an
    escalated complaint is measured from its original registration. This test
    pins that as intent rather than accident.
    """
    sla = resolve_complaint_sla(
        created_at=START,
        closed_at=None,
        status="IN_PROGRESS",
        target_days=TARGET,
        now=START + timedelta(days=31),
    )
    assert sla is not None and sla.status == SLA_OVERDUE


def test_measurement_off_when_target_is_zero() -> None:
    assert _sla(999, target=0) is None


def test_closed_without_a_stamp_is_unknown_not_guessed() -> None:
    """An unstamped closure must not be scored — in either direction."""
    assert (
        resolve_complaint_sla(
            created_at=START,
            closed_at=None,
            status="CLOSED",
            target_days=TARGET,
            now=START + timedelta(days=99),
        )
        is None
    )


def test_closure_stamped_before_registration_does_not_go_negative() -> None:
    sla = resolve_complaint_sla(
        created_at=START,
        closed_at=START - timedelta(days=3),
        status="CLOSED",
        target_days=TARGET,
    )
    assert sla is not None
    assert sla.elapsed_days == 0
    assert sla.status == SLA_MET


# --------------------------------------------------------------------------
# closed_at / status stay in lockstep
# --------------------------------------------------------------------------


class _Row:
    def __init__(self, status: str = "REGISTERED") -> None:
        self.status = status
        self.closed_at: datetime | None = None


def test_closing_stamps_and_reopening_clears() -> None:
    row = _Row()
    apply_complaint_status(row, "CLOSED", now=START)
    assert row.closed_at == START

    apply_complaint_status(row, "IN_PROGRESS")
    assert row.closed_at is None, "reopen must clear the superseded closure"


def test_reclosing_keeps_the_first_stamp() -> None:
    """Closing an already-closed complaint is a no-op, not a clock reset."""
    row = _Row()
    apply_complaint_status(row, "CLOSED", now=START)
    apply_complaint_status(row, "CLOSED", now=START + timedelta(days=5))
    assert row.closed_at == START


def test_reopen_then_close_measures_the_new_cycle() -> None:
    row = _Row()
    apply_complaint_status(row, "CLOSED", now=START)
    apply_complaint_status(row, "IN_PROGRESS")
    later = START + timedelta(days=40)
    apply_complaint_status(row, "CLOSED", now=later)
    assert row.closed_at == later


# --------------------------------------------------------------------------
# Dashboard rollup — real SQL
# --------------------------------------------------------------------------


def _postgres_available() -> bool:
    try:
        eng = create_engine(
            get_settings().database_url,
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


requires_postgres = pytest.mark.skipif(
    not _postgres_available(),
    reason="SLA rollup is SQL — needs PostgreSQL interval arithmetic",
)


@pytest.fixture()
def db_session() -> Generator[Session, None, None]:
    eng = create_engine(get_settings().database_url, pool_pre_ping=True, future=True)
    factory = sessionmaker(bind=eng, autoflush=False, autocommit=False, future=True)
    session = factory()
    try:
        yield session
    finally:
        session.rollback()
        session.close()
        eng.dispose()


def _seed(
    session: Session,
    unit: str,
    *,
    age_days: float,
    closed_after: float | None = None,
    stamp_closure: bool = True,
    now: datetime | None = None,
) -> None:
    """Seed one complaint aged ``age_days``.

    Pass ``now`` (and the same instant to the provider) whenever an assertion
    depends on a whole-day boundary: seeding and reading otherwise happen
    microseconds apart, and "4 days remaining" floors to 3.
    """
    now = now or datetime.now(UTC)
    created = now - timedelta(days=age_days)
    closed = (
        created + timedelta(days=closed_after) if closed_after is not None else None
    )
    session.add(
        CmBatch1ComplaintORM(
            id=uuid.uuid4(),
            complaint_number=f"SLA-{uuid.uuid4().hex[:12]}",
            customer_id="CUST-SLA",
            category="BILLING",
            channel="WALK_IN",
            subject="SLA fixture",
            description="SLA fixture",
            priority="MEDIUM",
            status="CLOSED" if closed_after is not None else "IN_PROGRESS",
            closed_at=closed if stamp_closure else None,
            owning_unit_id=unit,
            created_at=created,
            updated_at=now,
        )
    )


@requires_postgres
def test_dashboard_rollup_partitions_every_complaint(db_session: Session) -> None:
    # Own unit key per run so the assertions are independent of lab data.
    unit = f"SLA-{uuid.uuid4().hex[:8]}"
    _seed(db_session, unit, age_days=1)  # on track
    _seed(db_session, unit, age_days=26)  # warning (past day 24)
    _seed(db_session, unit, age_days=40)  # overdue
    _seed(db_session, unit, age_days=50, closed_after=10)  # met
    _seed(db_session, unit, age_days=60, closed_after=45)  # missed
    _seed(db_session, unit, age_days=70, closed_after=5, stamp_closure=False)
    db_session.flush()

    provider = CmBatch1ActivityDashboardProvider(db_session)
    provider._owning_unit_for_branch = lambda _branch_id: unit  # type: ignore[assignment]
    kpis = provider.complaint_kpis(branch_id=uuid.uuid4(), target_days=TARGET)

    assert kpis.total == 6
    assert kpis.sla is not None
    assert kpis.sla.on_track == 1
    assert kpis.sla.warning == 1
    assert kpis.sla.overdue == 1
    assert kpis.sla.met == 1
    assert kpis.sla.missed == 1
    assert kpis.sla.unknown == 1
    # 1 met of 2 settled — the unstamped row is excluded, not counted as met.
    assert kpis.sla.compliance_percentage == 50.0
    assert (
        kpis.sla.on_track
        + kpis.sla.warning
        + kpis.sla.overdue
        + kpis.sla.met
        + kpis.sla.missed
        + kpis.sla.unknown
        == kpis.total
    )


@requires_postgres
def test_dashboard_rollup_judges_each_row_against_its_own_registration(
    db_session: Session,
) -> None:
    """Interval arithmetic is per row, not against a single shared cutoff.

    Both complaints below took 10 days to resolve, but were registered months
    apart. A cutoff-based query would score the older one as missed.
    """
    unit = f"SLA-{uuid.uuid4().hex[:8]}"
    _seed(db_session, unit, age_days=400, closed_after=10)
    _seed(db_session, unit, age_days=12, closed_after=10)
    db_session.flush()

    provider = CmBatch1ActivityDashboardProvider(db_session)
    provider._owning_unit_for_branch = lambda _branch_id: unit  # type: ignore[assignment]
    kpis = provider.complaint_kpis(branch_id=uuid.uuid4(), target_days=TARGET)

    assert kpis.sla is not None
    assert kpis.sla.met == 2
    assert kpis.sla.missed == 0


@requires_postgres
def test_sla_alerts_lists_worst_first_and_counts_the_whole_scope(
    db_session: Session,
) -> None:
    unit = f"SLA-{uuid.uuid4().hex[:8]}"
    now = datetime.now(UTC)
    _seed(db_session, unit, age_days=1, now=now)  # healthy — must not appear
    _seed(db_session, unit, age_days=26, now=now)  # warning
    _seed(db_session, unit, age_days=35, now=now)  # overdue
    _seed(db_session, unit, age_days=90, now=now)  # overdue, worst
    _seed(db_session, unit, age_days=99, closed_after=1, now=now)  # closed
    db_session.flush()

    provider = CmBatch1ActivityDashboardProvider(db_session)
    provider._owning_unit_for_branch = lambda _branch_id: unit  # type: ignore[assignment]
    alerts = provider.sla_alerts(
        branch_id=uuid.uuid4(), target_days=TARGET, now=now
    )

    assert alerts.overdue_count == 2
    assert alerts.warning_count == 1
    assert [item.is_overdue for item in alerts.items] == [True, True, False]
    # Oldest first — the 90-day complaint outranks the 35-day one.
    assert alerts.items[0].overdue_days == 60
    assert alerts.items[1].overdue_days == 5
    assert alerts.items[2].overdue_days is None
    assert alerts.items[2].remaining_days == 4


@requires_postgres
def test_sla_alert_counts_survive_a_truncated_list(db_session: Session) -> None:
    """A badge must not under-report because the feed was capped."""
    unit = f"SLA-{uuid.uuid4().hex[:8]}"
    for age in (40, 50, 60, 70, 80):
        _seed(db_session, unit, age_days=age)
    db_session.flush()

    provider = CmBatch1ActivityDashboardProvider(db_session)
    provider._owning_unit_for_branch = lambda _branch_id: unit  # type: ignore[assignment]
    alerts = provider.sla_alerts(branch_id=uuid.uuid4(), target_days=TARGET, limit=2)

    assert len(alerts.items) == 2
    assert alerts.overdue_count == 5


@requires_postgres
def test_sla_alerts_empty_when_measurement_is_off(db_session: Session) -> None:
    unit = f"SLA-{uuid.uuid4().hex[:8]}"
    _seed(db_session, unit, age_days=90)
    db_session.flush()

    provider = CmBatch1ActivityDashboardProvider(db_session)
    provider._owning_unit_for_branch = lambda _branch_id: unit  # type: ignore[assignment]
    alerts = provider.sla_alerts(branch_id=uuid.uuid4(), target_days=0)

    assert alerts.items == []
    assert alerts.overdue_count == 0


@requires_postgres
def test_dashboard_rollup_omitted_when_measurement_is_off(
    db_session: Session,
) -> None:
    unit = f"SLA-{uuid.uuid4().hex[:8]}"
    _seed(db_session, unit, age_days=40)
    db_session.flush()

    provider = CmBatch1ActivityDashboardProvider(db_session)
    provider._owning_unit_for_branch = lambda _branch_id: unit  # type: ignore[assignment]
    kpis = provider.complaint_kpis(branch_id=uuid.uuid4(), target_days=0)

    assert kpis.total == 1
    assert kpis.sla is None
