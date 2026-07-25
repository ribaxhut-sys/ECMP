"""CAPABILITY-012 Complaint search filter criteria (immutable)."""

from __future__ import annotations

import uuid
from dataclasses import dataclass
from datetime import datetime

from app.modules.search.domain.enums import ComplaintSortField, SortOrder


@dataclass(frozen=True, slots=True)
class ComplaintSearchFilters:
    """Read-only filter bag for Complaint search — no domain mutation."""

    keyword: str | None = None
    status: str | None = None
    priority: str | None = None
    category: str | None = None
    branch_id: uuid.UUID | None = None
    assigned_to: uuid.UUID | None = None
    created_by: uuid.UUID | None = None
    created_from: datetime | None = None
    created_to: datetime | None = None
    sla_status: str | None = None
    escalated: bool | None = None
    page: int = 1
    page_size: int = 20
    sort: ComplaintSortField = ComplaintSortField.CREATED_AT
    order: SortOrder = SortOrder.DESC

    def applied(self) -> dict[str, object]:
        """Non-default filters for response ``filtersApplied``."""
        out: dict[str, object] = {}
        if self.keyword:
            out["keyword"] = self.keyword
        if self.status is not None:
            out["status"] = self.status
        if self.priority is not None:
            out["priority"] = self.priority
        if self.category is not None:
            out["category"] = self.category
        if self.branch_id is not None:
            out["branchId"] = str(self.branch_id)
        if self.assigned_to is not None:
            out["assignedTo"] = str(self.assigned_to)
        if self.created_by is not None:
            out["createdBy"] = str(self.created_by)
        if self.created_from is not None:
            out["createdFrom"] = self.created_from.isoformat()
        if self.created_to is not None:
            out["createdTo"] = self.created_to.isoformat()
        if self.sla_status is not None:
            out["slaStatus"] = self.sla_status
        if self.escalated is not None:
            out["escalated"] = self.escalated
        return out
