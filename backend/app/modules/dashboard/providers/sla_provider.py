"""SLA dashboard aggregates — CAP-006 deferred; no Foundation sla_records."""

from __future__ import annotations

from sqlalchemy.orm import Session

from app.modules.dashboard.domain.dto import DashboardFilters, SlaSummaryMetrics


class SlaDashboardProvider:
    """Always-zero SLA clocks (BQ-005 / DEC-026). Does not query ``complaints``."""

    def __init__(self, session: Session) -> None:
        self._session = session

    def summary(self, filters: DashboardFilters) -> SlaSummaryMetrics:
        _ = (self._session, filters)
        return SlaSummaryMetrics(
            active=0,
            breached=0,
            resolved_within_sla=0,
            resolved_outside_sla=0,
            compliance_percentage=0.0,
        )
