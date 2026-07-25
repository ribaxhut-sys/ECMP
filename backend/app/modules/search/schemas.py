"""CAPABILITY-012 Search API schemas (read-only)."""

from __future__ import annotations

from math import ceil
from typing import Any, Generic, TypeVar

from pydantic import BaseModel, ConfigDict, Field

from app.modules.complaints.schemas import ComplaintResponse
from app.modules.search.domain.enums import ComplaintSortField, SortOrder

T = TypeVar("T")


class SearchPagination(BaseModel):
    """Database-side pagination metadata for search responses."""

    model_config = ConfigDict(populate_by_name=True)

    page: int = Field(ge=1)
    page_size: int = Field(alias="pageSize", ge=1, le=100)
    total_items: int = Field(alias="totalItems", ge=0)
    total_pages: int = Field(alias="totalPages", ge=0)
    has_next: bool = Field(alias="hasNext")
    has_previous: bool = Field(alias="hasPrevious")

    @classmethod
    def from_total(cls, *, page: int, page_size: int, total_items: int) -> SearchPagination:
        page = max(1, page)
        page_size = max(1, min(page_size, 100))
        total_items = max(0, total_items)
        total_pages = ceil(total_items / page_size) if total_items > 0 else 0
        return cls(
            page=page,
            pageSize=page_size,
            totalItems=total_items,
            totalPages=total_pages,
            hasNext=page < total_pages if total_pages > 0 else False,
            hasPrevious=page > 1 and total_items > 0,
        )


class SearchSort(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    field: ComplaintSortField
    order: SortOrder


class SearchResponse(BaseModel, Generic[T]):
    """Search envelope — items + pagination + applied filters + sort."""

    model_config = ConfigDict(populate_by_name=True)

    items: list[T]
    pagination: SearchPagination
    filters_applied: dict[str, Any] = Field(alias="filtersApplied")
    sort: SearchSort


ComplaintSearchResponse = SearchResponse[ComplaintResponse]
