"""Local customer reference-cache provider (lab) — ADR-002, not Customer Master SoR.

Reads Postgres ``customers`` so lab seed (ID / name / phone) is searchable
via CM Batch-1 API-502 without inventing an enterprise master.
"""

from __future__ import annotations

import re

from sqlalchemy import or_, select
from sqlalchemy.orm import Session

from app.integrations.customer.types import (
    CustomerExistsResult,
    CustomerLookupResult,
    CustomerLookupStatus,
    MinimalCustomer,
)
from app.models import Customer


def _digits_only(value: str) -> str:
    return re.sub(r"\D+", "", value)


def _to_minimal(row: Customer) -> MinimalCustomer:
    external = (row.external_customer_id or "").strip()
    phone = (row.phone or "").strip()
    email = (row.email or "").strip()
    return MinimalCustomer(
        customer_id=str(row.id),
        customer_number=external or str(row.id),
        identity_number=external or str(row.id),
        reference_number=phone or external or str(row.id),
        display_name=(row.full_name or "").strip() or external or str(row.id),
        phone=phone,
        email=email,
    )


class LocalCacheCustomerProvider:
    """Read-only lab provider backed by local ``customers`` cache table."""

    def __init__(self, session: Session, *, available: bool = True) -> None:
        self._session = session
        self._available = available

    def find_by_customer_number(self, customer_number: str) -> CustomerLookupResult:
        return self._search(customer_number)

    def find_by_national_id(self, national_id: str) -> CustomerLookupResult:
        return self._search(national_id)

    def find_by_reference_number(self, reference_number: str) -> CustomerLookupResult:
        return self._search(reference_number)

    def exists(self, customer_id: str) -> CustomerExistsResult:
        if not self._available:
            return CustomerExistsResult(
                status=CustomerLookupStatus.UNAVAILABLE, exists=False
            )
        row = self._get_by_id(customer_id)
        if row is None:
            return CustomerExistsResult(
                status=CustomerLookupStatus.NOT_FOUND, exists=False
            )
        return CustomerExistsResult(status=CustomerLookupStatus.FOUND, exists=True)

    def get_minimal_customer(self, customer_id: str) -> CustomerLookupResult:
        if not self._available:
            return CustomerLookupResult(status=CustomerLookupStatus.UNAVAILABLE)
        row = self._get_by_id(customer_id)
        if row is None:
            return CustomerLookupResult(status=CustomerLookupStatus.NOT_FOUND)
        minimal = _to_minimal(row)
        return CustomerLookupResult(
            status=CustomerLookupStatus.FOUND,
            customer=minimal,
            candidates=(minimal,),
        )

    def _get_by_id(self, customer_id: str) -> Customer | None:
        key = (customer_id or "").strip()
        if not key:
            return None
        try:
            import uuid as uuid_mod

            uid = uuid_mod.UUID(key)
            stmt = select(Customer).where(
                Customer.deleted_at.is_(None),
                Customer.id == uid,
            )
            found = self._session.scalars(stmt).first()
            if found is not None:
                return found
        except ValueError:
            pass

        stmt = select(Customer).where(
            Customer.deleted_at.is_(None),
            Customer.external_customer_id == key,
        )
        return self._session.scalars(stmt).first()

    def _search(self, raw: str) -> CustomerLookupResult:
        if not self._available:
            return CustomerLookupResult(status=CustomerLookupStatus.UNAVAILABLE)

        q = (raw or "").strip()
        if not q:
            return CustomerLookupResult(status=CustomerLookupStatus.NOT_FOUND)

        term = f"%{q}%"
        digits = _digits_only(q)
        name_filters = [
            Customer.full_name.ilike(f"{q}%"),
            Customer.full_name.ilike(f"% {q}%"),
        ]
        filters = [
            Customer.external_customer_id.ilike(term),
            Customer.phone.ilike(term),
            *name_filters,
        ]
        if digits and digits != q:
            filters.append(Customer.phone.ilike(f"%{digits}%"))
            filters.append(Customer.external_customer_id.ilike(f"%{digits}%"))

        stmt = (
            select(Customer)
            .where(Customer.deleted_at.is_(None), or_(*filters))
            .order_by(Customer.full_name.asc())
            # Lab / Mode A: allow large ambiguous name sets for intake pagination UX.
            .limit(150)
        )
        rows = list(self._session.scalars(stmt).all())
        if not rows:
            return CustomerLookupResult(status=CustomerLookupStatus.NOT_FOUND)

        candidates = tuple(_to_minimal(r) for r in rows)
        if len(candidates) > 1:
            return CustomerLookupResult(
                status=CustomerLookupStatus.AMBIGUOUS,
                candidates=candidates,
            )
        return CustomerLookupResult(
            status=CustomerLookupStatus.FOUND,
            customer=candidates[0],
            candidates=candidates,
        )
