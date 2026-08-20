"""Unit coverage for LocalCacheCustomerProvider + search-key / visibility helpers."""

from __future__ import annotations

import uuid
from collections.abc import Generator

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker

from app.core.authorization.principal import Principal
from app.db.base import Base
from app.integrations.customer.local_cache_adapter import LocalCacheCustomerProvider
from app.integrations.customer.types import CustomerLookupStatus
from app.models import Customer
from app.modules.cm_batch1.customer_search_key import validate_customer_search_key
from app.modules.cm_case.application.visibility import (
    CaseVisibilityClass,
    is_pusat_unit,
    resolve_case_visibility,
)
from app.modules.internal_complaint.application.visibility import (
    resolve_internal_visibility,
)


@pytest.fixture()
def db_session() -> Generator[Session, None, None]:
    engine = create_engine("sqlite:///:memory:", future=True)
    Base.metadata.create_all(engine, tables=[Customer.__table__])
    factory = sessionmaker(bind=engine, autoflush=False, autocommit=False, future=True)
    session = factory()
    try:
        yield session
    finally:
        session.close()
        engine.dispose()


def _seed_customer(
    session: Session,
    *,
    external_id: str,
    full_name: str,
    phone: str | None = None,
) -> Customer:
    row = Customer(
        id=uuid.uuid4(),
        external_customer_id=external_id,
        full_name=full_name,
        phone=phone,
        email=None,
    )
    session.add(row)
    session.commit()
    return row


def test_local_cache_search_found_and_exists(db_session: Session) -> None:
    row = _seed_customer(
        db_session,
        external_id="3200000000000099",
        full_name="Lab Cache User",
        phone="081234567890",
    )
    provider = LocalCacheCustomerProvider(db_session)

    by_number = provider.find_by_customer_number("3200000000000099")
    assert by_number.status == CustomerLookupStatus.FOUND
    assert by_number.customer is not None
    assert by_number.customer.display_name == "Lab Cache User"

    by_phone = provider.find_by_reference_number("081234567890")
    assert by_phone.status == CustomerLookupStatus.FOUND

    by_name = provider.find_by_national_id("Lab")
    assert by_name.status == CustomerLookupStatus.FOUND

    exists = provider.exists(str(row.id))
    assert exists.exists is True
    assert exists.status == CustomerLookupStatus.FOUND

    minimal = provider.get_minimal_customer(str(row.id))
    assert minimal.status == CustomerLookupStatus.FOUND
    assert minimal.customer is not None


def test_local_cache_unavailable_and_not_found(db_session: Session) -> None:
    down = LocalCacheCustomerProvider(db_session, available=False)
    assert down.find_by_customer_number("3200000000000099").status == (
        CustomerLookupStatus.UNAVAILABLE
    )
    assert down.exists("missing").exists is False
    assert down.get_minimal_customer("missing").status == (
        CustomerLookupStatus.UNAVAILABLE
    )

    up = LocalCacheCustomerProvider(db_session)
    assert up.find_by_customer_number("").status == CustomerLookupStatus.NOT_FOUND
    assert up.exists("not-a-uuid").exists is False
    assert up.get_minimal_customer(str(uuid.uuid4())).status == (
        CustomerLookupStatus.NOT_FOUND
    )


def test_local_cache_ambiguous_name(db_session: Session) -> None:
    _seed_customer(db_session, external_id="3200000000000001", full_name="Rina Satu")
    _seed_customer(db_session, external_id="3200000000000002", full_name="Rina Dua")
    provider = LocalCacheCustomerProvider(db_session)
    result = provider.find_by_customer_number("Rina")
    assert result.status == CustomerLookupStatus.AMBIGUOUS
    assert len(result.candidates) == 2


def test_customer_search_key_edges() -> None:
    assert validate_customer_search_key("").ok is False
    assert validate_customer_search_key("ab").ok is False
    assert validate_customer_search_key("abc").ok is True
    assert validate_customer_search_key("081234567").ok is False  # 9 digits
    phone = validate_customer_search_key("08123456789")
    assert phone.ok is True
    assert phone.kind == "phone"
    assert validate_customer_search_key("12345678").ok is True
    assert validate_customer_search_key("1234567").ok is False


def test_case_visibility_classes() -> None:
    assert is_pusat_unit(None) is False
    assert is_pusat_unit("PUSAT") is True
    assert is_pusat_unit("branch-x") is False

    admin = Principal(
        user_id=uuid.uuid4(),
        roles=("ADMIN",),
        permissions=frozenset({"*"}),
    )
    assert resolve_case_visibility(admin) == CaseVisibilityClass.ALL

    supervisor_pusat = Principal(
        user_id=uuid.uuid4(),
        roles=("SUPERVISOR",),
        permissions=frozenset({"complaints:read"}),
        org_unit_id="HO",
    )
    assert resolve_case_visibility(supervisor_pusat) == CaseVisibilityClass.PUSAT

    supervisor_branch = Principal(
        user_id=uuid.uuid4(),
        roles=("SUPERVISOR",),
        permissions=frozenset({"complaints:read"}),
        org_unit_id="UPPPD-TANAH-ABANG",
    )
    assert resolve_case_visibility(supervisor_branch) == CaseVisibilityClass.UNIT

    agent = Principal(
        user_id=uuid.uuid4(),
        roles=("AGENT",),
        permissions=frozenset({"complaints:read"}),
    )
    assert resolve_case_visibility(agent) == CaseVisibilityClass.SELF

    viewer = Principal(
        user_id=uuid.uuid4(),
        roles=("VIEWER",),
        permissions=frozenset({"complaints:read"}),
    )
    assert resolve_case_visibility(viewer) == CaseVisibilityClass.ALL
    assert resolve_internal_visibility(viewer) == CaseVisibilityClass.ALL

    ho_scheduler = Principal(
        user_id=uuid.uuid4(),
        roles=("HO_SCHEDULER",),
        permissions=frozenset({"complaints:read"}),
    )
    assert resolve_case_visibility(ho_scheduler) == CaseVisibilityClass.PUSAT
