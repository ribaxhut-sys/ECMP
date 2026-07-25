"""CAPABILITY-013 Dashboard application service (read-only aggregation)."""

from __future__ import annotations

from datetime import UTC, datetime

from app.core.errors import ValidationAppError
from app.modules.complaints.service import ComplaintService
from app.modules.dashboard.domain.dto import DashboardFilters, TrendPeriod
from app.modules.dashboard.providers.complaint_provider import (
    ComplaintDashboardProvider,
)
from app.modules.dashboard.providers.notification_provider import (
    NotificationDashboardProvider,
)
from app.modules.dashboard.providers.queue_provider import QueueDashboardProvider
from app.modules.dashboard.providers.sla_provider import SlaDashboardProvider
from app.modules.dashboard.schemas import (
    DashboardComplaintSummaryResponse,
    DashboardHeader,
    DashboardKpiResponse,
    DashboardNotificationsResponse,
    DashboardOverviewResponse,
    DashboardQueueResponse,
    DashboardRecentActivityItem,
    DashboardSlaResponse,
    DashboardSlaStage,
    DashboardSlaSummary,
    DashboardTrendItem,
    DashboardTrendsResponse,
)
from app.modules.kpi.service import KpiService
from app.modules.settings.registry import SettingsKey
from app.modules.settings.service import SettingsService
from app.modules.timelines.service import TimelineService

_DEFAULT_RECENT_LIMIT = 10
_SYSTEM_ACTOR = "SYSTEM"


def _ensure_utc(value: datetime) -> datetime:
    if value.tzinfo is None:
        return value.replace(tzinfo=UTC)
    return value.astimezone(UTC)


def _validate_filters(filters: DashboardFilters) -> DashboardFilters:
    date_from = (
        _ensure_utc(filters.date_from) if filters.date_from is not None else None
    )
    date_to = _ensure_utc(filters.date_to) if filters.date_to is not None else None
    if date_from is not None and date_to is not None and date_from > date_to:
        raise ValidationAppError(
            "dateFrom must be less than or equal to dateTo",
            details={
                "dateFrom": date_from.isoformat(),
                "dateTo": date_to.isoformat(),
            },
        )
    return DashboardFilters(
        branch_id=filters.branch_id,
        date_from=date_from,
        date_to=date_to,
    )


def _pct(numerator: int | float, denominator: int | float) -> float:
    if denominator <= 0:
        return 0.0
    return round((float(numerator) / float(denominator)) * 100.0, 2)


