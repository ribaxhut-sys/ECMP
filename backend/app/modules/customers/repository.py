"""Customer persistence repository (local reference cache)."""

from __future__ import annotations

import uuid

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
                    Customer.phone.ilike(term),
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

    def get_by_id(self, customer_id: uuid.UUID) -> Customer | None:
        stmt = select(Customer).where(
            Customer.deleted_at.is_(None),
            Customer.id == customer_id,
        )
        return self._session.scalars(stmt).first()

    def update_phone(self, customer_id: uuid.UUID, phone: str) -> Customer | None:
        """Mode A lab: mutate local reference-cache phone only (not Customer Master)."""
        row = self.get_by_id(customer_id)
        if row is None:
            return None
        row.phone = phone.strip() or None
        self._session.add(row)
        self._session.commit()
        self._session.refresh(row)
        return row
