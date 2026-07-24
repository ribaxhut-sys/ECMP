"""KPI Foundation service — read-only aggregations (TASK-026 / DEC-015)."""

from __future__ import annotations

import uuid
from datetime import UTC, datetime

from app.core.errors import ValidationAppError
from app.models import SlaRecord
from app.modules.kpi.repository import KpiRepository
from app.modules.kpi.schemas import (
    ComplaintKpiCounts,
    KpiSummaryResponse,
    SlaStageKpiCounts,
)


def _ensure_utc(value: datetime) -> datetime:
    if value.tzinfo is None:
        return value.replace(tzinfo=UTC)
    return value.astimezone(UTC)


def _validate_filters(
    *,
    date_from: datetime | None,
    date_to: datetime | None,
) -> tuple[datetime | None, datetime | None]:
    normalized_from = _ensure_utc(date_from) if date_from is not None else None
    normalized_to = _ensure_utc(date_to) if date_to is not None else None
    if (
        normalized_from is not None
        and normalized_to is not None
        and normalized_from > normalized_to
    ):
        raise ValidationAppError(
            "dateFrom must be less than or equal to dateTo",
            details={
                "dateFrom": normalized_from.isoformat(),
                "dateTo": normalized_to.isoformat(),
            },
        )
    return normalized_from, normalized_to


class KpiService:
    def __init__(self, repository: KpiRepository) -> None:
        self._repo = repository

    def summary(
        self,
        *,
        branch_id: uuid.UUID | None = None,
        date_from: datetime | None = None,
        date_to: datetime | None = None,
        category: str | None = None,
        priority: str | None = None,
    ) -> KpiSummaryResponse:
        """Live KPI summary from operational tables. Never persists."""
        date_from, date_to = _validate_filters(
            date_from=date_from, date_to=date_to
        )
        filters = {
            "branch_id": branch_id,
            "date_from": date_from,
            "date_to": date_to,
            "category": category,
            "priority": priority,
        }

        total, open_count, closed = self._repo.count_complaints(**filters)
        assignment = self._repo.count_sla_pair(
            status_column=SlaRecord.assignment_status, **filters
        )
        appointment = self._repo.count_sla_pair(
            status_column=SlaRecord.appointment_status, **filters
        )
        resolution = self._repo.count_sla_pair(
            status_column=SlaRecord.resolution_status, **filters
        )
        escalation = self._repo.count_sla_pair(
            status_column=SlaRecord.escalation_status, **filters
        )
        overall = self._repo.count_sla_pair(
            status_column=SlaRecord.overall_status, **filters
        )

        return KpiSummaryResponse(
            complaints=ComplaintKpiCounts(
                total=total, open=open_count, closed=closed
            ),
            assignment=SlaStageKpiCounts(
                completed=assignment[0], breached=assignment[1]
            ),
            appointment=SlaStageKpiCounts(
                completed=appointment[0], breached=appointment[1]
            ),
            resolution=SlaStageKpiCounts(
                completed=resolution[0], breached=resolution[1]
            ),
            escalation=SlaStageKpiCounts(
                completed=escalation[0], breached=escalation[1]
            ),
            overall=SlaStageKpiCounts(
                completed=overall[0], breached=overall[1]
            ),
        )
