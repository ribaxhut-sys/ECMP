"""CAPABILITY-012 Search application service (read-only)."""

from __future__ import annotations

from app.modules.complaints.schemas import ComplaintResponse
from app.modules.search.domain.filters import ComplaintSearchFilters
from app.modules.search.providers.complaint import ComplaintSearchProvider
from app.modules.search.schemas import (
    ComplaintSearchResponse,
    SearchPagination,
    SearchSort,
)


class SearchService:
    """Orchestrates SearchProviders — no domain mutation."""

    def __init__(self, complaint_provider: ComplaintSearchProvider) -> None:
        self._complaints = complaint_provider

    def search_complaints(
        self, filters: ComplaintSearchFilters
    ) -> ComplaintSearchResponse:
        rows, total = self._complaints.search(filters)
        items = [ComplaintResponse.model_validate(row) for row in rows]
        return ComplaintSearchResponse(
            items=items,
            pagination=SearchPagination.from_total(
                page=filters.page,
                page_size=filters.page_size,
                total_items=total,
            ),
            filtersApplied=filters.applied(),
            sort=SearchSort(field=filters.sort, order=filters.order),
        )
