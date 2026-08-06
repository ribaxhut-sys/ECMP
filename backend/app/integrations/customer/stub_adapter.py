"""In-memory Master Customer stub adapter (ADR-002 — not SoR).

Preserves prior ``MasterCustomerStub`` seed and search semantics.
"""

from __future__ import annotations

from app.integrations.customer.types import (
    CustomerExistsResult,
    CustomerLookupResult,
    CustomerLookupStatus,
    MinimalCustomer,
)

# Synthetic seed only — never real PII.
_SEED: tuple[MinimalCustomer, ...] = (
    MinimalCustomer(
        customer_id="CUST-10001",
        customer_number="CN-10000001",
        identity_number="ID-10000001",
        reference_number="REF-10000001",
        display_name="Synthetic Customer One",
    ),
    MinimalCustomer(
        customer_id="CUST-10002",
        customer_number="CN-10000002",
        identity_number="ID-10000002",
        reference_number="REF-10000002",
        display_name="Synthetic Customer Two",
    ),
    # Ambiguous identity shared by two records when searching a special key.
    MinimalCustomer(
        customer_id="CUST-AMB-A",
        customer_number="CN-AMB-A",
        identity_number="ID-AMBIG",
        reference_number="REF-AMB-A",
        display_name="Ambiguous A",
    ),
    MinimalCustomer(
        customer_id="CUST-AMB-B",
        customer_number="CN-AMB-B",
        identity_number="ID-AMBIG",
        reference_number="REF-AMB-B",
        display_name="Ambiguous B",
    ),
)


class StubCustomerProvider:
    """Read-only stub. Write-back is forbidden. Default Batch-1 provider."""

    def __init__(self, *, available: bool = True) -> None:
        self._available = available
        self._records = list(_SEED)

    def find_by_customer_number(self, customer_number: str) -> CustomerLookupResult:
        return self._search(customer_number=customer_number)

    def find_by_national_id(self, national_id: str) -> CustomerLookupResult:
        return self._search(identity_number=national_id)

    def find_by_reference_number(self, reference_number: str) -> CustomerLookupResult:
        return self._search(reference_number=reference_number)

    def exists(self, customer_id: str) -> CustomerExistsResult:
        if not self._available:
            return CustomerExistsResult(
                status=CustomerLookupStatus.UNAVAILABLE, exists=False
            )
        found = any(r.customer_id == customer_id for r in self._records)
        if found:
            return CustomerExistsResult(
                status=CustomerLookupStatus.FOUND, exists=True
            )
        return CustomerExistsResult(
            status=CustomerLookupStatus.NOT_FOUND, exists=False
        )

    def get_minimal_customer(self, customer_id: str) -> CustomerLookupResult:
        if not self._available:
            return CustomerLookupResult(status=CustomerLookupStatus.UNAVAILABLE)
        for row in self._records:
            if row.customer_id == customer_id:
                return CustomerLookupResult(
                    status=CustomerLookupStatus.FOUND, customer=row
                )
        return CustomerLookupResult(status=CustomerLookupStatus.NOT_FOUND)

    def _search(
        self,
        *,
        customer_number: str | None = None,
        identity_number: str | None = None,
        reference_number: str | None = None,
    ) -> CustomerLookupResult:
        if not self._available:
            return CustomerLookupResult(status=CustomerLookupStatus.UNAVAILABLE)

        matches: list[MinimalCustomer] = []
        if customer_number:
            matches = [r for r in self._records if r.customer_number == customer_number]
        elif identity_number:
            matches = [r for r in self._records if r.identity_number == identity_number]
        elif reference_number:
            matches = [
                r for r in self._records if r.reference_number == reference_number
            ]

        if not matches:
            return CustomerLookupResult(status=CustomerLookupStatus.NOT_FOUND)
        if len(matches) > 1:
            return CustomerLookupResult(
                status=CustomerLookupStatus.AMBIGUOUS,
                candidates=tuple(matches),
            )
        return CustomerLookupResult(
            status=CustomerLookupStatus.FOUND,
            customer=matches[0],
            candidates=(matches[0],),
        )
