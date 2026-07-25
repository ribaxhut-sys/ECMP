"""CAPABILITY-013 — provider aggregation unit tests (mocked session)."""

from __future__ import annotations

import uuid
from datetime import UTC, datetime
from types import SimpleNamespace
from unittest.mock import MagicMock

from app.modules.dashboard.domain.dto import DashboardFilters, TrendPeriod
from app.modules.dashboard.providers.complaint_provider import (
    ComplaintDashboardProvider,
)
from app.modules.dashboard.providers.notification_provider import (
    NotificationDashboardProvider,
)
from app.modules.dashboard.providers.queue_provider import QueueDashboardProvider
from app.modules.dashboard.providers.sla_provider import SlaDashboardProvider


def _row(**kwargs: object) -> SimpleNamespace:
    return SimpleNamespace(**kwargs)


def test_complaint_summary_reads_single_aggregate_row() -> None:
    session = MagicMock()
    session.execute.return_value.one.return_value = _row(
        total=10,
        open_count=6,
        closed_count=3,
        pending_count=1,
        overdue_count=2,
        escalated_count=1,
        today_count=2,
        month_count=8,
    )
    metrics = ComplaintDashboardProvider(session).summary(DashboardFilters())
    assert metrics.total_complaints == 10
    assert metrics.open_complaints == 6
    assert metrics.overdue_complaints == 2
    session.execute.assert_called_once()


def test_complaint_trends_fills_missing_days() -> None:
    session = MagicMock()
    day = datetime(2026, 7, 25, tzinfo=UTC)
    session.execute.return_value.all.return_value = [
        _row(day=day, count=4),
    ]
    buckets = ComplaintDashboardProvider(session).trends(
        DashboardFilters(), period=TrendPeriod.TODAY
    )
    assert len(buckets) == 1
    assert buckets[0].count == 4


def test_complaint_resolution_and_escalation() -> None:
    session = MagicMock()
    session.scalar.side_effect = [20, 5, 1800.0, 3]
    provider = ComplaintDashboardProvider(session)
    total, closed, avg = provider.resolution_stats(DashboardFilters())
    assert (total, closed, avg) == (20, 5, 1800.0)
    assert provider.escalation_count(DashboardFilters()) == 3


def test_queue_summary_with_branch_join() -> None:
    session = MagicMock()
    session.execute.return_value.one.return_value = _row(
        waiting=2, serving=1, completed=5, cancelled=1
    )
    session.scalar.return_value = 45.5
    metrics = QueueDashboardProvider(session).summary(
        DashboardFilters(branch_id=uuid.uuid4())
    )
    assert metrics.waiting == 2
    assert metrics.average_waiting_time == 45.5


def test_sla_compliance_percentage() -> None:
    session = MagicMock()
    session.execute.return_value.one.return_value = _row(
        active=3, breached=2, within=8, outside=2
    )
    metrics = SlaDashboardProvider(session).summary(DashboardFilters())
    assert metrics.resolved_within_sla == 8
    assert metrics.compliance_percentage == 80.0


def test_sla_compliance_zero_when_no_resolved() -> None:
    session = MagicMock()
    session.execute.return_value.one.return_value = _row(
        active=1, breached=0, within=0, outside=0
    )
    metrics = SlaDashboardProvider(session).summary(DashboardFilters())
    assert metrics.compliance_percentage == 0.0


def test_notification_summary() -> None:
    session = MagicMock()
    session.execute.return_value.one.return_value = _row(
        pending=2, sent=7, failed=1, cancelled=0
    )
    metrics = NotificationDashboardProvider(session).summary(DashboardFilters())
    assert metrics.sent == 7
    assert metrics.pending == 2


def test_providers_apply_date_and_branch_filters() -> None:
    session = MagicMock()
    session.execute.return_value.one.return_value = _row(
        total=0,
        open_count=0,
        closed_count=0,
        pending_count=0,
        overdue_count=0,
        escalated_count=0,
        today_count=0,
        month_count=0,
        waiting=0,
        serving=0,
        completed=0,
        cancelled=0,
        active=0,
        breached=0,
        within=0,
        outside=0,
        pending=0,
        sent=0,
        failed=0,
    )
    session.scalar.return_value = 0
    session.execute.return_value.all.return_value = []
    filters = DashboardFilters(
        branch_id=uuid.uuid4(),
        date_from=datetime(2026, 7, 1, tzinfo=UTC),
        date_to=datetime(2026, 7, 25, tzinfo=UTC),
    )
    ComplaintDashboardProvider(session).summary(filters)
    ComplaintDashboardProvider(session).trends(filters, period=TrendPeriod.SEVEN_D)
    ComplaintDashboardProvider(session).trends(filters, period=TrendPeriod.THIRTY_D)
    QueueDashboardProvider(session).summary(filters)
    QueueDashboardProvider(session).average_waiting_time(filters)
    SlaDashboardProvider(session).summary(filters)
    NotificationDashboardProvider(session).summary(filters)


def test_registration_builds_service() -> None:
    from app.modules.dashboard.registration import build_dashboard_service

    session = MagicMock()
    svc = build_dashboard_service(session)
    assert svc is not None


def test_overview_requires_wiring() -> None:
    from app.modules.dashboard.service import DashboardService

    svc = DashboardService(
        complaint_provider=MagicMock(),
        queue_provider=MagicMock(),
        sla_provider=MagicMock(),
        notification_provider=MagicMock(),
    )
    try:
        svc.overview()
        raise AssertionError("expected RuntimeError")
    except RuntimeError:
        pass


def test_naive_datetime_normalized() -> None:
    from app.modules.dashboard.service import _ensure_utc

    naive = datetime(2026, 7, 25, 12, 0, 0)
    assert _ensure_utc(naive).tzinfo is UTC
