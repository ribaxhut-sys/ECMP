"""S2 Task 05 — Master Customer CustomerProvider integration tests."""

from __future__ import annotations

import uuid
from typing import get_type_hints

import pytest
from fastapi.testclient import TestClient

from app.core.authorization.principal import Principal
from app.core.config import Settings
from app.core.errors import ValidationAppError
from app.integrations.customer import (
    CustomerLookupStatus,
    CustomerProvider,
    EnterpriseCustomerProvider,
    StubCustomerProvider,
    build_customer_provider,
    mask_identity,
)
from app.main import create_app
from app.modules.cm_batch1.enumeration import EnumerationGuard
from app.modules.cm_batch1.master_customer import MasterCustomerStub
from app.modules.cm_batch1.router import get_cm_batch1_service
from app.modules.cm_batch1.schemas import (
    CreateComplaintBatch1Request,
    CustomerSearchRequest,
)
from app.modules.cm_batch1.service import CmBatch1Service
from app.modules.cm_batch1.store import Batch1Store
from cm_batch1_helpers import confirmed_create

# ---------------------------------------------------------------------------
# Unit — contract surface
# ---------------------------------------------------------------------------


def test_stub_isinstance_customer_provider() -> None:
    assert isinstance(StubCustomerProvider(), CustomerProvider)


def test_enterprise_isinstance_customer_provider() -> None:
    assert isinstance(EnterpriseCustomerProvider(), CustomerProvider)


def test_mask_identity_batch1() -> None:
    assert mask_identity("ID-10000001") == "*******0001"
    assert mask_identity("AB") == "****"


# ---------------------------------------------------------------------------
# Provider — stub adapter
# ---------------------------------------------------------------------------


def test_stub_find_by_customer_number_found() -> None:
    provider = StubCustomerProvider()
    result = provider.find_by_customer_number("CN-10000001")
    assert result.status == CustomerLookupStatus.FOUND
    assert result.customer is not None
    assert result.customer.customer_id == "CUST-10001"


def test_stub_find_by_national_id_ambiguous() -> None:
    provider = StubCustomerProvider()
    result = provider.find_by_national_id("ID-AMBIG")
    assert result.status == CustomerLookupStatus.AMBIGUOUS
    assert len(result.candidates) == 2


def test_stub_find_by_reference_not_found() -> None:
    provider = StubCustomerProvider()
    result = provider.find_by_reference_number("REF-MISSING")
    assert result.status == CustomerLookupStatus.NOT_FOUND


def test_stub_exists_and_get_minimal() -> None:
    provider = StubCustomerProvider()
    assert provider.exists("CUST-10001").exists is True
    assert provider.exists("CUST-10001").status == CustomerLookupStatus.FOUND
    assert provider.exists("CUST-GONE").exists is False
    assert provider.exists("CUST-GONE").status == CustomerLookupStatus.NOT_FOUND

    lookup = provider.get_minimal_customer("CUST-10002")
    assert lookup.status == CustomerLookupStatus.FOUND
    assert lookup.customer is not None
    assert lookup.customer.display_name == "Synthetic Customer Two"


def test_stub_unavailable_normalized() -> None:
    provider = StubCustomerProvider(available=False)
    assert (
        provider.find_by_customer_number("CN-10000001").status
        == CustomerLookupStatus.UNAVAILABLE
    )
    assert provider.exists("CUST-10001").status == CustomerLookupStatus.UNAVAILABLE
    assert (
        provider.get_minimal_customer("CUST-10001").status
        == CustomerLookupStatus.UNAVAILABLE
    )


# ---------------------------------------------------------------------------
# Provider — enterprise skeleton
# ---------------------------------------------------------------------------


def test_enterprise_returns_unavailable() -> None:
    provider = EnterpriseCustomerProvider(base_url="https://example.invalid")
    assert (
        provider.find_by_customer_number("CN-10000001").status
        == CustomerLookupStatus.UNAVAILABLE
    )
    assert (
        provider.find_by_national_id("ID-10000001").status
        == CustomerLookupStatus.UNAVAILABLE
    )
    assert (
        provider.find_by_reference_number("REF-10000001").status
        == CustomerLookupStatus.UNAVAILABLE
    )
    assert provider.exists("CUST-10001").status == CustomerLookupStatus.UNAVAILABLE
    assert (
        provider.get_minimal_customer("CUST-10001").status
        == CustomerLookupStatus.UNAVAILABLE
    )


