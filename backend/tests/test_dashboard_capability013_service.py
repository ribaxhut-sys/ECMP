"""CAPABILITY-013 — DashboardService KPI + widget orchestration tests."""

from __future__ import annotations

import uuid
from datetime import UTC, date, datetime
from unittest.mock import MagicMock

import pytest

from app.core.errors import ValidationAppError
from app.modules.dashboard.domain.dto import (
    ComplaintSummaryMetrics,
    DashboardFilters,
    NotificationSummaryMetrics,
    QueueSummaryMetrics,
    SlaSummaryMetrics,
    TrendBucket,
    TrendPeriod,
)
from app.modules.dashboard.providers.cm_batch1_activity_provider import (
    CmBatch1ActivityDashboardProvider,
)
from app.modules.dashboard.providers.complaint_provider import (
    ComplaintDashboardProvider,
)
from app.modules.dashboard.providers.notification_provider import (
    NotificationDashboardProvider,
)
from app.modules.dashboard.providers.queue_provider import QueueDashboardProvider
from app.modules.dashboard.providers.sla_provider import SlaDashboardProvider
from app.modules.dashboard.schemas import DashboardAggregateKpiResponse
from app.modules.dashboard.service import DashboardService, _pct


def _svc(
    *,
    complaint: MagicMock | None = None,
    queue: MagicMock | None = None,
    sla: MagicMock | None = None,
    notification: MagicMock | None = None,
    activity: MagicMock | None = None,
) -> DashboardService:
    return DashboardService(
        complaint_provider=complaint or MagicMock(spec=ComplaintDashboardProvider),
        queue_provider=queue or MagicMock(spec=QueueDashboardProvider),
        sla_provider=sla or MagicMock(spec=SlaDashboardProvider),
        notification_provider=notification
        or MagicMock(spec=NotificationDashboardProvider),
        activity_provider=activity,
    )


def test_pct_helpers() -> None:
    assert _pct(0, 0) == 0.0
    assert _pct(1, 4) == 25.0
    assert _pct(2, 3) == 66.67


def test_summary_maps_provider_metrics() -> None:
    complaint = MagicMock(spec=ComplaintDashboardProvider)
    complaint.summary.return_value = ComplaintSummaryMetrics(
        total_complaints=10,
        open_complaints=7,
        closed_complaints=2,
        pending_complaints=1,
        overdue_complaints=3,
        escalated_complaints=1,
        today_complaints=2,
        this_month_complaints=8,
    )
    result = _svc(complaint=complaint).summary()
    assert result.total_complaints == 10
    assert result.overdue_complaints == 3
    assert result.this_month_complaints == 8
    complaint.summary.assert_called_once()


def test_queue_and_notifications_and_sla() -> None:
    queue = MagicMock(spec=QueueDashboardProvider)
    queue.summary.return_value = QueueSummaryMetrics(
        waiting=4, serving=1, completed=9, cancelled=2, average_waiting_time=120.5
    )
    sla = MagicMock(spec=SlaDashboardProvider)
    sla.summary.return_value = SlaSummaryMetrics(
        active=5,
        breached=2,
        resolved_within_sla=8,
        resolved_outside_sla=2,
        compliance_percentage=80.0,
    )
    notification = MagicMock(spec=NotificationDashboardProvider)
    notification.summary.return_value = NotificationSummaryMetrics(
        pending=3, sent=10, failed=1, cancelled=0
    )
    svc = _svc(queue=queue, sla=sla, notification=notification)
    assert svc.queue().waiting == 4
    assert svc.sla().compliance_percentage == 80.0
    assert svc.notifications().sent == 10


def test_trends_maps_buckets() -> None:
    complaint = MagicMock(spec=ComplaintDashboardProvider)
    complaint.trends.return_value = [
        TrendBucket(day=date(2026, 7, 24), count=2),
        TrendBucket(day=date(2026, 7, 25), count=5),
    ]
    result = _svc(complaint=complaint).trends(period=TrendPeriod.TODAY)
    assert result.period == "today"
    assert result.items[1].count == 5


def test_kpi_formulas() -> None:
    complaint = MagicMock(spec=ComplaintDashboardProvider)
    complaint.resolution_stats.return_value = (10, 4, 3600.0)
    complaint.escalation_count.return_value = 2
    sla = MagicMock(spec=SlaDashboardProvider)
    sla.summary.return_value = SlaSummaryMetrics(
        active=1,
        breached=1,
        resolved_within_sla=3,
        resolved_outside_sla=1,
        compliance_percentage=75.0,
    )
    queue = MagicMock(spec=QueueDashboardProvider)
    queue.average_waiting_time.return_value = 90.0

    result = _svc(complaint=complaint, sla=sla, queue=queue).kpi()
    assert result.complaint_resolution_rate == 40.0
    assert result.sla_compliance == 75.0
    assert result.escalation_rate == 20.0
    assert result.average_resolution_time == 3600.0
    assert result.average_queue_waiting_time == 90.0


def test_aggregate_kpis_forwards_period_window_normalized_to_utc() -> None:
    """/reports may narrow the Aggregate KPI to a period (same SoT, one window)."""
    activity = MagicMock(spec=CmBatch1ActivityDashboardProvider)
    activity.complaint_kpis.return_value = DashboardAggregateKpiResponse(
        total=3, open=2, closed=1, escalatePending=0
    )
    svc = _svc(activity=activity)

    result = svc.aggregate_kpis(
        date_from=datetime(2026, 8, 1),  # naive — service normalizes to UTC
        date_to=datetime(2026, 8, 31, tzinfo=UTC),
    )

    assert result.total == 3
    activity.complaint_kpis.assert_called_once()
    kwargs = activity.complaint_kpis.call_args.kwargs
    assert kwargs["branch_id"] is None
    assert kwargs["date_from"] == datetime(2026, 8, 1, tzinfo=UTC)
    assert kwargs["date_to"] == datetime(2026, 8, 31, tzinfo=UTC)
    # DEC-031: the SLA target rides along on the same call rather than costing
    # a second round-trip. Asserted as present, not pinned to 30 — the value is
    # configuration and a deployment may legitimately change it.
    assert kwargs["target_days"] >= 0
    assert 1 <= kwargs["warning_percent"] <= 99


def test_aggregate_kpis_invalid_period_raises() -> None:
    activity = MagicMock(spec=CmBatch1ActivityDashboardProvider)
    svc = _svc(activity=activity)
    with pytest.raises(ValidationAppError):
        svc.aggregate_kpis(
            date_from=datetime(2026, 8, 31, tzinfo=UTC),
            date_to=datetime(2026, 8, 1, tzinfo=UTC),
        )
    activity.complaint_kpis.assert_not_called()


def test_invalid_date_range_raises() -> None:
    svc = _svc()
    with pytest.raises(ValidationAppError):
        svc.summary(
            DashboardFilters(
                date_from=datetime(2026, 7, 25, tzinfo=UTC),
                date_to=datetime(2026, 7, 1, tzinfo=UTC),
            )
        )


def test_filters_forwarded_with_branch() -> None:
    complaint = MagicMock(spec=ComplaintDashboardProvider)
    complaint.summary.return_value = ComplaintSummaryMetrics(
        total_complaints=0,
        open_complaints=0,
        closed_complaints=0,
        pending_complaints=0,
        overdue_complaints=0,
        escalated_complaints=0,
        today_complaints=0,
        this_month_complaints=0,
    )
    branch = uuid.uuid4()
    _svc(complaint=complaint).summary(DashboardFilters(branch_id=branch))
    called: DashboardFilters = complaint.summary.call_args.args[0]
    assert called.branch_id == branch
