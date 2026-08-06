"""Dependency-injection factory for ``CustomerProvider`` implementations."""

from __future__ import annotations

from typing import TYPE_CHECKING, Literal

from app.integrations.customer.enterprise_adapter import EnterpriseCustomerProvider
from app.integrations.customer.provider import CustomerProvider
from app.integrations.customer.stub_adapter import StubCustomerProvider

if TYPE_CHECKING:
    from sqlalchemy.orm import Session

CustomerProviderName = Literal["stub", "enterprise", "local"]


def build_customer_provider(
    name: CustomerProviderName | str = "stub",
    *,
    available: bool = True,
    enterprise_base_url: str | None = None,
    session: Session | None = None,
) -> CustomerProvider:
    """Construct the configured Master Customer provider.

    Defaults to the in-memory stub so Batch-1 behavior is unchanged.
    ``local`` reads the lab ``customers`` reference cache (not SoR).
    """
    key = (name or "stub").strip().lower()
    if key == "stub":
        return StubCustomerProvider(available=available)
    if key == "enterprise":
        return EnterpriseCustomerProvider(base_url=enterprise_base_url)
    if key == "local":
        if session is None:
            raise ValueError(
                "customer provider 'local' requires a SQLAlchemy session"
            )
        from app.integrations.customer.local_cache_adapter import (
            LocalCacheCustomerProvider,
        )

        return LocalCacheCustomerProvider(session, available=available)
    raise ValueError(
        "Unknown customer provider "
        f"'{name}'. Expected 'stub', 'enterprise', or 'local'."
    )
