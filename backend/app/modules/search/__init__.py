"""CAPABILITY-012 reusable Search & Filtering (read-only).

Initially backs Complaint search. Architecture is provider-based so Queue /
Notification / etc. can plug in later without domain mutation.
"""

from app.modules.search.domain import (
    ComplaintSearchFilters,
    ComplaintSortField,
    SortOrder,
)
from app.modules.search.registration import build_search_service
from app.modules.search.service import SearchService

__all__ = [
    "ComplaintSearchFilters",
    "ComplaintSortField",
    "SearchService",
    "SortOrder",
    "build_search_service",
]
