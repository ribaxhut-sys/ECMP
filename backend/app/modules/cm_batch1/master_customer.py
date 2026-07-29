"""Compatibility shim — prefer ``app.integrations.customer``.

Keeps historic imports working while Batch-1 services depend only on
``CustomerProvider``.
"""

from __future__ import annotations

from datetime import UTC, datetime

from app.integrations.customer.masking import mask_identity as _mask_identity
from app.integrations.customer.stub_adapter import StubCustomerProvider
from app.integrations.customer.types import (
    CustomerLookupStatus,
    MinimalCustomer,
)

# Historic type alias
MasterCustomerRecord = MinimalCustomer


class MasterCustomerStub(StubCustomerProvider):
    """Deprecated name for ``StubCustomerProvider`` (tests / transitional)."""

    @property
    def available(self) -> bool:
        return self._available

    @available.setter
    def available(self, value: bool) -> None:
        self._available = value

    def search(
        self,
        *,
        customer_number: str | None = None,
        identity_number: str | None = None,
        reference_number: str | None = None,
    ) -> list[MinimalCustomer]:
        """Legacy multi-key search used by older call sites."""
        if customer_number:
            result = self.find_by_customer_number(customer_number)
        elif identity_number:
            result = self.find_by_national_id(identity_number)
        elif reference_number:
            result = self.find_by_reference_number(reference_number)
        else:
            return []
        if result.status == CustomerLookupStatus.UNAVAILABLE:
            return []
        if result.status == CustomerLookupStatus.AMBIGUOUS:
            return list(result.candidates)
        if result.status == CustomerLookupStatus.FOUND and result.customer:
            return [result.customer]
        return []

    def get(self, customer_id: str) -> MinimalCustomer | None:
        result = self.get_minimal_customer(customer_id)
        if result.status == CustomerLookupStatus.FOUND:
            return result.customer
        return None

    @staticmethod
    def mask_identity(value: str) -> str:
        return _mask_identity(value)

    @staticmethod
    def now() -> datetime:
        return datetime.now(UTC)


mask_identity = _mask_identity


def now() -> datetime:
    return datetime.now(UTC)


__all__ = [
    "MasterCustomerRecord",
    "MasterCustomerStub",
    "mask_identity",
    "now",
]
