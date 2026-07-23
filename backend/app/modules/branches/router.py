"""Branch HTTP routes — reference list (API-223)."""

from __future__ import annotations

from typing import Annotated

from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.orm import Session

from app.core.auth import Principal, require_permissions
from app.core.schemas import ListResponse, PageMeta
from app.db.session import get_db_session
from app.modules.branches.repository import BranchRepository
from app.modules.branches.schemas import BranchResponse
from app.modules.branches.service import BranchService

router = APIRouter(prefix="/api/v1/branches", tags=["Branches"])


def get_branch_service(
    session: Annotated[Session, Depends(get_db_session)],
) -> BranchService:
    return BranchService(BranchRepository(session))


@router.get(
    "",
    response_model=ListResponse[BranchResponse],
    status_code=status.HTTP_200_OK,
    summary="List branch references",
)
def list_branches(
    service: Annotated[BranchService, Depends(get_branch_service)],
    principal: Annotated[Principal, Depends(require_permissions("complaints:read"))],
    page: Annotated[int, Query(ge=1)] = 1,
    page_size: Annotated[int, Query(alias="pageSize", ge=1, le=100)] = 20,
    q: Annotated[str | None, Query(max_length=200)] = None,
) -> ListResponse[BranchResponse]:
    _ = principal
    items, total = service.list(page=page, page_size=page_size, q=q)
    return ListResponse(
        data=items,
        meta=PageMeta(page=page, pageSize=page_size, totalItems=total),
    )
