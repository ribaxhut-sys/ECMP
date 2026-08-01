"""CustomerProvider contract — business services never call HTTP/DB directly."""

from __future__ import annotations

from typing import Protocol, runtime_checkable

from app.integrations.customer.types import (
    CustomerExistsResult,
    CustomerLookupResult,
)


@runtime_checkable
class CustomerProvider(Protocol):
    """Read-only Master Customer integration surface for CM Batch 1."""

    def find_by_customer_number(self, customer_number: str) -> CustomerLookupResult:
        """Locate by customer number (exactly one key)."""

    def find_by_national_id(self, national_id: str) -> CustomerLookupResult:
        """Locate by national / identity number (exactly one key)."""

    def find_by_reference_number(self, reference_number: str) -> CustomerLookupResult:
        """Locate by external reference number (exactly one key)."""

    def exists(self, customer_id: str) -> CustomerExistsResult:
        """Whether a customer id is known to Master Customer."""

    def get_minimal_customer(self, customer_id: str) -> CustomerLookupResult:
        """Fetch Batch-1 minimal profile by customer id."""
