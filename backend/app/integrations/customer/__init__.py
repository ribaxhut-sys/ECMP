"""Master Customer integration — read-only (ADR-002; ECMP is not SoR).

Business services depend only on ``CustomerProvider``. Adapters are swappable
via ``CUSTOMER_PROVIDER`` (``stub`` | ``enterprise`` | ``local``).
"""

from __future__ import annotations

from app.integrations.customer.enterprise_adapter import EnterpriseCustomerProvider
from app.integrations.customer.factory import build_customer_provider
from app.integrations.customer.local_cache_adapter import LocalCacheCustomerProvider
from app.integrations.customer.masking import mask_identity
from app.integrations.customer.provider import CustomerProvider
from app.integrations.customer.stub_adapter import StubCustomerProvider
from app.integrations.customer.types import (
    CustomerExistsResult,
    CustomerLookupResult,
    CustomerLookupStatus,
    MinimalCustomer,
)

__all__ = [
    "CustomerExistsResult",
    "CustomerLookupResult",
    "CustomerLookupStatus",
    "CustomerProvider",
    "EnterpriseCustomerProvider",
    "LocalCacheCustomerProvider",
    "MinimalCustomer",
    "StubCustomerProvider",
    "build_customer_provider",
    "mask_identity",
]
