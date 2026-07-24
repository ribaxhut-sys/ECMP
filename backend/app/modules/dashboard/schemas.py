"""Dashboard Summary contracts (API-319 / TASK-027). Composition only."""

from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


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


class DashboardSummaryResponse(BaseModel):
    """Aggregated dashboard payload — never persisted."""

    model_config = ConfigDict(populate_by_name=True)

    header: DashboardHeader
    sla: DashboardSlaSummary
    recent_activity: list[DashboardRecentActivityItem] = Field(
        default_factory=list, alias="recentActivity"
    )