# ---------------------------------------------------------------------------
# Factory / DI
# ---------------------------------------------------------------------------


def test_factory_default_stub() -> None:
    provider = build_customer_provider()
    assert isinstance(provider, StubCustomerProvider)
    assert (
        provider.find_by_customer_number("CN-10000001").status
        == CustomerLookupStatus.FOUND
    )


def test_factory_enterprise() -> None:
    provider = build_customer_provider("enterprise")
    assert isinstance(provider, EnterpriseCustomerProvider)
    assert (
        provider.find_by_customer_number("CN-10000001").status
        == CustomerLookupStatus.UNAVAILABLE
    )


def test_factory_unknown_raises() -> None:
    with pytest.raises(ValueError, match="Unknown customer provider"):
        build_customer_provider("kafka")


def test_settings_customer_provider_default() -> None:
    settings = Settings()
    assert settings.customer_provider == "stub"
    assert settings.customer_provider_enterprise_base_url is None


def test_di_swappable_without_business_code_change() -> None:
    store = Batch1Store()
    store.reset()
    stub_svc = CmBatch1Service(
        customer_provider=build_customer_provider("stub"),
        guard=EnumerationGuard(),
        store=store,
    )
    result = stub_svc.search_customer(
        CustomerSearchRequest(customerNumber="CN-10000001"),
        principal_key="di-1",
    )
    assert result.verification_status == "verified"

    enterprise_svc = CmBatch1Service(
        customer_provider=build_customer_provider("enterprise"),
        guard=EnumerationGuard(),
        store=store,
        strict_master=True,
    )
    with pytest.raises(ValidationAppError, match="tidak tersedia"):
        enterprise_svc.search_customer(
            CustomerSearchRequest(customerNumber="CN-10000001"),
            principal_key="di-2",
        )


def test_service_constructor_accepts_customer_provider() -> None:
    hints = get_type_hints(CmBatch1Service.__init__)
    assert "customer_provider" in hints
    assert hints["customer_provider"] == CustomerProvider | None


# ---------------------------------------------------------------------------
# Regression — complaint registration unchanged via provider
# ---------------------------------------------------------------------------


def test_regression_create_still_works_with_provider() -> None:
    store = Batch1Store()
    store.reset()
    svc = CmBatch1Service(
        customer_provider=StubCustomerProvider(),
        guard=EnumerationGuard(),
        store=store,
    )
    created = confirmed_create(svc,
        CreateComplaintBatch1Request(
            customerId="CUST-10001",
            category="BILLING",
            channel="WEB",
            subject="Provider regression subject line",
            description="Regression description for master customer provider.",
        ),
        request_id="s2-t05-reg-1",
        channel_message_id=None,
        actor_id="tester",
    )
    assert created.complaint_id
    assert created.case_created is False
    assert created.replayed is False


def test_regression_shim_master_customer_stub_still_constructible() -> None:
    """Transitional alias remains for older imports."""
    stub = MasterCustomerStub()
    assert stub.get("CUST-10001") is not None
    assert stub.search(customer_number="CN-10000001")[0].customer_id == "CUST-10001"


def test_router_wires_provider_override() -> None:
    app = create_app()
    store = Batch1Store()
    store.reset()

    def _override() -> CmBatch1Service:
        return CmBatch1Service(
            customer_provider=build_customer_provider("stub"),
            store=store,
            guard=EnumerationGuard(),
        )

    app.dependency_overrides[get_cm_batch1_service] = _override

    async def _principal() -> Principal:
        return Principal(
            user_id=uuid.uuid4(),
            roles=("AGENT",),
            permissions=frozenset({"complaints:read", "complaints:create", "*"}),
        )

    from app.core.authorization.authentication import get_current_principal

    app.dependency_overrides[get_current_principal] = _principal
    with TestClient(app) as client:
        response = client.post(
            "/api/v1/cm/customers/search",
            json={"customerNumber": "CN-10000001"},
        )
    app.dependency_overrides.clear()
    assert response.status_code == 200
    assert response.json()["data"]["verificationStatus"] == "verified"
