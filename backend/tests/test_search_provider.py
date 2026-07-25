"""CAPABILITY-012 — ComplaintSearchProvider unit tests (mocked session)."""

from __future__ import annotations

import uuid
from datetime import UTC, datetime
from types import SimpleNamespace
from unittest.mock import MagicMock

from app.modules.search.domain.enums import ComplaintSortField, SortOrder
from app.modules.search.domain.filters import ComplaintSearchFilters
from app.modules.search.providers.complaint import ComplaintSearchProvider


def test_provider_search_applies_offset_limit_and_count() -> None:
    session = MagicMock()
    session.scalar.return_value = 42
    row = SimpleNamespace(id=uuid.uuid4())
    session.scalars.return_value.unique.return_value.all.return_value = [row]

    provider = ComplaintSearchProvider(session)
    filters = ComplaintSearchFilters(
        status="NEW",
        priority="HIGH",
        category="Billing",
        branch_id=uuid.uuid4(),
        created_by=uuid.uuid4(),
        created_from=datetime(2026, 1, 1, tzinfo=UTC),
        created_to=datetime(2026, 6, 1, tzinfo=UTC),
        page=2,
        page_size=10,
        sort=ComplaintSortField.UPDATED_AT,
        order=SortOrder.ASC,
    )
    items, total = provider.search(filters)
    assert total == 42
    assert items == [row]
    session.scalar.assert_called_once()
    session.scalars.assert_called_once()


def test_provider_joins_for_assignee_sla_keyword_escalated() -> None:
    session = MagicMock()
    session.scalar.return_value = 0
    session.scalars.return_value.unique.return_value.all.return_value = []
    provider = ComplaintSearchProvider(session)

    for filters in (
        ComplaintSearchFilters(assigned_to=uuid.uuid4()),
        ComplaintSearchFilters(sla_status="PENDING"),
        ComplaintSearchFilters(keyword="CMP-1"),
        ComplaintSearchFilters(escalated=True),
        ComplaintSearchFilters(escalated=False),
        ComplaintSearchFilters(
            sort=ComplaintSortField.SLA_DUE_DATE, order=SortOrder.DESC
        ),
        ComplaintSearchFilters(sort=ComplaintSortField.PRIORITY, order=SortOrder.ASC),
        ComplaintSearchFilters(keyword="   "),
    ):
        items, total = provider.search(filters)
        assert items == []
        assert total == 0
