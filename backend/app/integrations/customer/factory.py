"""Dependency-injection factory for ``CustomerProvider`` implementations."""

from __future__ import annotations

from typing import Literal

from app.integrations.customer.enterprise_adapter import EnterpriseCustomerProvider
from app.integrations.customer.provider import CustomerProvider
from app.integrations.customer.stub_adapter import StubCustomerProvider

CustomerProviderName = Literal["stub", "enterprise"]


def build_customer_provider(
    name: CustomerProviderName | str = "stub",
    *,
    available: bool = True,
    enterprise_base_url: str | None = None,
) -> CustomerProvider:
    """Construct the configured Master Customer provider.

    Defaults to the in-memory stub so Batch-1 behavior is unchanged.
    """
    key = (name or "stub").strip().lower()
    if key == "stub":
        return StubCustomerProvider(available=available)
    if key == "enterprise":
        return EnterpriseCustomerProvider(base_url=enterprise_base_url)
    raise ValueError(
        f"Unknown customer provider '{name}'. Expected 'stub' or 'enterprise'."
    )
