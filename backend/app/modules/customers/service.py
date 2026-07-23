"""Customer application service (no FastAPI imports)."""

from __future__ import annotations

from app.modules.customers.repository import CustomerRepository
from app.modules.customers.schemas import CustomerResponse


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
