"""Customer HTTP routes — local reference cache (API-222)."""

from __future__ import annotations

import uuid
from typing import Annotated

from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.orm import Session

from app.core.auth import Principal, require_permissions
from app.core.schemas import DataResponse, ListResponse, PageMeta
from app.db.session import get_db_session
from app.modules.customers.repository import CustomerRepository
from app.modules.customers.schemas import (
    CustomerPhoneUpdateRequest,
    CustomerResponse,
)
from app.modules.customers.service import CustomerService

router = APIRouter(prefix="/api/v1/customers", tags=["Customers"])


def get_customer_service(
    session: Annotated[Session, Depends(get_db_session)],
) -> CustomerService:
    return CustomerService(CustomerRepository(session))


@router.get(
    "",
    response_model=ListResponse[CustomerResponse],
    status_code=status.HTTP_200_OK,
    summary="List customer references",
)
def list_customers(
    service: Annotated[CustomerService, Depends(get_customer_service)],
    principal: Annotated[Principal, Depends(require_permissions("complaints:read"))],
    page: Annotated[int, Query(ge=1)] = 1,
    page_size: Annotated[int, Query(alias="pageSize", ge=1, le=100)] = 20,
    q: Annotated[str | None, Query(max_length=200)] = None,
) -> ListResponse[CustomerResponse]:
    _ = principal
    items, total = service.list(page=page, page_size=page_size, q=q)
    return ListResponse(
        data=items,
        meta=PageMeta(page=page, pageSize=page_size, totalItems=total),
    )


@router.patch(
    "/{customer_id}",
    response_model=DataResponse[CustomerResponse],
    status_code=status.HTTP_200_OK,
    summary="Update local customer reference phone (Mode A cache)",
)
def update_customer_phone(
    customer_id: uuid.UUID,
    body: CustomerPhoneUpdateRequest,
    service: Annotated[CustomerService, Depends(get_customer_service)],
    principal: Annotated[
        Principal, Depends(require_permissions("customers:update"))
    ],
) -> DataResponse[CustomerResponse]:
    """Mutates lab ``customers`` cache only — not Enterprise Customer Master (ADR-002)."""
    _ = principal
    return DataResponse(data=service.update_phone(customer_id, body))
