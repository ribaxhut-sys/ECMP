"""CAPABILITY-012 Search domain enums."""

from __future__ import annotations

from enum import StrEnum


class SortOrder(StrEnum):
    ASC = "asc"
    DESC = "desc"


class ComplaintSortField(StrEnum):
    """Sortable Complaint search columns (API camelCase values)."""

    CREATED_AT = "createdAt"
    UPDATED_AT = "updatedAt"
    PRIORITY = "priority"
    STATUS = "status"
    SLA_DUE_DATE = "slaDueDate"
