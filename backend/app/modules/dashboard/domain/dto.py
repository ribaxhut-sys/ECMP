"""CAPABILITY-013 Dashboard domain DTOs — aggregation results only."""

from __future__ import annotations

import uuid
from dataclasses import dataclass
from datetime import date, datetime
from enum import StrEnum


class TrendPeriod(StrEnum):
    TODAY = "today"
    SEVEN_D = "7d"
    THIRTY_D = "30d"


@dataclass(frozen=True, slots=True)
class DashboardFilters:
    """Shared read filters for dashboard widgets."""

    branch_id: uuid.UUID | None = None
    date_from: datetime | None = None
    date_to: datetime | None = None


@dataclass(frozen=True, slots=True)
class ComplaintSummaryMetrics:
    total_complaints: int
    open_complaints: int
    closed_complaints: int
    pending_complaints: int
    overdue_complaints: int
    escalated_complaints: int
    today_complaints: int
    this_month_complaints: int


@dataclass(frozen=True, slots=True)
class QueueSummaryMetrics:
    waiting: int
    serving: int
    completed: int
    cancelled: int
    average_waiting_time: float
    """Average wait for WAITING tickets in seconds (0.0 when none)."""


@dataclass(frozen=True, slots=True)
class SlaSummaryMetrics:
    active: int
    breached: int
    resolved_within_sla: int
    resolved_outside_sla: int
    compliance_percentage: float


@dataclass(frozen=True, slots=True)
class NotificationSummaryMetrics:
    pending: int
    sent: int
    failed: int
    cancelled: int


@dataclass(frozen=True, slots=True)
class TrendBucket:
    day: date
    count: int


@dataclass(frozen=True, slots=True)
class KpiMetrics:
    complaint_resolution_rate: float
    sla_compliance: float
    escalation_rate: float
    average_resolution_time: float
    """Average resolution duration in seconds (0.0 when none)."""
    average_queue_waiting_time: float
    """Average WAITING ticket age in seconds (0.0 when none)."""
