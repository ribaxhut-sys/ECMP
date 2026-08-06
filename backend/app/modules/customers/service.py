"""Customer application service (no FastAPI imports)."""

from __future__ import annotations

import uuid

from app.core.errors import NotFoundError
from app.core.user_messages import m
from app.modules.customers.repository import CustomerRepository
from app.modules.customers.schemas import CustomerPhoneUpdateRequest, CustomerResponse


class CustomerService:
    def __init__(self, repository: CustomerRepository) -> None:
        self._repo = repository

    def list(
        self,
        *,
        page: int,
        page_size: int,
        q: str | None = None,
    ) -> tuple[list[CustomerResponse], int]:
        rows, total = self._repo.list_page(page=page, page_size=page_size, q=q)
        return [CustomerResponse.model_validate(row) for row in rows], total

    def update_phone(
        self,
        customer_id: uuid.UUID,
        body: CustomerPhoneUpdateRequest,
    ) -> CustomerResponse:
        phone = (body.phone or "").strip()
        row = self._repo.update_phone(customer_id, phone)
        if row is None:
            raise NotFoundError(m("customer.not_found"))
        return CustomerResponse.model_validate(row)
