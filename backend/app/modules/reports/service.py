"""Report application service (no FastAPI imports)."""

from __future__ import annotations

import uuid
from datetime import UTC, datetime

from app.core.errors import ValidationAppError
from app.core.user_messages import m
from app.modules.cm_batch1.complaint_number import resolve_unit_code
from app.modules.reports.pdf import ReportPrintData, build_report_pdf
from app.modules.reports.repository import ReportRepository
from app.modules.reports.schemas import (
    AggregateComplaintStatus,
    BranchCount,
    CycleTimeBucket,
    CycleTimeData,
    ReportPrintCategory,
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
        for status in AggregateComplaintStatus
    ]


def _percentile(sorted_days: list[float], fraction: float) -> float:
    """Linear-interpolated percentile over an already sorted list."""
    if not sorted_days:
        return 0.0
    if len(sorted_days) == 1:
        return sorted_days[0]
    position = fraction * (len(sorted_days) - 1)
    low = int(position)
    high = min(low + 1, len(sorted_days) - 1)
    weight = position - low
    return sorted_days[low] * (1 - weight) + sorted_days[high] * weight


# Age bands for the closed-case distribution; last band is the open-ended tail.
_CYCLE_TIME_BANDS: tuple[tuple[str, float | None], ...] = (
    ("sameDay", 1.0),
    ("upTo3Days", 3.0),
    ("upTo7Days", 7.0),
    ("over7Days", None),
)


def _cycle_time_buckets(days: list[float]) -> list[CycleTimeBucket]:
    counts = {key: 0 for key, _ in _CYCLE_TIME_BANDS}
    for value in days:
        for key, upper in _CYCLE_TIME_BANDS:
            if upper is None or value <= upper:
                counts[key] += 1
                break
    return [CycleTimeBucket(key=key, count=counts[key]) for key, _ in _CYCLE_TIME_BANDS]


def _round_days(value: float) -> float:
    return round(value, 1)


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
                unitCode=resolve_unit_code(code) if code else None,
                total=total,
                open=open_count,
                closed=closed,
                escalated=escalated,
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
                escalated,
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

    def cycle_time(
        self,
        *,
        branch_id: uuid.UUID | None = None,
        date_from: datetime | None = None,
        date_to: datetime | None = None,
    ) -> CycleTimeData:
        """How long closed cases took (RES-CM), over the closure window.

        Complaints carry no ``closed_at``, so cycle time is measured on Cases —
        the unit that actually records closure time.
        """
        date_from, date_to = _validate_filters(date_from=date_from, date_to=date_to)
        days = sorted(
            self._repo.closed_case_durations_days(
                branch_id=branch_id, date_from=date_from, date_to=date_to
            )
        )
        if not days:
            return CycleTimeData(closedCases=0, buckets=_cycle_time_buckets([]))
        return CycleTimeData(
            closedCases=len(days),
            averageDays=_round_days(sum(days) / len(days)),
            medianDays=_round_days(_percentile(days, 0.5)),
            p90Days=_round_days(_percentile(days, 0.9)),
            fastestDays=_round_days(days[0]),
            slowestDays=_round_days(days[-1]),
            buckets=_cycle_time_buckets(days),
        )

    def print_pdf(
        self,
        *,
        category: ReportPrintCategory,
        period_label: str,
        branch_id: uuid.UUID | None = None,
        branch_label: str | None = None,
        date_from: datetime | None = None,
        date_to: datetime | None = None,
        generated_at: datetime | None = None,
    ) -> bytes:
        """Export-to-PDF for /reports — same filters/predicates as the screen,
        rendered server-side so the file looks the same on every browser."""
        date_from, date_to = _validate_filters(date_from=date_from, date_to=date_to)

        total_created = 0
        by_status: list[StatusCount] = []
        resolved = 0
        escalated = 0
        cycle_time: CycleTimeData | None = None

        if category in (ReportPrintCategory.ALL, ReportPrintCategory.CREATED):
            total_created = self._repo.count_total(
                branch_id=branch_id, date_from=date_from, date_to=date_to
            )
            by_status = _status_counts(
                self._repo.count_by_status(
                    branch_id=branch_id, date_from=date_from, date_to=date_to
                )
            )
        if category in (ReportPrintCategory.ALL, ReportPrintCategory.RESOLVED):
            resolved = self._repo.count_resolved(
                branch_id=branch_id, date_from=date_from, date_to=date_to
            )
            if category == ReportPrintCategory.RESOLVED:
                cycle_time = self.cycle_time(
                    branch_id=branch_id, date_from=date_from, date_to=date_to
                )
        if category in (ReportPrintCategory.ALL, ReportPrintCategory.ESCALATED):
            escalated = self._repo.count_escalated(
                branch_id=branch_id, date_from=date_from, date_to=date_to
            )

        payload = ReportPrintData(
            category=category,
            period_label=period_label,
            branch_label=branch_label,
            generated_at=generated_at or datetime.now(UTC),
            total_created=total_created,
            by_status=by_status,
            resolved=resolved,
            escalated=escalated,
            cycle_time=cycle_time,
        )
        return build_report_pdf(payload)
