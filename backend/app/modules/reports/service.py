"""Report application service (no FastAPI imports)."""

from __future__ import annotations

import uuid
from datetime import UTC, datetime

from app.core.enums import ComplaintStatus
from app.core.errors import ValidationAppError
from app.core.user_messages import m
from app.modules.reports.repository import ReportRepository
from app.modules.reports.schemas import (
    BranchCount,
    ReportSummaryData,
    StatusCount,
)


def _ensure_utc(value: datetime) -> datetime:
    if value.tzinfo is None:
        return value.replace(tzinfo=UTC)
    return value


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
            m("config.date_from_lte_date_to"),
            details={
                "dateFrom": normalized_from.isoformat(),
                "dateTo": normalized_to.isoformat(),
            },
        )
    return normalized_from, normalized_to


def _status_counts(raw: list[tuple[str, int]]) -> list[StatusCount]:
    counted = {status: count for status, count in raw}
    return [
        StatusCount(status=status, count=counted.get(status.value, 0))
        for status in ComplaintStatus
    ]


def _completion_ratio(closed: int, total: int) -> float:
    if total <= 0:
        return -1.0
    return closed / total


class ReportService:
    def __init__(self, repository: ReportRepository) -> None:
        self._repo = repository

    def summary(
        self,
        *,
        branch_id: uuid.UUID | None = None,
        date_from: datetime | None = None,
        date_to: datetime | None = None,
    ) -> ReportSummaryData:
        date_from, date_to = _validate_filters(date_from=date_from, date_to=date_to)
        total = self._repo.count_total(
            branch_id=branch_id, date_from=date_from, date_to=date_to
        )
        by_status = _status_counts(
            self._repo.count_by_status(
                branch_id=branch_id, date_from=date_from, date_to=date_to
            )
        )
        return ReportSummaryData(total=total, byStatus=by_status)

    def by_status(
        self,
        *,
        branch_id: uuid.UUID | None = None,
        date_from: datetime | None = None,
        date_to: datetime | None = None,
    ) -> list[StatusCount]:
        date_from, date_to = _validate_filters(date_from=date_from, date_to=date_to)
        return _status_counts(
            self._repo.count_by_status(
                branch_id=branch_id, date_from=date_from, date_to=date_to
            )
        )

    def by_branch(
        self,
        *,
        branch_id: uuid.UUID | None = None,
        date_from: datetime | None = None,
        date_to: datetime | None = None,
    ) -> list[BranchCount]:
        date_from, date_to = _validate_filters(date_from=date_from, date_to=date_to)
        rows = self._repo.count_by_branch(
            branch_id=branch_id, date_from=date_from, date_to=date_to
        )
        items = [
            BranchCount(
                branchId=row_branch_id,
                branchCode=code,
                branchName=name,
                total=total,
                open=open_count,
                closed=closed,
                caseTotal=case_total,
                caseOpen=case_open,
                caseClosed=case_closed,
            )
            for (
                row_branch_id,
                code,
                name,
                total,
                open_count,
                closed,
                case_total,
                case_open,
                case_closed,
            ) in rows
        ]
        items.sort(
            key=lambda row: (
                _completion_ratio(row.case_closed, row.case_total),
                row.total,
            ),
            reverse=True,
        )
        return items
