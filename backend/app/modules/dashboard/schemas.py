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
    in_progress: int = Field(default=0, alias="inProgress")


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
