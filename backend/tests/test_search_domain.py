"""CAPABILITY-012 — SearchPagination / filters / sort domain tests."""

from __future__ import annotations

import uuid
from datetime import UTC, datetime

from app.modules.search.domain.enums import ComplaintSortField, SortOrder
from app.modules.search.domain.filters import ComplaintSearchFilters
from app.modules.search.schemas import SearchPagination


def test_pagination_from_total_edge_cases() -> None:
    empty = SearchPagination.from_total(page=1, page_size=20, total_items=0)
    assert empty.total_pages == 0
    assert empty.has_next is False
    assert empty.has_previous is False

    mid = SearchPagination.from_total(page=2, page_size=10, total_items=25)
    assert mid.total_pages == 3
    assert mid.has_next is True
    assert mid.has_previous is True

    last = SearchPagination.from_total(page=3, page_size=10, total_items=25)
    assert last.has_next is False
    assert last.has_previous is True


def test_filters_applied_echo() -> None:
    branch = uuid.uuid4()
    filters = ComplaintSearchFilters(
        keyword="  bill  ",
        status="NEW",
        priority="HIGH",
        category="Billing",
        branch_id=branch,
        assigned_to=uuid.uuid4(),
        created_by=uuid.uuid4(),
        created_from=datetime(2026, 1, 1, tzinfo=UTC),
        created_to=datetime(2026, 12, 31, tzinfo=UTC),
        sla_status="BREACHED",
        escalated=True,
        sort=ComplaintSortField.PRIORITY,
        order=SortOrder.ASC,
    )
    applied = filters.applied()
    assert applied["keyword"] == "  bill  "
    assert applied["status"] == "NEW"
    assert applied["branchId"] == str(branch)
    assert applied["escalated"] is True
    assert "page" not in applied


def test_default_sort_is_created_at_desc() -> None:
    filters = ComplaintSearchFilters()
    assert filters.sort == ComplaintSortField.CREATED_AT
    assert filters.order == SortOrder.DESC