class DashboardService:
    """Orchestrates dashboard providers — no domain mutation, no writes."""

    def __init__(
        self,
        *,
        complaint_provider: ComplaintDashboardProvider,
        queue_provider: QueueDashboardProvider,
        sla_provider: SlaDashboardProvider,
        notification_provider: NotificationDashboardProvider,
        kpi_service: KpiService | None = None,
        timeline_service: TimelineService | None = None,
        complaint_service: ComplaintService | None = None,
        settings_service: SettingsService | None = None,
    ) -> None:
        self._complaints = complaint_provider
        self._queue = queue_provider
        self._sla = sla_provider
        self._notifications = notification_provider
        self._kpi = kpi_service
        self._timeline = timeline_service
        self._complaint_svc = complaint_service
        self._settings = settings_service

    def summary(
        self, filters: DashboardFilters | None = None
    ) -> DashboardComplaintSummaryResponse:
        f = _validate_filters(filters or DashboardFilters())
        m = self._complaints.summary(f)
        return DashboardComplaintSummaryResponse(
            totalComplaints=m.total_complaints,
            openComplaints=m.open_complaints,
            closedComplaints=m.closed_complaints,
            pendingComplaints=m.pending_complaints,
            overdueComplaints=m.overdue_complaints,
            escalatedComplaints=m.escalated_complaints,
            todayComplaints=m.today_complaints,
            thisMonthComplaints=m.this_month_complaints,
        )

    def queue(
        self, filters: DashboardFilters | None = None
    ) -> DashboardQueueResponse:
        f = _validate_filters(filters or DashboardFilters())
        m = self._queue.summary(f)
        return DashboardQueueResponse(
            waiting=m.waiting,
            serving=m.serving,
            completed=m.completed,
            cancelled=m.cancelled,
            averageWaitingTime=m.average_waiting_time,
        )

    def sla(
        self, filters: DashboardFilters | None = None
    ) -> DashboardSlaResponse:
        f = _validate_filters(filters or DashboardFilters())
        m = self._sla.summary(f)
        return DashboardSlaResponse(
            active=m.active,
            breached=m.breached,
            resolvedWithinSLA=m.resolved_within_sla,
            resolvedOutsideSLA=m.resolved_outside_sla,
            compliancePercentage=m.compliance_percentage,
        )

    def notifications(
        self, filters: DashboardFilters | None = None
    ) -> DashboardNotificationsResponse:
        f = _validate_filters(filters or DashboardFilters())
        m = self._notifications.summary(f)
        return DashboardNotificationsResponse(
            pending=m.pending,
            sent=m.sent,
            failed=m.failed,
            cancelled=m.cancelled,
        )

    def trends(
        self,
        *,
        period: TrendPeriod = TrendPeriod.SEVEN_D,
        filters: DashboardFilters | None = None,
    ) -> DashboardTrendsResponse:
        f = _validate_filters(filters or DashboardFilters())
        buckets = self._complaints.trends(f, period=period)
        return DashboardTrendsResponse(
            period=period.value,
            items=[
                DashboardTrendItem(date=b.day, count=b.count) for b in buckets
            ],
        )

    def kpi(
        self, filters: DashboardFilters | None = None
    ) -> DashboardKpiResponse:
        """Numeric KPI rates only (CAPABILITY-013)."""
        f = _validate_filters(filters or DashboardFilters())
        total, closed, avg_resolution = self._complaints.resolution_stats(f)
        escalated = self._complaints.escalation_count(f)
        sla = self._sla.summary(f)
        avg_wait = self._queue.average_waiting_time(f)
        return DashboardKpiResponse(
            complaintResolutionRate=_pct(closed, total),
            slaCompliance=sla.compliance_percentage,
            escalationRate=_pct(escalated, total),
            averageResolutionTime=round(avg_resolution, 2),
            averageQueueWaitingTime=round(avg_wait, 2),
        )

    def overview(self) -> DashboardOverviewResponse:
        """API-319 composition (KPI + timeline + complaint). No SQL in dashboard."""
        if (
            self._kpi is None
            or self._timeline is None
            or self._complaint_svc is None
            or self._settings is None
        ):
            raise RuntimeError(
                "Dashboard overview requires KPI/Timeline/Complaint/Settings wiring"
            )

        kpi = self._kpi.summary()
        recent_limit = self._settings.get_int(
            SettingsKey.DASHBOARD_RECENT_LIMIT,
            default=_DEFAULT_RECENT_LIMIT,
        )
        if recent_limit < 1:
            recent_limit = _DEFAULT_RECENT_LIMIT
        rows = self._timeline.list_recent(limit=recent_limit)

        recent: list[DashboardRecentActivityItem] = []
        for row in rows:
            complaint = self._complaint_svc.get(row.complaint_id)
            actor = row.__dict__.get("actor")
            actor_name = (
                getattr(actor, "full_name", None) if actor is not None else None
            )
            if not actor_name:
                meta = row.metadata_json if isinstance(row.metadata_json, dict) else None
                meta_actor = meta.get("actor") if meta else None
                actor_name = str(meta_actor) if meta_actor else _SYSTEM_ACTOR

            recent.append(
                DashboardRecentActivityItem(
                    eventType=str(row.event_type),
                    complaintNumber=complaint.complaint_number,
                    timestamp=row.event_at,
                    actor=actor_name,
                )
            )

        return DashboardOverviewResponse(
            header=DashboardHeader(
                totalComplaints=kpi.complaints.total,
                openComplaints=kpi.complaints.open,
                closedComplaints=kpi.complaints.closed,
            ),
            sla=DashboardSlaSummary(
                assignment=DashboardSlaStage(
                    completed=kpi.assignment.completed,
                    breached=kpi.assignment.breached,
                ),
                appointment=DashboardSlaStage(
                    completed=kpi.appointment.completed,
                    breached=kpi.appointment.breached,
                ),
                resolution=DashboardSlaStage(
                    completed=kpi.resolution.completed,
                    breached=kpi.resolution.breached,
                ),
                escalation=DashboardSlaStage(
                    completed=kpi.escalation.completed,
                    breached=kpi.escalation.breached,
                ),
                overall=DashboardSlaStage(
                    completed=kpi.overall.completed,
                    breached=kpi.overall.breached,
                ),
            ),
            recentActivity=recent,
        )
