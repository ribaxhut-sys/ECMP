"""CAPABILITY-013 SLA dashboard aggregates (SQL only)."""

from __future__ import annotations

from sqlalchemy import and_, case, func, select
from sqlalchemy.orm import Session

from app.core.enums import ComplaintStatus, SlaStatus
from app.models import Complaint, SlaRecord
from app.modules.dashboard.domain.dto import DashboardFilters, SlaSummaryMetrics

_RESOLVED_STATUSES = (
    ComplaintStatus.RESOLVED.value,
    ComplaintStatus.CLOSED.value,
)


class SlaDashboardProvider:
    """Read-only SLA compliance aggregates. Reuses sla_records + complaints."""

    def __init__(self, session: Session) -> None:
        self._session = session

    def summary(self, filters: DashboardFilters) -> SlaSummaryMetrics:
        clauses = self._base_filters(filters)

        stmt = (
            select(
                func.coalesce(
                    func.sum(
                        case(
                            (
                                SlaRecord.overall_status == SlaStatus.PENDING.value,
                                1,
                            ),
                            else_=0,
                        )
                    ),
                    0,
                ).label("active"),
                func.coalesce(
                    func.sum(
                        case(
                            (
                                SlaRecord.overall_status
                                == SlaStatus.BREACHED.value,
                                1,
                            ),
                            else_=0,
                        )
                    ),
                    0,
                ).label("breached"),
                func.coalesce(
                    func.sum(
                        case(
                            (
                                and_(
                                    SlaRecord.overall_status
                                    == SlaStatus.COMPLETED.value,
                                    Complaint.status.in_(_RESOLVED_STATUSES),
                                ),
                                1,
                            ),
                            else_=0,
                        )
                    ),
                    0,
                ).label("within"),
                func.coalesce(
                    func.sum(
                        case(
                            (
                                and_(
                                    SlaRecord.overall_status
                                    == SlaStatus.BREACHED.value,
                                    Complaint.status.in_(_RESOLVED_STATUSES),
                                ),
                                1,
                            ),
                            else_=0,
                        )
                    ),
                    0,
                ).label("outside"),
            )
            .select_from(SlaRecord)
            .join(Complaint, Complaint.id == SlaRecord.complaint_id)
        )
        if clauses:
            stmt = stmt.where(*clauses)
        row = self._session.execute(stmt).one()
        within = int(row.within or 0)
        outside = int(row.outside or 0)
        decided = within + outside
        compliance = (
            round((within / decided) * 100.0, 2) if decided > 0 else 0.0
        )
        return SlaSummaryMetrics(
            active=int(row.active or 0),
            breached=int(row.breached or 0),
            resolved_within_sla=within,
            resolved_outside_sla=outside,
            compliance_percentage=compliance,
        )

    def _base_filters(self, filters: DashboardFilters) -> list[object]:
        clauses: list[object] = [Complaint.deleted_at.is_(None)]
        if filters.branch_id is not None:
            clauses.append(Complaint.branch_id == filters.branch_id)
        if filters.date_from is not None:
            clauses.append(Complaint.reported_at >= filters.date_from)
        if filters.date_to is not None:
            clauses.append(Complaint.reported_at <= filters.date_to)
        return clauses
