"""Customer persistence repository (local reference cache)."""

from __future__ import annotations

from sqlalchemy import Select, func, or_, select
from sqlalchemy.orm import Session

from app.models import Customer


class CustomerRepository:
    def __init__(self, session: Session) -> None:
        self._session = session

    def list_page(
        self,
        *,
        page: int,
        page_size: int,
        q: str | None = None,
    ) -> tuple[list[Customer], int]:
        filters = [Customer.deleted_at.is_(None)]
        if q:
            term = f"%{q.strip()}%"
            filters.append(
                or_(
                    Customer.external_customer_id.ilike(term),
                    Customer.full_name.ilike(term),
                    Customer.email.ilike(term),
                )
            )

        count_stmt = select(func.count()).select_from(Customer).where(*filters)
        total = int(self._session.scalar(count_stmt) or 0)

        stmt: Select[tuple[Customer]] = (
            select(Customer)
            .where(*filters)
            .order_by(Customer.full_name.asc(), Customer.created_at.asc())
            .offset((page - 1) * page_size)
            .limit(page_size)
        )
        items = list(self._session.scalars(stmt).all())
        return items, total
