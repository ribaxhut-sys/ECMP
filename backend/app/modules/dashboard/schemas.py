"""CAPABILITY-013 Dashboard HTTP / OpenAPI schemas (read-only)."""

from __future__ import annotations

from datetime import date, datetime

from pydantic import BaseModel, ConfigDict, Field


class DashboardComplaintSummaryResponse(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    total_complaints: int = Field(alias="totalComplaints")
    open_complaints: int = Field(alias="openComplaints")
    closed_complaints: int = Field(alias="closedComplaints")
    pending_complaints: int = Field(alias="pendingComplaints")
    overdue_complaints: int = Field(alias="overdueComplaints")
    escalated_complaints: int = Field(alias="escalatedComplaints")
    today_complaints: int = Field(alias="todayComplaints")
    this_month_complaints: int = Field(alias="thisMonthComplaints")


class DashboardQueueResponse(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    waiting: int
    serving: int
    completed: int
    cancelled: int
    average_waiting_time: float = Field(alias="averageWaitingTime")


class DashboardSlaResponse(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    active: int
    breached: int
    resolved_within_sla: int = Field(alias="resolvedWithinSLA")
    resolved_outside_sla: int = Field(alias="resolvedOutsideSLA")
    compliance_percentage: float = Field(alias="compliancePercentage")


class DashboardNotificationsResponse(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    pending: int
    sent: int
    failed: int
    cancelled: int


class DashboardTrendItem(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    date: date
    count: int


class DashboardTrendsResponse(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    period: str
    items: list[DashboardTrendItem]


class DashboardKpiResponse(BaseModel):
    """Numeric KPI rates only — no chart payloads."""

    model_config = ConfigDict(populate_by_name=True)

    complaint_resolution_rate: float = Field(alias="complaintResolutionRate")
    sla_compliance: float = Field(alias="slaCompliance")
    escalation_rate: float = Field(alias="escalationRate")
    average_resolution_time: float = Field(alias="averageResolutionTime")
    average_queue_waiting_time: float = Field(alias="averageQueueWaitingTime")


# --- API-319 composition (preserved at /dashboard/overview) ---


class DashboardHeader(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    total_complaints: int = Field(default=0, alias="totalComplaints")
    open_complaints: int = Field(default=0, alias="openComplaints")
    closed_complaints: int = Field(default=0, alias="closedComplaints")


class DashboardSlaStage(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    completed: int = 0
    breached: int = 0


class DashboardSlaSummary(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    assignment: DashboardSlaStage
    appointment: DashboardSlaStage
    resolution: DashboardSlaStage
    escalation: DashboardSlaStage
    overall: DashboardSlaStage


class DashboardRecentActivityItem(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    event_type: str = Field(alias="eventType")
    complaint_number: str = Field(alias="complaintNumber")
    timestamp: datetime
    actor: str
    case_number: str | None = Field(default=None, alias="caseNumber")


class DashboardResolutionSla(BaseModel):
    """Resolution-SLA rollup for the dashboard (DEC-031).

    Replaces the five-stage CAP-006 shape (``DashboardSlaSummary``) on this
    payload: Mode A has no assignment/appointment/escalation clocks, so those
    stages could only ever report zero. These six counts partition every
    complaint in scope — ``onTrack + warning + overdue + met + missed +
    unknown == total``.
    """

    model_config = ConfigDict(populate_by_name=True)

    target_days: int = Field(alias="targetDays")
    #: Open, inside the target, before the warning threshold.
    on_track: int = Field(default=0, alias="onTrack")
    #: Open, past the warning threshold, target not yet passed.
    warning: int = 0
    #: Open, target already passed.
    overdue: int = 0
    #: Closed within the target.
    met: int = 0
    #: Closed after the target had passed.
    missed: int = 0
    #: Closed without a stamped closure time — cannot be judged either way.
    unknown: int = 0
    #: ``met / (met + missed)`` as a percentage; ``None`` when nothing settled.
    compliance_percentage: float | None = Field(
        default=None, alias="compliancePercentage"
    )


class ComplaintSlaAlertItem(BaseModel):
    """One complaint that needs attention on SLA grounds (DEC-031).

    The in-app substitute for the proactive notification CAP-005/CAP-006 would
    send. Fase 1 was read-time only; Fase 2 (FR-030) also records durable
    threshold events via the hourly sweep — this feed still computes at read
    time so the next visit surfaces H-7 / H-3 / H-1 / BREACH (C-6).
    """

    model_config = ConfigDict(populate_by_name=True)

    complaint_id: str = Field(alias="complaintId")
    complaint_number: str = Field(alias="complaintNumber")
    subject: str | None = None
    owning_unit_id: str | None = Field(default=None, alias="owningUnitId")
    priority: str | None = None
    due_at: datetime = Field(alias="dueAt")
    elapsed_days: int = Field(alias="elapsedDays")
    remaining_days: int | None = Field(default=None, alias="remainingDays")
    overdue_days: int | None = Field(default=None, alias="overdueDays")
    #: ``True`` = past the target. ``False`` = approaching it.
    is_overdue: bool = Field(alias="isOverdue")
    #: C-6 label when inside H-7 / H-3 / H-1 / BREACH; else ``None`` (e.g. 80% zone).
    threshold: str | None = None


class ComplaintSlaAlertsResponse(BaseModel):
    """Alert feed plus the totals, so a badge can show a count without
    re-counting a truncated list."""

    model_config = ConfigDict(populate_by_name=True)

    target_days: int = Field(alias="targetDays")
    overdue_count: int = Field(default=0, alias="overdueCount")
    warning_count: int = Field(default=0, alias="warningCount")
    items: list[ComplaintSlaAlertItem] = Field(default_factory=list)


class DashboardAggregateKpiResponse(BaseModel):
    """DEC-020 Aggregate complaint KPI counts (CM Batch-1), branch-lockable.

    Gated by ``dashboard:read`` so branch Manager (BC-8.4) can see own-branch
    numbers without receiving operational ``complaints:read`` / list access.
    Branch scope uses Aggregate ``owningUnitId`` (= ``Branch.code``), aligned
    with list visibility — not the creating officer's membership.
    """

    model_config = ConfigDict(populate_by_name=True)

    total: int = 0
    open: int = 0
    closed: int = 0
    escalate_pending: int = Field(default=0, alias="escalatePending")
    waiting_assignment: int = Field(default=0, alias="waitingAssignment")
    escalate_approved: int = Field(default=0, alias="escalateApproved")
    #: HQ visit already scheduled — still on the escalation path
    #: (``ESCALATION_ACTIVE``) whatever the aggregate status says.
    escalate_scheduled: int = Field(default=0, alias="escalateScheduled")
    #: Open and already accepted by Pusat (``hq_accepted_at`` or
    #: ``HQ_SCHEDULED``). Cabang dashboard drops these from its work book;
    #: Pusat keeps them. Does not change DEC-025 ``open + closed == total``.
    hq_accepted_open: int = Field(default=0, alias="hqAcceptedOpen")
    #: Open and returned to the branch (``RETURNED_TO_BRANCH``). Extra KPI
    #: for cabang queue health — not a donut slice; those rows stay in
    #: ``waitingAssignment`` / ``inProgress`` so the partition still sums.
    returned_to_branch: int = Field(default=0, alias="returnedToBranch")
    in_progress: int = Field(default=0, alias="inProgress")
    sla: DashboardResolutionSla | None = Field(
        default=None,
        description="30-day resolution SLA rollup; null when not measured (DEC-031)",
    )


class DashboardOverviewResponse(BaseModel):
    """API-319 composition payload — never persisted."""

    model_config = ConfigDict(populate_by_name=True)

    header: DashboardHeader
    sla: DashboardSlaSummary
    recent_activity: list[DashboardRecentActivityItem] = Field(
        default_factory=list, alias="recentActivity"
    )


# Backward-compatible alias used by older imports / tests.
DashboardSummaryResponse = DashboardOverviewResponse
