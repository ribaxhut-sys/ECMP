"""Enterprise Platform Master Customer adapter (skeleton).

HTTP / auth / discovery are intentionally out of scope. Until wired, every
lookup returns ``UNAVAILABLE`` (Provider Temporarily Unavailable).
"""

from __future__ import annotations

from app.integrations.customer.types import (
    CustomerExistsResult,
    CustomerLookupResult,
    CustomerLookupStatus,
)


class EnterpriseCustomerProvider:
    """Future Enterprise Platform integration — same ``CustomerProvider`` surface.

    No HTTP calls. Selecting this adapter via ``CUSTOMER_PROVIDER=enterprise``
    yields normalized unavailability so business services stay transport-agnostic.
    """

    def __init__(self, *, base_url: str | None = None) -> None:
        # Reserved for future HTTP client configuration.
        self._base_url = base_url

    def find_by_customer_number(self, customer_number: str) -> CustomerLookupResult:
        _ = customer_number
        return self._unavailable()

    def find_by_national_id(self, national_id: str) -> CustomerLookupResult:
        _ = national_id
        return self._unavailable()

    def find_by_reference_number(self, reference_number: str) -> CustomerLookupResult:
        _ = reference_number
        return self._unavailable()

    def exists(self, customer_id: str) -> CustomerExistsResult:
        _ = customer_id
        return CustomerExistsResult(
            status=CustomerLookupStatus.UNAVAILABLE, exists=False
        )

    def get_minimal_customer(self, customer_id: str) -> CustomerLookupResult:
        _ = customer_id
        return self._unavailable()

    @staticmethod
    def _unavailable() -> CustomerLookupResult:
        return CustomerLookupResult(status=CustomerLookupStatus.UNAVAILABLE)
