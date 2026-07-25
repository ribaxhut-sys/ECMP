"""CAPABILITY-012 Search & Filtering HTTP routes (API-388).

Mounted before generic ``GET /complaints/{id}`` so ``search`` is not
parsed as a UUID path param.
"""

from __future__ import annotations

import uuid
from datetime import datetime
from typing import Annotated, Literal

from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.orm import Session

from app.core.auth import Principal, require_permissions
from app.core.enums import ComplaintStatus, SlaStatus
from app.db.session import get_db_session
from app.modules.search.domain.enums import ComplaintSortField, SortOrder
from app.modules.search.domain.filters import ComplaintSearchFilters
from app.modules.search.permissions import COMPLAINTS_READ
from app.modules.search.registration import build_search_service
from app.modules.search.schemas import ComplaintSearchResponse
from app.modules.search.service import SearchService

router = APIRouter(prefix="/api/v1/complaints", tags=["Search"])

PriorityFilter = Literal["LOW", "MEDIUM", "HIGH", "CRITICAL"]


def get_search_service(
    session: Annotated[Session, Depends(get_db_session)],
) -> SearchService:
    return build_search_service(session)


@router.get(
    "/search",
    response_model=ComplaintSearchResponse,
    status_code=status.HTTP_200_OK,
    summary="Search and filter complaints",
)
def search_complaints(
    service: Annotated[SearchService, Depends(get_search_service)],
    principal: Annotated[Principal, Depends(require_permissions(COMPLAINTS_READ))],
    keyword: Annotated[str | None, Query(max_length=200)] = None,
    status_filter: Annotated[
        ComplaintStatus | None, Query(alias="status")
    ] = None,
    priority: Annotated[PriorityFilter | None, Query()] = None,
    category: Annotated[str | None, Query(max_length=64)] = None,
    branch_id: Annotated[uuid.UUID | None, Query(alias="branchId")] = None,
    assigned_to: Annotated[uuid.UUID | None, Query(alias="assignedTo")] = None,
    created_by: Annotated[uuid.UUID | None, Query(alias="createdBy")] = None,
    created_from: Annotated[datetime | None, Query(alias="createdFrom")] = None,
    created_to: Annotated[datetime | None, Query(alias="createdTo")] = None,
    sla_status: Annotated[
        SlaStatus | None, Query(alias="slaStatus")
    ] = None,
    escalated: Annotated[bool | None, Query()] = None,
    page: Annotated[int, Query(ge=1)] = 1,
    page_size: Annotated[int, Query(alias="pageSize", ge=1, le=100)] = 20,
    sort: Annotated[ComplaintSortField, Query()] = ComplaintSortField.CREATED_AT,
    order: Annotated[SortOrder, Query()] = SortOrder.DESC,
) -> ComplaintSearchResponse:
    """API-388 — combinable filters, keyword, sort, DB-side pagination."""
    _ = principal
    filters = ComplaintSearchFilters(
        keyword=keyword.strip() if keyword else None,
        status=status_filter.value if status_filter else None,
        priority=priority,
        category=category.strip() if category else None,
        branch_id=branch_id,
        assigned_to=assigned_to,
        created_by=created_by,
        created_from=created_from,
        created_to=created_to,
        sla_status=sla_status.value if sla_status else None,
        escalated=escalated,
        page=page,
        page_size=page_size,
        sort=sort,
        order=order,
    )
    return service.search_complaints(filters)
