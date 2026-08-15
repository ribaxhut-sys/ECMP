"""Report service unit tests."""

from __future__ import annotations

import uuid
from datetime import UTC, datetime
from unittest.mock import MagicMock

import pytest

from app.core.enums import ComplaintStatus
from app.core.errors import ValidationAppError
from app.modules.reports.repository import ReportRepository
from app.modules.reports.service import ReportService


def test_summary_uses_complaint_status_enum() -> None:
    repo = MagicMock()
    repo.count_total.return_value = 5
    repo.count_by_status.return_value = [("NEW", 3), ("CLOSED", 2)]

    result = ReportService(repo).summary()

    assert result.total == 5
    assert len(result.by_status) == len(ComplaintStatus)
    by_status = {item.status: item.count for item in result.by_status}
    assert by_status[ComplaintStatus.NEW] == 3
    assert by_status[ComplaintStatus.CLOSED] == 2
    assert by_status[ComplaintStatus.ASSIGNED] == 0


def test_by_status_fills_missing_statuses() -> None:
    repo = MagicMock()
    repo.count_by_status.return_value = [("ASSIGNED", 4)]

    result = ReportService(repo).by_status()

    assert [item.status for item in result] == list(ComplaintStatus)
    assert result[1].status == ComplaintStatus.ASSIGNED
    assert result[1].count == 4


def test_by_branch_sorts_by_case_completion_percent() -> None:
    branch_a = uuid.uuid4()
    branch_b = uuid.uuid4()
    repo = MagicMock()
    repo.count_by_branch.return_value = [
        (branch_a, "BR-A", "Alpha", 10, 9, 1, 8, 2, 6),
        (branch_b, "BR-B", "Beta", 3, 0, 3, 3, 0, 3),
        (None, None, None, 1, 1, 0, 0, 0, 0),
    ]

    result = ReportService(repo).by_branch()

    assert [item.branch_code for item in result] == ["BR-B", "BR-A", None]
    assert result[0].closed == 3
    assert result[1].closed == 1


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
