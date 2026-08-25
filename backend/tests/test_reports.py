"""Report service unit tests."""

from __future__ import annotations

import uuid
from datetime import UTC, datetime
from unittest.mock import MagicMock

import pytest

from app.core.errors import ValidationAppError
from app.modules.reports.repository import ReportRepository
from app.modules.reports.schemas import AggregateComplaintStatus
from app.modules.reports.service import ReportService


def test_summary_uses_aggregate_status_enum() -> None:
    repo = MagicMock()
    repo.count_total.return_value = 5
    repo.count_by_status.return_value = [("REGISTERED", 3), ("CLOSED", 2)]

    result = ReportService(repo).summary()

    assert result.total == 5
    assert len(result.by_status) == len(AggregateComplaintStatus)
    by_status = {item.status: item.count for item in result.by_status}
    assert by_status[AggregateComplaintStatus.REGISTERED] == 3
    assert by_status[AggregateComplaintStatus.CLOSED] == 2
    assert by_status[AggregateComplaintStatus.IN_PROGRESS] == 0


def test_by_status_fills_missing_statuses() -> None:
    repo = MagicMock()
    repo.count_by_status.return_value = [("REGISTERED", 4)]

    result = ReportService(repo).by_status()

    assert [item.status for item in result] == list(AggregateComplaintStatus)
    assert result[0].status == AggregateComplaintStatus.REGISTERED
    assert result[0].count == 4
    assert result[1].count == 0


def test_by_branch_sorts_by_case_completion_percent() -> None:
    branch_a = uuid.uuid4()
    branch_b = uuid.uuid4()
    repo = MagicMock()
    repo.count_by_branch.return_value = [
        (branch_a, "UPPPD-TANAH-ABANG", "UPPPD Tanah Abang", 10, 9, 1, 2, 8, 2, 6),
        (branch_b, "BR-B", "Beta", 3, 0, 3, 1, 3, 0, 3),
        (None, None, None, 1, 1, 0, 0, 0, 0, 0),
    ]

    result = ReportService(repo).by_branch()

    assert [item.branch_code for item in result] == ["BR-B", "UPPPD-TANAH-ABANG", None]
    assert result[0].closed == 3
    assert result[1].closed == 1
    assert result[0].unit_code == "BRB"
    assert result[1].unit_code == "TAB"
    assert result[2].unit_code is None
    assert result[0].escalated == 1
    assert result[1].escalated == 2


def test_invalid_date_range_rejected() -> None:
    repo = MagicMock()
    service = ReportService(repo)
    date_from = datetime(2026, 7, 20, tzinfo=UTC)
    date_to = datetime(2026, 7, 10, tzinfo=UTC)

    with pytest.raises(ValidationAppError):
        service.summary(date_from=date_from, date_to=date_to)
    repo.count_total.assert_not_called()


def test_combine_case_counts_adds_implied_no_case_complaints() -> None:
    assert ReportRepository._combine_case_counts((5, 3, 2), (4, 1, 3)) == (9, 4, 5)


def test_count_by_branch_branch_resolved_excludes_hq_escalated_closed() -> None:
    """caseClosed = selesai di cabang; escalated = open only (opsi B)."""
    session = MagicMock()
    repo = ReportRepository(session)
    branch_id = uuid.uuid4()
    session.execute.return_value.all.side_effect = [
        # total=4, closed=2, escalated=1 (open-only already applied in SQL mock)
        [(branch_id, "UPPPD-TANAH-ABANG", "UPPPD Tanah Abang", 4, 2, 1)],
        # cases: 3 total, 2 all_closed, 1 branch_resolved (1 CLOSED+escalatedToPusat)
        [("UPPPD-TANAH-ABANG", 3, 2, 1)],
        # implied: 1 CLOSED HQ_CLOSED → all_closed=1, branch_resolved=0
        [("UPPPD-TANAH-ABANG", 1, 1, 0)],
    ]
    rows = repo.count_by_branch()
    row = rows[0]
    assert row[3:7] == (4, 2, 2, 1)  # total, open, closed, escalated
    assert row[7:10] == (4, 1, 1)  # caseTotal, caseOpen, caseClosed (branch)


def test_count_by_branch_keeps_idle_active_branches() -> None:
    """Kesehatan Cabang needs the full unit set, including zeros."""
    session = MagicMock()
    repo = ReportRepository(session)
    idle_id = uuid.uuid4()
    active_id = uuid.uuid4()
    session.execute.return_value.all.side_effect = [
        [
            (idle_id, "UPPPD-GAMBIR", "UPPPD Gambir", 0, 0, 0),
            (active_id, "UPPPD-TANAH-ABANG", "UPPPD Tanah Abang", 12, 5, 2),
        ],
        # (unit, total, all_closed, branch_resolved)
        [("UPPPD-TANAH-ABANG", 10, 2, 2)],
        [],
    ]
    rows = repo.count_by_branch()
    codes = [row[1] for row in rows]
    assert codes[0] == "UPPPD-TANAH-ABANG"
    assert "UPPPD-GAMBIR" in codes
    assert rows[0][3] == 12
    gambir = next(row for row in rows if row[1] == "UPPPD-GAMBIR")
    assert gambir[3:] == (0, 0, 0, 0, 0, 0, 0)


def test_cycle_time_summarizes_closed_case_durations() -> None:
    """Average, median, p90 and the age-band distribution over closed cases."""
    repo = MagicMock()
    repo.closed_case_durations_days.return_value = [0.5, 2.0, 5.0, 9.0, 4.0]

    result = ReportService(repo).cycle_time()

    assert result.closed_cases == 5
    assert result.average_days == 4.1
    assert result.median_days == 4.0
    assert result.p90_days == 7.4
    assert result.fastest_days == 0.5
    assert result.slowest_days == 9.0
    assert {b.key: b.count for b in result.buckets} == {
        "sameDay": 1,
        "upTo3Days": 1,
        "upTo7Days": 2,
        "over7Days": 1,
    }


def test_cycle_time_empty_window_reports_zero_not_none_buckets() -> None:
    repo = MagicMock()
    repo.closed_case_durations_days.return_value = []

    result = ReportService(repo).cycle_time()

    assert result.closed_cases == 0
    assert result.average_days is None
    assert [b.count for b in result.buckets] == [0, 0, 0, 0]


def test_cycle_time_rejects_inverted_window() -> None:
    repo = MagicMock()
    with pytest.raises(ValidationAppError):
        ReportService(repo).cycle_time(
            date_from=datetime(2026, 8, 31, tzinfo=UTC),
            date_to=datetime(2026, 8, 1, tzinfo=UTC),
        )
    repo.closed_case_durations_days.assert_not_called()


def test_cycle_time_forwards_normalized_window_to_repository() -> None:
    repo = MagicMock()
    repo.closed_case_durations_days.return_value = []

    ReportService(repo).cycle_time(date_from=datetime(2026, 8, 1))

    repo.closed_case_durations_days.assert_called_once_with(
        branch_id=None, date_from=datetime(2026, 8, 1, tzinfo=UTC), date_to=None
    )
