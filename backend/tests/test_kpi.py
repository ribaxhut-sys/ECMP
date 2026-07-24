"""KPI Foundation unit/service tests (TASK-026 / API-318)."""

from __future__ import annotations

import uuid
from datetime import UTC, datetime, timedelta
from unittest.mock import MagicMock

import pytest

from app.core.errors import ValidationAppError
from app.models import SlaRecord
from app.modules.kpi.service import KpiService


def test_complaint_totals_and_open_closed() -> None:
    repo = MagicMock()
    repo.count_complaints.return_value = (10, 7, 3)
    repo.count_sla_pair.return_value = (0, 0)

    result = KpiService(repo).summary()

    assert result.complaints.total == 10
    assert result.complaints.open == 7
    assert result.complaints.closed == 3
    repo.count_complaints.assert_called_once()


def test_assignment_metrics() -> None:
    repo = MagicMock()
    repo.count_complaints.return_value = (0, 0, 0)

    def _pair(*, status_column, **_kwargs):
        if status_column is SlaRecord.assignment_status:
            return (4, 2)
        return (0, 0)

    repo.count_sla_pair.side_effect = _pair
    result = KpiService(repo).summary()
    assert result.assignment.completed == 4
    assert result.assignment.breached == 2


def test_resolution_escalation_overall_metrics() -> None:
    repo = MagicMock()
    repo.count_complaints.return_value = (5, 5, 0)

    def _pair(*, status_column, **_kwargs):
        mapping = {
            id(SlaRecord.assignment_status): (1, 0),
            id(SlaRecord.appointment_status): (1, 1),
            id(SlaRecord.resolution_status): (2, 3),
            id(SlaRecord.escalation_status): (0, 4),
            id(SlaRecord.overall_status): (1, 5),
        }
        return mapping.get(id(status_column), (0, 0))

    repo.count_sla_pair.side_effect = _pair
    result = KpiService(repo).summary()
    assert result.resolution.completed == 2
    assert result.resolution.breached == 3
    assert result.escalation.breached == 4
    assert result.overall.completed == 1
    assert result.overall.breached == 5


def test_date_filter_validation() -> None:
    repo = MagicMock()
    with pytest.raises(ValidationAppError):
        KpiService(repo).summary(
            date_from=datetime(2026, 7, 23, tzinfo=UTC),
            date_to=datetime(2026, 7, 22, tzinfo=UTC),
        )
    repo.count_complaints.assert_not_called()


def test_branch_category_priority_filters_forwarded() -> None:
    repo = MagicMock()
    repo.count_complaints.return_value = (1, 1, 0)
    repo.count_sla_pair.return_value = (0, 0)
    branch_id = uuid.uuid4()
    date_from = datetime(2026, 7, 1, tzinfo=UTC)
    date_to = date_from + timedelta(days=7)

    KpiService(repo).summary(
        branch_id=branch_id,
        date_from=date_from,
        date_to=date_to,
        category="BILLING",
        priority="HIGH",
    )

    kwargs = repo.count_complaints.call_args.kwargs
    assert kwargs["branch_id"] == branch_id
    assert kwargs["category"] == "BILLING"
    assert kwargs["priority"] == "HIGH"
    assert kwargs["date_from"] == date_from
    assert kwargs["date_to"] == date_to
