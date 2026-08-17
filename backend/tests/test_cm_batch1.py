"""CM Batch 1 — FR-001 / FR-002 / FR-003 (unit + API + S2 persistence)."""

from __future__ import annotations

import uuid
from collections.abc import Generator
from pathlib import Path

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker

from app.core.authorization.principal import Principal
from app.core.errors import (
    InvalidStateError,
    NotFoundError,
    RateLimitedError,
    ValidationAppError,
)
from app.db.base import Base
from app.integrations.customer import StubCustomerProvider
from app.main import create_app
from app.modules.cm_batch1.duplicate_config import DuplicateConfig
from app.modules.cm_batch1.duplicate_engine import score_candidate, subject_similarity
from app.modules.cm_batch1.entities import ComplaintAggregate
from app.modules.cm_batch1.enumeration import EnumerationGuard
from app.modules.cm_batch1.models import (
    CmBatch1ChannelMessageORM,
    CmBatch1ComplaintORM,
    CmBatch1CustomerLockORM,
    CmBatch1DuplicateDecisionORM,
    CmBatch1IdempotencyORM,
    CmBatch1LaterReviewItemORM,
    CmBatch1NumberCounterORM,
)
from app.modules.cm_batch1.repository import CmBatch1Repository
from app.modules.cm_batch1.router import get_cm_batch1_service
from app.modules.cm_batch1.schemas import (
    CreateComplaintBatch1Request,
    CustomerSearchRequest,
    DuplicateCheckRequest,
    DuplicateDecisionRequest,
    IntakeEscalationDecisionRequest,
)
from app.modules.cm_batch1.service import CmBatch1Service
from app.modules.cm_batch1.store import Batch1Store
from cm_batch1_helpers import confirmed_create

_BATCH1_TABLES = [
    CmBatch1ComplaintORM.__table__,
    CmBatch1IdempotencyORM.__table__,
    CmBatch1ChannelMessageORM.__table__,
    CmBatch1CustomerLockORM.__table__,
    CmBatch1NumberCounterORM.__table__,
    CmBatch1DuplicateDecisionORM.__table__,
    CmBatch1LaterReviewItemORM.__table__,
]


@pytest.fixture()
def store() -> Batch1Store:
    s = Batch1Store()
    s.reset()
    return s


@pytest.fixture()
def service(store: Batch1Store) -> CmBatch1Service:
    return CmBatch1Service(
        customer_provider=StubCustomerProvider(),
        guard=EnumerationGuard(max_failures=3, window_seconds=60, block_seconds=30),
        store=store,
    )


@pytest.fixture()
def db_session() -> Generator[Session, None, None]:
    engine = create_engine("sqlite:///:memory:", future=True)
    Base.metadata.create_all(engine, tables=_BATCH1_TABLES)
    factory = sessionmaker(bind=engine, autoflush=False, autocommit=False, future=True)
    session = factory()
    try:
        yield session
    finally:
        session.close()
        engine.dispose()


@pytest.fixture()
def persistent_service(db_session: Session) -> CmBatch1Service:
    return CmBatch1Service(
        customer_provider=StubCustomerProvider(),
        guard=EnumerationGuard(max_failures=3, window_seconds=60, block_seconds=30),
        store=CmBatch1Repository(db_session),
    )


def test_tc_cm_fr002_01_unique_customer_number(service: CmBatch1Service) -> None:
    result = service.search_customer(
        CustomerSearchRequest(customerNumber="CN-10000001"),
        principal_key="p1",
    )
    assert result.verification_status == "verified"
    assert result.customer_id == "CUST-10001"
    assert result.enumeration_outcome == "allowed"


def test_customer_search_rejects_short_id(service: CmBatch1Service) -> None:
    with pytest.raises(ValidationAppError) as exc:
        service.search_customer(
            CustomerSearchRequest(customerNumber="32"),
            principal_key="p-short-id",
        )
    assert "8" in exc.value.message or "pendek" in exc.value.message.lower()


def test_customer_search_rejects_short_phone(service: CmBatch1Service) -> None:
    with pytest.raises(ValidationAppError) as exc:
        service.search_customer(
            CustomerSearchRequest(customerNumber="0833"),
            principal_key="p-short-phone",
        )
    assert "10" in exc.value.message or "telepon" in exc.value.message.lower()


def test_tc_cm_fr002_02_ambiguous_no_lock(service: CmBatch1Service) -> None:
    result = service.search_customer(
        CustomerSearchRequest(identityNumber="ID-AMBIG"),
        principal_key="p1",
    )
    assert result.verification_status == "ambiguous"
    assert result.customer_id is None
    assert len(result.candidates) == 2


def test_tc_cm_fr002_03_not_found(service: CmBatch1Service) -> None:
    result = service.search_customer(
        CustomerSearchRequest(customerNumber="CN-MISSING"),
        principal_key="p1",
    )
    assert result.verification_status == "not_found"


def test_tc_cm_fr002_04_write_back_rejected(service: CmBatch1Service) -> None:
    with pytest.raises(ValidationAppError) as exc:
        service.reject_master_write_back()
    assert "write-back" in exc.value.message.lower() or "forbidden" in exc.value.message.lower()


def test_tc_cm_fr002_05_strict_unavailable(store: Batch1Store) -> None:
    svc = CmBatch1Service(
        customer_provider=StubCustomerProvider(available=False),
        guard=EnumerationGuard(),
        store=store,
        strict_master=True,
    )
    with pytest.raises(ValidationAppError):
        svc.search_customer(
            CustomerSearchRequest(customerNumber="CN-10000001"),
            principal_key="p1",
        )


def test_tc_cm_fr002_07_two_keys_rejected(service: CmBatch1Service) -> None:
    with pytest.raises(ValidationAppError) as exc:
        service.search_customer(
            CustomerSearchRequest(customerNumber="CN-10000001", identityNumber="ID-10000001"),
            principal_key="p1",
        )
    assert "Tepat satu" in exc.value.message


def test_tc_cm_fr002_08_enumeration_blocks(service: CmBatch1Service) -> None:
    for _ in range(3):
        service.search_customer(
            CustomerSearchRequest(customerNumber="CN-MISSING"),
            principal_key="attacker",
        )
    with pytest.raises(RateLimitedError) as exc:
        service.search_customer(
            CustomerSearchRequest(customerNumber="CN-MISSING"),
            principal_key="attacker",
        )
    assert exc.value.details is not None
    assert exc.value.details.get("enumerationOutcome") in {"blocked", "alerted"}


def test_tc_cm_fr002_09_as_of_present(service: CmBatch1Service) -> None:
    result = service.search_customer(
        CustomerSearchRequest(customerNumber="CN-10000001"),
        principal_key="p1",
    )
    assert result.as_of is not None
    view = service.customer_360_minimum("CUST-10001")
    assert view.as_of is not None
    assert view.complaint_count == 0
    assert "displayName" in view.profile


def test_tc_cm_fr001_confirm_lock_required_on_create(
    service: CmBatch1Service,
) -> None:
    """TD-CM-001 / EX-D / FR-002 AC1 — create without confirm is rejected."""
    with pytest.raises(ValidationAppError, match="dikonfirmasi/dikunci"):
        service.create_complaint(
            CreateComplaintBatch1Request(
                customerId="CUST-10001",
                category="BILLING",
                channel="BRANCH",
                subject="No lock",
                description="Desc",
            ),
            request_id="req-lock-1",
            channel_message_id=None,
            actor_id="actor-lock",
            principal_key="actor-lock",
        )


def test_tc_cm_fr001_01_create_registered_no_case(service: CmBatch1Service) -> None:
    created = confirmed_create(service,
        CreateComplaintBatch1Request(
            customerId="CUST-10001",
            category="BILLING",
            channel="BRANCH",
            subject="Test subject",
            description="Test description",
        ),
        request_id="req-1",
        channel_message_id=None,
        actor_id="actor-1",
    )
    assert created.status == "REGISTERED"
    assert created.case_created is False
    assert created.complaint_number.count("-") == 2
    unit, yymm, seq = created.complaint_number.split("-")
    assert len(unit) == 3 and unit.isalpha()
    assert len(yymm) == 4 and yymm.isdigit()
    assert seq.isdigit() and int(seq) >= 1


def test_create_complaint_number_format_b_tanah_abang(service: CmBatch1Service) -> None:
    created = confirmed_create(
        service,
        CreateComplaintBatch1Request(
            customerId="CUST-10001",
            category="BILLING",
            channel="BRANCH",
            subject="Format B",
            description="Nomor unit-bulan",
            recordingUnitId="UPPPD-TANAH-ABANG",
        ),
        request_id="req-format-b-tab",
        channel_message_id=None,
        actor_id="actor-1",
    )
    assert created.complaint_number.startswith("TAB-")
    _, yymm, seq = created.complaint_number.split("-")
    assert len(yymm) == 4 and yymm.isdigit()
    assert seq == "0001"

    second = confirmed_create(
        service,
        CreateComplaintBatch1Request(
            customerId="CUST-10002",
            category="BILLING",
            channel="BRANCH",
            subject="Format B 2",
            description="Seq naik",
            recordingUnitId="UPPPD-TANAH-ABANG",
        ),
        request_id="req-format-b-tab-2",
        channel_message_id=None,
        actor_id="actor-1",
    )
    assert second.complaint_number.startswith("TAB-")
    assert second.complaint_number.split("-")[2] == "0002"


def test_create_branch_closed_without_case(service: CmBatch1Service) -> None:
    created = confirmed_create(
        service,
        CreateComplaintBatch1Request(
            customerId="CUST-10001",
            category="BILLING",
            channel="BRANCH",
            subject="Walk-in resolved",
            description="Keluhan singkat\n\n---\nPenyelesaian:\nSudah diganti",
            intakeDisposition="BRANCH_CLOSED",
        ),
        request_id="req-branch-closed",
        channel_message_id=None,
        actor_id="actor-1",
    )
    assert created.status == "CLOSED"
    assert created.case_created is False
    assert created.priority == "MEDIUM"


def test_create_branch_closed_requires_resolution(service: CmBatch1Service) -> None:
    from app.core.errors import ValidationAppError

    try:
        confirmed_create(
            service,
            CreateComplaintBatch1Request(
                customerId="CUST-10001",
                category="BILLING",
                channel="BRANCH",
                subject="No resolution",
                description="Keluhan tanpa penyelesaian",
                intakeDisposition="BRANCH_CLOSED",
            ),
            request_id="req-branch-closed-bad",
            channel_message_id=None,
            actor_id="actor-1",
        )
        raise AssertionError("expected ValidationAppError")
    except ValidationAppError as exc:
        assert "note" in str(exc).lower() or "BRANCH_CLOSED" in str(
            getattr(exc, "details", {})
        ) or "Catatan" in str(getattr(exc, "details", {}))


def test_create_escalate_requires_escalation_reason(
    service: CmBatch1Service,
) -> None:
    from app.core.errors import ValidationAppError

    try:
        confirmed_create(
            service,
            CreateComplaintBatch1Request(
                customerId="CUST-10001",
                category="BILLING",
                channel="BRANCH",
                subject="No escalation reason",
                description="Keluhan tanpa alasan eskalasi",
                intakeDisposition="ESCALATE_PENDING_APPROVAL",
            ),
            request_id="req-escalate-missing-reason",
            channel_message_id=None,
            actor_id="actor-1",
        )
        raise AssertionError("expected ValidationAppError")
    except ValidationAppError as exc:
        assert "escalation reason" in str(exc).lower() or "Alasan eskalasi" in str(
            getattr(exc, "details", {})
        )


def test_tc_cm_fr001_02_customer_id_only(service: CmBatch1Service) -> None:
    created = confirmed_create(service,
        CreateComplaintBatch1Request(
            customerId="CUST-10001",
            category="BILLING",
            channel="BRANCH",
            subject="Sub",
            description="Desc",
        ),
        request_id="req-2",
        channel_message_id=None,
        actor_id="actor-1",
    )
    dumped = created.model_dump(by_alias=True)
    assert dumped["customerId"] == "CUST-10001"
    assert "fullName" not in dumped
    assert "identityNumber" not in dumped


def test_tc_cm_fr001_04_missing_fields(service: CmBatch1Service) -> None:
    with pytest.raises(ValidationAppError):
        confirmed_create(service,
            CreateComplaintBatch1Request(
                customerId="CUST-10001",
                category="",
                channel="BRANCH",
                subject="Sub",
                description="Desc",
            ),
            request_id="req-3",
            channel_message_id=None,
            actor_id="a",
        )


def test_tc_cm_fr001_08_strict_master_unavailable_create_rejected(
    store: Batch1Store,
) -> None:
    """AC-CM-FR001-08 — strict mode + Master Customer down at create time → reject.

    Customer is confirmed/locked while Master Customer is reachable (mirrors
    a real sequence: search + confirm succeed, then Master Customer goes down
    before the create call lands). ``create_complaint`` re-checks existence
    via ``self._customers.exists(...)`` (service.py ~L723) and must reject
    when that check reports UNAVAILABLE under strict_master — it must not
    silently fall back to the already-confirmed lock.
    """
    provider = StubCustomerProvider()
    svc = CmBatch1Service(
        customer_provider=provider,
        guard=EnumerationGuard(max_failures=3, window_seconds=60, block_seconds=30),
        store=store,
        strict_master=True,
    )
    svc.confirm_customer("CUST-10001", principal_key="actor-strict")

    provider._available = False  # Master Customer goes down after confirm.

    with pytest.raises(ValidationAppError) as exc:
        svc.create_complaint(
            CreateComplaintBatch1Request(
                customerId="CUST-10001",
                category="BILLING",
                channel="BRANCH",
                subject="Strict reject",
                description="Master Customer unavailable at create",
            ),
            request_id="req-strict-1",
            channel_message_id=None,
            actor_id="actor-strict",
            principal_key="actor-strict",
        )
    assert "Strict" in exc.value.message
    assert "ditolak" in exc.value.message


def test_tc_cm_fr001_10_request_id_replay(service: CmBatch1Service) -> None:
    first = confirmed_create(service,
        CreateComplaintBatch1Request(
            customerId="CUST-10001",
            category="BILLING",
            channel="BRANCH",
            subject="Sub",
            description="Desc",
        ),
        request_id="same-req",
        channel_message_id=None,
        actor_id="a",
    )
    second = confirmed_create(service,
        CreateComplaintBatch1Request(
            customerId="CUST-10001",
            category="BILLING",
            channel="BRANCH",
            subject="Sub changed",
            description="Desc",
        ),
        request_id="same-req",
        channel_message_id=None,
        actor_id="a",
    )
    assert second.replayed is True
    assert second.complaint_id == first.complaint_id
    assert second.case_created is False


def test_tc_cm_fr001_11_channel_message_replay(service: CmBatch1Service) -> None:
    first = confirmed_create(service,
        CreateComplaintBatch1Request(
            customerId="CUST-10001",
            category="BILLING",
            channel="CHANNEL",
            subject="Sub",
            description="Desc",
        ),
        request_id="req-ch-1",
        channel_message_id="MSG-9",
        actor_id="a",
    )
    second = confirmed_create(service,
        CreateComplaintBatch1Request(
            customerId="CUST-10001",
            category="BILLING",
            channel="CHANNEL",
            subject="Other",
            description="Desc",
        ),
        request_id="req-ch-2",
        channel_message_id="MSG-9",
        actor_id="a",
    )
    assert second.complaint_id == first.complaint_id
    assert second.replayed is True


def test_tc_cm_fr001_12_360_after_create(service: CmBatch1Service) -> None:
    confirmed_create(service,
        CreateComplaintBatch1Request(
            customerId="CUST-10001",
            category="BILLING",
            channel="BRANCH",
            subject="Sub",
            description="Desc",
        ),
        request_id="req-360",
        channel_message_id=None,
        actor_id="a",
    )
    view = service.customer_360_minimum("CUST-10001")
    assert view.complaint_count == 1
    assert len(view.active_complaints) == 1
    assert len(view.complaint_history) == 1
    assert view.complaint_history[0]["complaintNumber"]


# --- API smoke (auth override) ---


@pytest.fixture()
def api_client(service: CmBatch1Service) -> Generator[TestClient, None, None]:
    app = create_app()
    app.dependency_overrides[get_cm_batch1_service] = lambda: service

    class _NoOpAttachments:
        def bind_staging_to_complaint(self, **kwargs):  # type: ignore[no-untyped-def]
            return []

        def transfer(self, body, *, actor_id=None):  # type: ignore[no-untyped-def]
            from app.modules.cm_batch1.schemas import TransferAttachmentsResponse

            return TransferAttachmentsResponse(
                stagingToken=body.staging_token,
                survivingComplaintId=body.surviving_complaint_id,
                transferredCount=0,
                attachments=[],
                discarded=False,
            )

    from app.modules.cm_batch1.router import get_cm_batch1_attachment_service

    app.dependency_overrides[get_cm_batch1_attachment_service] = lambda: _NoOpAttachments()

    async def _principal() -> Principal:
        return Principal(
            user_id=uuid.UUID("11111111-1111-1111-1111-111111111111"),
            roles=("AGENT",),
            permissions=frozenset({"complaints:read", "complaints:create", "*"}),
        )

    from app.core.authorization.authentication import get_current_principal

    app.dependency_overrides[get_current_principal] = _principal
    with TestClient(app) as client:
        yield client
    app.dependency_overrides.clear()


def test_api_search_and_create_roundtrip(api_client: TestClient) -> None:
    search = api_client.post(
        "/api/v1/cm/customers/search",
        json={"customerNumber": "CN-10000001"},
    )
    assert search.status_code == 200, search.text
    body = search.json()["data"]
    assert body["customerId"] == "CUST-10001"

    confirm = api_client.post(
        "/api/v1/cm/customers/confirm",
        json={"customerId": "CUST-10001"},
    )
    assert confirm.status_code == 200, confirm.text
    assert confirm.json()["data"]["locked"] is True

    created = api_client.post(
        "/api/v1/cm/complaints",
        headers={"Idempotency-Key": "api-req-1"},
        json={
            "customerId": "CUST-10001",
            "category": "BILLING",
            "channel": "BRANCH",
            "subject": "API create",
            "description": "desc\n\n---\nCatatan:\nCatatan lab",
        },
    )
    assert created.status_code == 201, created.text
    data = created.json()["data"]
    assert data["status"] == "REGISTERED"
    assert data["caseCreated"] is False

    replay = api_client.post(
        "/api/v1/cm/complaints",
        headers={"Idempotency-Key": "api-req-1"},
        json={
            "customerId": "CUST-10001",
            "category": "BILLING",
            "channel": "BRANCH",
            "subject": "API create",
            "description": "desc\n\n---\nCatatan:\nCatatan lab",
        },
    )
    assert replay.status_code == 200, replay.text
    assert replay.json()["data"]["complaintId"] == data["complaintId"]
    assert replay.json()["data"]["replayed"] is True

    listed = api_client.get("/api/v1/cm/complaints?page=1&pageSize=20")
    assert listed.status_code == 200, listed.text
    list_body = listed.json()
    assert list_body["meta"]["page"] == 1
    assert list_body["meta"]["pageSize"] == 20
    assert list_body["meta"]["totalItems"] >= 1
    assert any(row["complaintId"] == data["complaintId"] for row in list_body["data"])

    by_kw = api_client.get("/api/v1/cm/complaints?keyword=API%20create")
    assert by_kw.status_code == 200, by_kw.text
    assert any(row["complaintId"] == data["complaintId"] for row in by_kw.json()["data"])

    by_pri = api_client.get("/api/v1/cm/complaints?priority=MEDIUM")
    assert by_pri.status_code == 200, by_pri.text
    assert by_pri.json()["meta"]["totalItems"] >= 1

    by_cat = api_client.get("/api/v1/cm/complaints?category=BILLING")
    assert by_cat.status_code == 200, by_cat.text
    assert any(row["complaintId"] == data["complaintId"] for row in by_cat.json()["data"])

    miss = api_client.get("/api/v1/cm/complaints?keyword=zzznomatch999")
    assert miss.status_code == 200, miss.text
    assert miss.json()["meta"]["totalItems"] == 0


@pytest.fixture()
def api_client_unauthorized(service: CmBatch1Service) -> Generator[TestClient, None, None]:
    """Same wiring as ``api_client``, but the principal lacks complaints:create.

    AC-CM-FR001-05 — "Unauthorized -> reject + security audit". This exercises
    the real ``require_permissions("complaints:create")`` dependency instead
    of a hand-rolled check, matching the pattern the router actually uses.
    """
    app = create_app()
    app.dependency_overrides[get_cm_batch1_service] = lambda: service

    async def _principal() -> Principal:
        return Principal(
            user_id=uuid.UUID("22222222-2222-2222-2222-222222222222"),
            roles=("VIEWER",),
            permissions=frozenset({"complaints:read"}),  # no complaints:create
        )

    from app.core.authorization.authentication import get_current_principal

    app.dependency_overrides[get_current_principal] = _principal
    with TestClient(app) as client:
        yield client
    app.dependency_overrides.clear()


def test_tc_cm_fr001_05_unauthorized_create_rejected(
    api_client_unauthorized: TestClient,
) -> None:
    """AC-CM-FR001-05 — principal without complaints:create is rejected (API-500).

    HTTP-layer assertion only; the security-audit-row assertion is a separate
    test gated on a real Postgres connection (see
    ``test_tc_cm_fr001_05_unauthorized_create_writes_security_audit`` below) —
    ``write_security_event`` never raises to the caller (by design, see
    app/modules/audit/security_events.py), so the 403 here is verifiable in
    any environment regardless of whether the audit write itself succeeds.
    """
    response = api_client_unauthorized.post(
        "/api/v1/cm/complaints",
        headers={"Idempotency-Key": "api-req-unauthz-1"},
        json={
            "customerId": "CUST-10001",
            "category": "BILLING",
            "channel": "BRANCH",
            "subject": "Should be rejected",
            "description": "No complaints:create permission",
        },
    )
    assert response.status_code == 403, response.text
    body = response.json()
    assert body["code"] == "FORBIDDEN"
    missing = (body.get("details") or {}).get("missingPermissions") or []
    assert "complaints:create" in missing


def _postgres_available() -> bool:
    from sqlalchemy import create_engine as _create_engine
    from sqlalchemy import text as _text

    from app.core.config import get_settings

    try:
        eng = _create_engine(
            get_settings().database_url,
            pool_pre_ping=True,
            future=True,
            connect_args={"connect_timeout": 2},
        )
        with eng.connect() as conn:
            conn.execute(_text("SELECT 1"))
        eng.dispose()
        return True
    except Exception:
        return False


requires_postgres = pytest.mark.skipif(
    not _postgres_available(),
    reason="PostgreSQL not available for security-audit row assertion",
)


@requires_postgres
def test_tc_cm_fr001_05_unauthorized_create_writes_security_audit(
    api_client_unauthorized: TestClient,
) -> None:
    """AC-CM-FR001-05 — the reject is also recorded as a security audit row.

    Same reject path as the always-on HTTP test above; this half additionally
    verifies the ``security.permission_denied`` SystemAuditLog row, matching
    the established platform pattern in
    test_secmig_p5_security_smoke.py::test_http_permission_denied_returns_403_and_permission_denied_audit.
    Skipped (not failed) when Postgres is unreachable, same as that file.
    """
    from sqlalchemy import create_engine, select
    from sqlalchemy.orm import sessionmaker

    from app.core.config import get_settings
    from app.modules.audit.models import SystemAuditLog
    from app.modules.audit.security_events import SecurityEventType

    response = api_client_unauthorized.post(
        "/api/v1/cm/complaints",
        headers={"Idempotency-Key": "api-req-unauthz-audit-1"},
        json={
            "customerId": "CUST-10001",
            "category": "BILLING",
            "channel": "BRANCH",
            "subject": "Should be rejected",
            "description": "No complaints:create permission",
        },
    )
    assert response.status_code == 403, response.text

    # Separate connection to the same database — write_security_event commits
    # on its own session inside the request, so a fresh read sees it too.
    engine = create_engine(get_settings().database_url, pool_pre_ping=True, future=True)
    session_factory = sessionmaker(bind=engine, autoflush=False, autocommit=False, future=True)
    session = session_factory()
    try:
        rows = list(
            session.scalars(
                select(SystemAuditLog)
                .where(
                    SystemAuditLog.event_type
                    == SecurityEventType.PERMISSION_DENIED.value,
                    SystemAuditLog.actor_id
                    == uuid.UUID("22222222-2222-2222-2222-222222222222"),
                )
                .order_by(SystemAuditLog.created_at.desc())
                .limit(5)
            )
        )
        assert rows, "expected security.permission_denied audit row"
        latest = rows[0]
        assert latest.entity_type == "Security"
        assert (latest.metadata_json or {}).get("reasonCode") == "FORBIDDEN"
        assert (latest.metadata_json or {}).get("path") == "/api/v1/cm/complaints"
    finally:
        session.close()
        engine.dispose()


# --- S2 Task 01 persistence ---


def test_s2_persistence_create_get_idempotent(persistent_service: CmBatch1Service) -> None:
    created = confirmed_create(persistent_service,
        CreateComplaintBatch1Request(
            customerId="CUST-10001",
            category="BILLING",
            channel="BRANCH",
            subject="Persisted",
            description="Desc",
        ),
        request_id="persist-req-1",
        channel_message_id=None,
        actor_id="actor-db",
    )
    assert created.status == "REGISTERED"
    assert created.case_created is False
    assert created.complaint_number.count("-") == 2
    unit, yymm, seq = created.complaint_number.split("-")
    assert len(unit) == 3 and unit.isalpha()
    assert len(yymm) == 4 and yymm.isdigit()
    assert seq.isdigit() and int(seq) >= 1

    loaded = persistent_service.get_complaint(created.complaint_id)
    assert loaded.complaint_id == created.complaint_id
    assert loaded.customer_id == "CUST-10001"

    replay = confirmed_create(persistent_service,
        CreateComplaintBatch1Request(
            customerId="CUST-10001",
            category="BILLING",
            channel="BRANCH",
            subject="Persisted",
            description="Desc",
        ),
        request_id="persist-req-1",
        channel_message_id=None,
        actor_id="actor-db",
    )
    assert replay.replayed is True
    assert replay.complaint_id == created.complaint_id


def test_s2_persistence_360_and_confirm(
    persistent_service: CmBatch1Service, db_session: Session
) -> None:
    persistent_service.confirm_customer("CUST-10001", principal_key="p-db")
    repo = CmBatch1Repository(db_session)
    assert repo.get_confirmed("p-db") == "CUST-10001"

    confirmed_create(persistent_service,
        CreateComplaintBatch1Request(
            customerId="CUST-10001",
            category="BILLING",
            channel="BRANCH",
            subject="360",
            description="Desc",
        ),
        request_id="persist-360",
        channel_message_id="CH-MSG-1",
        actor_id="a",
    )
    view = persistent_service.customer_360_minimum("CUST-10001")
    assert view.complaint_count == 1

    replay_ch = confirmed_create(persistent_service,
        CreateComplaintBatch1Request(
            customerId="CUST-10001",
            category="BILLING",
            channel="BRANCH",
            subject="other",
            description="Desc",
        ),
        request_id="persist-360-b",
        channel_message_id="CH-MSG-1",
        actor_id="a",
    )
    assert replay_ch.replayed is True


def test_s2_migration_revision_chain() -> None:
    path = (
        Path(__file__).resolve().parents[1]
        / "alembic"
        / "versions"
        / "0040_cm_batch1_persistence.py"
    )
    ns: dict[str, object] = {}
    exec(compile(path.read_text(encoding="utf-8"), str(path), "exec"), ns)
    assert ns["revision"] == "0040_cm_batch1_persistence"
    assert ns["down_revision"] == "0039_admin_rbac_repair"
    assert callable(ns["upgrade"])
    assert callable(ns["downgrade"])


def test_s2_task02_migration_revision_chain() -> None:
    path = (
        Path(__file__).resolve().parents[1]
        / "alembic"
        / "versions"
        / "0041_cm_batch1_duplicate.py"
    )
    ns: dict[str, object] = {}
    exec(compile(path.read_text(encoding="utf-8"), str(path), "exec"), ns)
    assert ns["revision"] == "0041_cm_batch1_duplicate"
    assert ns["down_revision"] == "0040_cm_batch1_persistence"
    assert callable(ns["upgrade"])
    assert callable(ns["downgrade"])


# --- S2 Task 02 FR-003 Duplicate Detection ---


def _seed_complaint(
    service: CmBatch1Service,
    *,
    request_id: str,
    category: str = "BILLING",
    subject: str = "Incorrect billing charge",
    channel: str = "BRANCH",
) -> str:
    created = confirmed_create(service,
        CreateComplaintBatch1Request(
            customerId="CUST-10001",
            category=category,
            channel=channel,
            subject=subject,
            description="Detail for duplicate tests",
        ),
        request_id=request_id,
        channel_message_id=None,
        actor_id="actor-dup",
    )
    return created.complaint_id


def test_unit_subject_similarity_deterministic() -> None:
    assert subject_similarity("Incorrect billing charge", "incorrect billing charge") == 1.0
    assert subject_similarity("billing charge", "network outage") < 0.2


def test_unit_score_uses_config_weights() -> None:
    cfg = DuplicateConfig()
    row = ComplaintAggregate(
        complaint_id="x",
        complaint_number="CM-1",
        customer_id="CUST-10001",
        category="BILLING",
        channel="BRANCH",
        subject="Incorrect billing charge",
        description="d",
        priority="MEDIUM",
    )
    score = score_candidate(
        intake_category="BILLING",
        intake_subject="Incorrect billing charge",
        intake_channel="BRANCH",
        existing=row,
        config=cfg,
    )
    assert score == 100
    assert score >= cfg.threshold


def test_tc_cm_fr003_01_warning_in_window(service: CmBatch1Service) -> None:
    _seed_complaint(service, request_id="dup-seed-1")
    result = service.check_duplicates(
        DuplicateCheckRequest(
            customerId="CUST-10001",
            category="BILLING",
            subject="Incorrect billing charge",
            channel="BRANCH",
        )
    )
    assert result.warning is True
    assert result.degraded is False
    assert len(result.candidates) >= 1
    assert result.candidates[0]["score"] >= 70


def test_tc_cm_fr003_02_link_existing_no_case(
    service: CmBatch1Service, store: Batch1Store
) -> None:
    surviving = _seed_complaint(service, request_id="dup-link-1")
    before = len(store._complaints)
    decision = service.record_duplicate_decision(
        DuplicateDecisionRequest(
            decision="link_existing",
            survivingComplaintId=surviving,
        ),
        actor_id="sup-1",
    )
    assert decision.decision == "link_existing"
    assert decision.case_created is False
    assert decision.surviving_complaint_id == surviving
    assert len(store._complaints) == before
    history = service.get_duplicate_history(customer_id="CUST-10001")
    assert any(h.decision == "link_existing" for h in history)


def test_tc_cm_fr003_03_override_without_reason_rejected(
    service: CmBatch1Service,
) -> None:
    with pytest.raises(ValidationAppError) as exc:
        service.record_duplicate_decision(
            DuplicateDecisionRequest(
                decision="override",
                customerId="CUST-10001",
                justification="too short",
            ),
            actor_id="a",
        )
    assert "Justifikasi" in exc.value.message or "alasan" in exc.value.message.lower()


def test_tc_cm_fr003_04_override_with_justification(
    service: CmBatch1Service,
) -> None:
    _seed_complaint(service, request_id="dup-ov-1")
    created = confirmed_create(service,
        CreateComplaintBatch1Request(
            customerId="CUST-10001",
            category="BILLING",
            channel="BRANCH",
            subject="Incorrect billing charge",
            description="Second intake",
            duplicateOverrideJustification="Distinct issue confirmed after customer call review",
        ),
        request_id="dup-ov-2",
        channel_message_id=None,
        actor_id="a",
    )
    assert created.case_created is False
    assert created.duplicate_check_result == "overridden"
    history = service.get_duplicate_history(customer_id="CUST-10001")
    assert any(h.decision == "override" for h in history)


def test_tc_cm_fr003_05_hard_block_rejects_create(service: CmBatch1Service) -> None:
    _seed_complaint(
        service,
        request_id="dup-hb-1",
        category="FRAUD",
        subject="Unauthorized card transaction",
    )
    with pytest.raises(ValidationAppError) as exc:
        confirmed_create(service,
            CreateComplaintBatch1Request(
                customerId="CUST-10001",
                category="FRAUD",
                channel="BRANCH",
                subject="Unauthorized card transaction",
                description="Second fraud report",
                duplicateOverrideJustification="Attempting override on hard block case now",
            ),
            request_id="dup-hb-2",
            channel_message_id=None,
            actor_id="a",
        )
    assert "Hard Block" in exc.value.message


def test_tc_cm_fr003_06_degraded_later_review(
    service: CmBatch1Service, store: Batch1Store
) -> None:
    store.force_degraded = True
    result = service.check_duplicates(
        DuplicateCheckRequest(customerId="CUST-10001", category="BILLING")
    )
    assert result.degraded is True
    assert result.later_review_work_item_id is not None
    assert result.later_review_work_item_id.startswith("LR-")
    assert result.candidates == []


def test_api_513_supervisor_queue_later_review_and_aging(
    service: CmBatch1Service, store: Batch1Store
) -> None:
    from datetime import UTC, datetime, timedelta

    store.force_degraded = True
    check = service.check_duplicates(
        DuplicateCheckRequest(customerId="CUST-10001", category="BILLING")
    )
    assert check.later_review_work_item_id is not None

    created = confirmed_create(
        service,
        CreateComplaintBatch1Request(
            customerId="CUST-10001",
            category="BILLING",
            channel="BRANCH",
            subject="Aging visibility subject",
            description="Detail for aging queue",
        ),
        request_id="aging-vis-1",
        actor_id="a",
    )
    row = store.get(created.complaint_id)
    assert row is not None
    row.created_at = datetime.now(UTC) - timedelta(hours=48)

    queue = service.get_supervisor_queue(aging_hours=24, limit=50)
    assert queue.aging_threshold_hours == 24
    assert any(
        i.work_item_id == check.later_review_work_item_id
        for i in queue.later_review_items
    )
    assert any(
        c.complaint_id == created.complaint_id for c in queue.aging_complaints
    )
    assert all(c.case_created is False for c in queue.aging_complaints)


def test_api_513_empty_queue(service: CmBatch1Service) -> None:
    queue = service.get_supervisor_queue(aging_hours=24, limit=50)
    assert queue.later_review_items == []
    assert queue.aging_complaints == []
    assert queue.aging_threshold_hours == 24


def test_api_513_aging_threshold_boundary(service: CmBatch1Service, store: Batch1Store) -> None:
    from datetime import UTC, datetime, timedelta

    created = confirmed_create(
        service,
        CreateComplaintBatch1Request(
            customerId="CUST-10001",
            category="BILLING",
            channel="BRANCH",
            subject="Boundary aging",
            description="Exact threshold",
        ),
        request_id="aging-bound-1",
        actor_id="a",
    )
    row = store.get(created.complaint_id)
    assert row is not None
    # Align to the same clock used by get_supervisor_queue: age exactly 24h.
    # Inclusion rule: created_at <= now - agingHours.
    fixed_now = datetime.now(UTC)
    row.created_at = fixed_now - timedelta(hours=24)

    included = service.get_supervisor_queue(aging_hours=24, limit=50)
    assert any(c.complaint_id == created.complaint_id for c in included.aging_complaints)

    # Just under threshold (newer than cutoff) must be excluded.
    row.created_at = datetime.now(UTC) - timedelta(hours=23, minutes=50)
    excluded = service.get_supervisor_queue(aging_hours=24, limit=50)
    assert all(c.complaint_id != created.complaint_id for c in excluded.aging_complaints)


def test_api_513_limit_caps_many_items(service: CmBatch1Service, store: Batch1Store) -> None:
    for i in range(12):
        store.create_later_review_work_item(
            customer_id=f"CUST-{i}", reason="duplicate_check_degraded"
        )
    capped = service.get_supervisor_queue(limit=5)
    assert len(capped.later_review_items) == 5
    # Contract: limit only — no offset/page; larger limit returns more.
    wider = service.get_supervisor_queue(limit=20)
    assert len(wider.later_review_items) == 12


def test_api_513_unknown_reason_pass_through(service: CmBatch1Service, store: Batch1Store) -> None:
    wid = store.create_later_review_work_item(
        customer_id="CUST-X", reason="future_enrichment_v2"
    )
    queue = service.get_supervisor_queue()
    hit = next(i for i in queue.later_review_items if i.work_item_id == wid)
    assert hit.reason == "future_enrichment_v2"
    assert hit.status == "OPEN"
    assert hit.complaint_id is None


def test_api_513_m3d_complaint_id_on_later_review(
    service: CmBatch1Service, store: Batch1Store
) -> None:
    """M3d / EX-G: complaintId present when known; null for pre-create degrade."""
    store.force_degraded = True
    check = service.check_duplicates(
        DuplicateCheckRequest(customerId="CUST-10001", category="BILLING")
    )
    assert check.later_review_work_item_id is not None
    queue = service.get_supervisor_queue()
    degraded = next(
        i
        for i in queue.later_review_items
        if i.work_item_id == check.later_review_work_item_id
    )
    assert degraded.complaint_id is None
    assert degraded.reason == "duplicate_check_degraded"

    created = confirmed_create(
        service,
        CreateComplaintBatch1Request(
            customerId="CUST-10001",
            category="BILLING",
            channel="BRANCH",
            subject="Bind failure anchor",
            description="Detail",
        ),
        request_id="m3d-anchor-1",
        actor_id="a",
    )
    wid = service.enqueue_later_review(
        customer_id=created.customer_id,
        reason="attachment_bind_failed",
        complaint_id=created.complaint_id,
    )
    queue2 = service.get_supervisor_queue()
    hit = next(i for i in queue2.later_review_items if i.work_item_id == wid)
    assert hit.complaint_id == created.complaint_id
    assert hit.reason == "attachment_bind_failed"
    assert hit.status == "OPEN"


def test_api_513_http_roundtrip_smoke_e2e(
    api_client: TestClient, service: CmBatch1Service, store: Batch1Store
) -> None:
    """Create → later-review + aging → API-513 JSON fields → detail get (no Case)."""
    from datetime import UTC, datetime, timedelta

    empty = api_client.get("/api/v1/cm/supervisor/queue?agingHours=24&limit=50")
    assert empty.status_code == 200, empty.text
    empty_body = empty.json()["data"]
    assert empty_body["laterReviewItems"] == []
    assert empty_body["agingComplaints"] == []
    assert empty_body["agingThresholdHours"] == 24
    assert "asOf" in empty_body

    store.force_degraded = True
    check = api_client.post(
        "/api/v1/cm/duplicates/check",
        json={"customerId": "CUST-10001", "category": "BILLING"},
    )
    assert check.status_code == 200, check.text
    lr_id = check.json()["data"]["laterReviewWorkItemId"]
    assert lr_id and str(lr_id).startswith("LR-")

    confirm = api_client.post(
        "/api/v1/cm/customers/confirm",
        json={"customerId": "CUST-10001"},
    )
    assert confirm.status_code == 200, confirm.text
    created = api_client.post(
        "/api/v1/cm/complaints",
        headers={"Idempotency-Key": "api513-e2e-1"},
        json={
            "customerId": "CUST-10001",
            "category": "BILLING",
            "channel": "BRANCH",
            "subject": "Supervisor e2e aging",
            "description": "Detail\n\n---\nCatatan:\nCatatan lab",
            "priority": "MEDIUM",
        },
    )
    assert created.status_code in (200, 201), created.text
    complaint = created.json()["data"]
    assert complaint["caseCreated"] is False
    complaint_id = complaint["complaintId"]

    row = store.get(complaint_id)
    assert row is not None
    row.created_at = datetime.now(UTC) - timedelta(hours=30)

    queue = api_client.get(
        "/api/v1/cm/supervisor/queue?workItemStatus=OPEN&agingHours=24&limit=100"
    )
    assert queue.status_code == 200, queue.text
    data = queue.json()["data"]
    assert data["agingThresholdHours"] == 24

    lr_hit = next(i for i in data["laterReviewItems"] if i["workItemId"] == lr_id)
    assert set(lr_hit.keys()) >= {
        "workItemId",
        "customerId",
        "reason",
        "status",
        "createdAt",
        "ageHours",
    }
    assert "complaintId" in lr_hit
    assert lr_hit["complaintId"] is None  # pre-create degraded
    assert lr_hit["status"] == "OPEN"
    assert lr_hit["reason"] == "duplicate_check_degraded"

    age_hit = next(c for c in data["agingComplaints"] if c["complaintId"] == complaint_id)
    assert set(age_hit.keys()) >= {
        "complaintId",
        "complaintNumber",
        "customerId",
        "status",
        "createdAt",
        "ageHours",
        "caseCreated",
    }
    assert age_hit["caseCreated"] is False
    assert age_hit["status"] == "REGISTERED"
    assert age_hit["ageHours"] >= 24

    # Detail via Aggregate service (API-501 path uses org-scope DB resolver —
    # lab api_client overrides service only; assert no Case without Postgres).
    detail = service.get_complaint(complaint_id)
    assert detail.case_created is False
    assert detail.complaint_id == complaint_id
    assert detail.complaint_number == age_hit["complaintNumber"]


def test_tc_cm_fr003_07_out_of_scope_uniform_empty(store: Batch1Store) -> None:
    svc = CmBatch1Service(
        customer_provider=StubCustomerProvider(),
        guard=EnumerationGuard(),
        store=store,
        scope_allows_candidate=lambda _c: False,
    )
    _seed_complaint(svc, request_id="dup-scope-1")
    result = svc.check_duplicates(
        DuplicateCheckRequest(
            customerId="CUST-10001",
            category="BILLING",
            subject="Incorrect billing charge",
            channel="BRANCH",
        )
    )
    assert result.warning is False
    assert result.candidates == []
    assert result.degraded is False


def test_tc_cm_fr003_08_no_case_from_duplicate_flow(service: CmBatch1Service) -> None:
    surviving = _seed_complaint(service, request_id="dup-nc-1")
    check = service.check_duplicates(
        DuplicateCheckRequest(
            customerId="CUST-10001",
            category="BILLING",
            subject="Incorrect billing charge",
            channel="BRANCH",
        )
    )
    assert check.warning is True
    decision = service.record_duplicate_decision(
        DuplicateDecisionRequest(
            decision="recommend_only",
            survivingComplaintId=surviving,
            customerId="CUST-10001",
        ),
        actor_id="a",
    )
    assert decision.case_created is False
    blocked = service.record_duplicate_decision(
        DuplicateDecisionRequest(
            decision="blocked",
            customerId="CUST-10001",
            survivingComplaintId=surviving,
        ),
        actor_id="a",
    )
    assert blocked.case_created is False
    assert blocked.hard_block is True


def test_s2_persistence_duplicate_check_and_decision(
    persistent_service: CmBatch1Service, db_session: Session
) -> None:
    first = confirmed_create(persistent_service,
        CreateComplaintBatch1Request(
            customerId="CUST-10001",
            category="BILLING",
            channel="BRANCH",
            subject="Wrong fee charged on account",
            description="Detail",
        ),
        request_id="persist-dup-1",
        channel_message_id=None,
        actor_id="a",
    )
    check = persistent_service.check_duplicates(
        DuplicateCheckRequest(
            customerId="CUST-10001",
            category="BILLING",
            subject="Wrong fee charged on account",
            channel="BRANCH",
        )
    )
    assert check.warning is True
    decision = persistent_service.record_duplicate_decision(
        DuplicateDecisionRequest(
            decision="link_existing",
            survivingComplaintId=first.complaint_id,
        ),
        actor_id="a",
    )
    assert decision.case_created is False
    repo = CmBatch1Repository(db_session)
    history = repo.get_duplicate_history(customer_id="CUST-10001")
    assert len(history) >= 1
    assert history[0].decision == "link_existing"


def test_api_505_and_506_roundtrip(
    api_client: TestClient, service: CmBatch1Service
) -> None:
    surviving = _seed_complaint(service, request_id="api-dup-1")
    check = api_client.post(
        "/api/v1/cm/duplicates/check",
        json={
            "customerId": "CUST-10001",
            "category": "BILLING",
            "subject": "Incorrect billing charge",
            "channel": "BRANCH",
        },
    )
    assert check.status_code == 200, check.text
    body = check.json()["data"]
    assert body["warning"] is True
    assert isinstance(body["candidates"], list)
    assert "degraded" in body

    decision = api_client.post(
        "/api/v1/cm/duplicates/decisions",
        json={
            "decision": "link_existing",
            "survivingComplaintId": surviving,
        },
    )
    assert decision.status_code == 200, decision.text
    data = decision.json()["data"]
    assert data["decision"] == "link_existing"
    assert data["caseCreated"] is False

    rejected = api_client.post(
        "/api/v1/cm/duplicates/decisions",
        json={
            "decision": "override",
            "customerId": "CUST-10001",
            "justification": "short",
        },
    )
    assert rejected.status_code == 400


def test_api_515_approve_intake_escalation(
    service: CmBatch1Service, store: Batch1Store
) -> None:
    created = confirmed_create(
        service,
        CreateComplaintBatch1Request(
            customerId="CUST-10001",
            category="BILLING",
            channel="BRANCH",
            subject="Escalate pending",
            description="Keluhan singkat\n\n---\nAlasan eskalasi:\nButuh pusat karena kompleks",
            intakeDisposition="ESCALATE_PENDING_APPROVAL",
        ),
        request_id="esc-approve-1",
        actor_id="agent-1",
    )
    assert created.intake_disposition == "ESCALATE_PENDING_APPROVAL"
    assert created.status == "REGISTERED"
    assert created.escalation_reason == "Butuh pusat karena kompleks"
    assert created.intake_narrative == "Keluhan singkat"

    decided = service.decide_intake_escalation(
        created.complaint_id,
        IntakeEscalationDecisionRequest(
            decision="APPROVE",
            note="Disetujui: lanjut ke Pusat untuk konfigurasi parameter terminal.",
            priority="HIGH",
        ),
        actor_id="supervisor-1",
    )
    assert decided.status == "REGISTERED"
    assert decided.intake_disposition == "ESCALATE_APPROVED"
    assert decided.case_created is False
    assert decided.supervisor_note is not None
    assert "konfigurasi parameter" in decided.supervisor_note
    assert decided.priority == "HIGH"
    row = store.get(created.complaint_id)
    assert row is not None
    assert row.intake_disposition == "ESCALATE_APPROVED"
    assert row.priority == "HIGH"
    assert "Catatan Supervisor:" in (row.description or "")


def test_supervisor_intake_escalate_auto_approves(
    service: CmBatch1Service, store: Batch1Store
) -> None:
    created = confirmed_create(
        service,
        CreateComplaintBatch1Request(
            customerId="CUST-10001",
            category="BILLING",
            channel="BRANCH",
            subject="Supervisor escalate intake",
            description="Keluhan\n\n---\nAlasan eskalasi:\nButuh pusat karena kompleks",
            intakeDisposition="ESCALATE_PENDING_APPROVAL",
            priority="HIGH",
        ),
        request_id="esc-spv-auto-1",
        actor_id="supervisor-1",
        auto_approve_escalation=True,
    )
    assert created.intake_disposition == "ESCALATE_APPROVED"
    assert created.supervisor_note is not None
    assert "kompleks" in created.supervisor_note
    row = store.get(created.complaint_id)
    assert row is not None
    assert row.intake_disposition == "ESCALATE_APPROVED"
    assert row.decided_by == "supervisor-1"


def test_api_515_approve_and_hq_accept_with_bound_case(
    service: CmBatch1Service, store: Batch1Store
) -> None:
    from datetime import date

    from app.modules.cm_batch1.schemas import HqAcceptAndScheduleRequest

    created = confirmed_create(
        service,
        CreateComplaintBatch1Request(
            customerId="CUST-10001",
            category="BILLING",
            channel="BRANCH",
            subject="Escalate with case",
            description="Keluhan\n\n---\nAlasan eskalasi:\nButuh pusat karena kompleks",
            intakeDisposition="ESCALATE_PENDING_APPROVAL",
        ),
        request_id="esc-case-bound-1",
        actor_id="agent-1",
    )
    row = store.get(created.complaint_id)
    assert row is not None
    row.case_created = True
    row.status = "IN_PROGRESS"

    decided = service.decide_intake_escalation(
        created.complaint_id,
        IntakeEscalationDecisionRequest(
            decision="APPROVE",
            note="Disetujui: Case tetap terikat nomor pengaduan.",
            priority="HIGH",
        ),
        actor_id="supervisor-1",
    )
    assert decided.intake_disposition == "ESCALATE_APPROVED"
    assert decided.status == "IN_PROGRESS"
    assert decided.case_created is True

    scheduled = service.accept_and_schedule_at_hq(
        created.complaint_id,
        HqAcceptAndScheduleRequest(
            arrivalDate=date(2026, 8, 20),
            arrivalTime="09:30",
            note="Bawa KTP asli dan bukti pembayaran terakhir.",
        ),
        actor_id="hq-1",
    )
    assert scheduled.hq_accepted_at is not None
    assert scheduled.intake_disposition == "HQ_SCHEDULED"
    assert scheduled.case_created is True

    with pytest.raises(InvalidStateError):
        service.decide_intake_escalation(
            created.complaint_id,
            IntakeEscalationDecisionRequest(
                decision="CANCEL",
                note="Tidak boleh batalkan setelah Pusat menerima pengaduan.",
            ),
            actor_id="supervisor-1",
        )


def test_api_515_approve_sets_decided_by(
    service: CmBatch1Service, store: Batch1Store
) -> None:
    created = confirmed_create(
        service,
        CreateComplaintBatch1Request(
            customerId="CUST-10001",
            category="BILLING",
            channel="BRANCH",
            subject="Escalate decided-by",
            description="Keluhan\n\n---\nAlasan eskalasi:\nButuh pusat karena kompleks",
            intakeDisposition="ESCALATE_PENDING_APPROVAL",
        ),
        request_id="esc-decided-by-1",
        actor_id="agent-1",
    )
    service.decide_intake_escalation(
        created.complaint_id,
        IntakeEscalationDecisionRequest(
            decision="APPROVE",
            note="Disetujui: lanjut ke Pusat untuk konfigurasi parameter terminal.",
            priority="HIGH",
        ),
        actor_id="supervisor-1",
    )
    row = store.get(created.complaint_id)
    assert row is not None
    assert row.decided_by == "supervisor-1"
    assert row.decided_at is not None


def test_work_stats_for_user_counts_created_and_decisions(
    service: CmBatch1Service,
) -> None:
    approved = confirmed_create(
        service,
        CreateComplaintBatch1Request(
            customerId="CUST-10001",
            category="BILLING",
            channel="BRANCH",
            subject="Escalate to be approved",
            description="Keluhan\n\n---\nAlasan eskalasi:\nButuh pusat",
            intakeDisposition="ESCALATE_PENDING_APPROVAL",
        ),
        request_id="stats-approved",
        actor_id="agent-1",
    )
    rejected = confirmed_create(
        service,
        CreateComplaintBatch1Request(
            customerId="CUST-10002",
            category="BILLING",
            channel="BRANCH",
            subject="Escalate to be rejected",
            description="Keluhan\n\n---\nAlasan eskalasi:\nButuh pusat",
            intakeDisposition="ESCALATE_PENDING_APPROVAL",
        ),
        request_id="stats-rejected",
        actor_id="agent-1",
    )
    confirmed_create(
        service,
        CreateComplaintBatch1Request(
            customerId="CUST-10002",
            category="SERVICE",
            channel="ONLINE",
            subject="Not escalated at all, distinct enough subject line",
            description="Keluhan biasa tanpa eskalasi, tidak ada hubungan dengan yang lain.",
        ),
        request_id="stats-plain",
        actor_id="agent-1",
    )

    service.decide_intake_escalation(
        approved.complaint_id,
        IntakeEscalationDecisionRequest(
            decision="APPROVE",
            note="Disetujui: lanjut ke Pusat untuk konfigurasi parameter terminal.",
            priority="HIGH",
        ),
        actor_id="supervisor-1",
    )
    service.decide_intake_escalation(
        rejected.complaint_id,
        IntakeEscalationDecisionRequest(
            decision="REJECT",
            note="Ditolak: kurang bukti pendukung untuk diteruskan ke Pusat.",
        ),
        actor_id="supervisor-1",
    )

    agent_stats = service.work_stats_for_user("agent-1")
    assert agent_stats.created_count == 3
    assert agent_stats.escalation_requested_count == 2
    assert agent_stats.escalation_approved_count == 0
    assert agent_stats.escalation_rejected_count == 0

    supervisor_stats = service.work_stats_for_user("supervisor-1")
    assert supervisor_stats.created_count == 0
    assert supervisor_stats.escalation_approved_count == 1
    assert supervisor_stats.escalation_rejected_count == 1

    assert service.work_stats_for_user("nobody").created_count == 0


def test_list_complaints_filters_by_created_by(service: CmBatch1Service) -> None:
    confirmed_create(
        service,
        CreateComplaintBatch1Request(
            customerId="CUST-10001",
            category="BILLING",
            channel="BRANCH",
            subject="Agent one complaint",
            description="Keluhan agent satu.",
        ),
        request_id="filter-agent-1",
        actor_id="agent-1",
    )
    confirmed_create(
        service,
        CreateComplaintBatch1Request(
            customerId="CUST-10002",
            category="BILLING",
            channel="BRANCH",
            subject="Agent two complaint",
            description="Keluhan agent dua.",
        ),
        request_id="filter-agent-2",
        actor_id="agent-2",
    )

    items, total = service.list_complaints(created_by="agent-1")
    assert total == 1
    assert len(items) == 1
    assert items[0].created_by == "agent-1"


def test_api_515_approve_requires_supervisor_note(
    service: CmBatch1Service,
) -> None:
    created = confirmed_create(
        service,
        CreateComplaintBatch1Request(
            customerId="CUST-10001",
            category="BILLING",
            channel="BRANCH",
            subject="Escalate pending note",
            description="Keluhan\n\n---\nAlasan eskalasi:\nButuh pusat",
            intakeDisposition="ESCALATE_PENDING_APPROVAL",
        ),
        request_id="esc-approve-note-required",
        actor_id="agent-1",
    )
    with pytest.raises(ValidationAppError):
        service.decide_intake_escalation(
            created.complaint_id,
            IntakeEscalationDecisionRequest(
                decision="APPROVE", note="short", priority="HIGH"
            ),
            actor_id="supervisor-1",
        )
    with pytest.raises(ValidationAppError):
        service.decide_intake_escalation(
            created.complaint_id,
            IntakeEscalationDecisionRequest(decision="APPROVE", priority="HIGH"),
            actor_id="supervisor-1",
        )


def test_api_515_approve_requires_priority(service: CmBatch1Service) -> None:
    created = confirmed_create(
        service,
        CreateComplaintBatch1Request(
            customerId="CUST-10001",
            category="BILLING",
            channel="BRANCH",
            subject="Escalate pending priority",
            description="Keluhan\n\n---\nAlasan eskalasi:\nButuh pusat",
            intakeDisposition="ESCALATE_PENDING_APPROVAL",
            priority="LOW",
        ),
        request_id="esc-approve-priority-required",
        actor_id="agent-1",
    )
    with pytest.raises(ValidationAppError):
        service.decide_intake_escalation(
            created.complaint_id,
            IntakeEscalationDecisionRequest(
                decision="APPROVE",
                note="Catatan supervisor cukup panjang untuk lolos validasi.",
            ),
            actor_id="supervisor-1",
        )


def test_api_515_reject_requires_note(service: CmBatch1Service) -> None:
    created = confirmed_create(
        service,
        CreateComplaintBatch1Request(
            customerId="CUST-10001",
            category="BILLING",
            channel="BRANCH",
            subject="Escalate reject",
            description="Keluhan\n\n---\nAlasan eskalasi:\nUji tolak dari supervisor",
            intakeDisposition="ESCALATE_PENDING_APPROVAL",
        ),
        request_id="esc-reject-1",
        actor_id="agent-1",
    )
    with pytest.raises(ValidationAppError):
        service.decide_intake_escalation(
            created.complaint_id,
            IntakeEscalationDecisionRequest(decision="REJECT", note="short"),
            actor_id="supervisor-1",
        )

    decided = service.decide_intake_escalation(
        created.complaint_id,
        IntakeEscalationDecisionRequest(
            decision="REJECT",
            note="Tolak: masih bisa diselesaikan di cabang dengan bukti lengkap.",
        ),
        actor_id="supervisor-1",
    )
    assert decided.intake_disposition == "ESCALATE_REJECTED"
    assert decided.status == "REGISTERED"
    assert decided.case_created is False
    assert decided.rejection_note is not None
    assert "cabang" in decided.rejection_note.lower() or len(
        decided.rejection_note
    ) >= 20


def test_api_515_cancel_batal_eskalasi(
    service: CmBatch1Service, store: Batch1Store
) -> None:
    created = confirmed_create(
        service,
        CreateComplaintBatch1Request(
            customerId="CUST-10001",
            category="BILLING",
            channel="BRANCH",
            subject="Escalate then cancel",
            description="Keluhan\n\n---\nAlasan eskalasi:\nButuh pusat untuk batal uji",
            intakeDisposition="ESCALATE_PENDING_APPROVAL",
        ),
        request_id="esc-cancel-1",
        actor_id="agent-1",
    )
    approved = service.decide_intake_escalation(
        created.complaint_id,
        IntakeEscalationDecisionRequest(
            decision="APPROVE",
            note="Disetujui sementara sebelum dibatalkan oleh supervisor.",
            priority="MEDIUM",
        ),
        actor_id="supervisor-1",
    )
    assert approved.intake_disposition == "ESCALATE_APPROVED"

    cancelled = service.decide_intake_escalation(
        created.complaint_id,
        IntakeEscalationDecisionRequest(
            decision="CANCEL",
            note="Batalkan Eskalasi: pelanggan sudah setuju diselesaikan di cabang.",
        ),
        actor_id="supervisor-1",
    )
    assert cancelled.intake_disposition == "ESCALATE_CANCELLED"
    assert cancelled.cancellation_note is not None
    assert "cabang" in cancelled.cancellation_note.lower()
    assert cancelled.supervisor_note is not None
    assert cancelled.hq_accepted_at is None
    row = store.get(created.complaint_id)
    assert row is not None
    assert "Batalkan Eskalasi:" in (row.description or "")
    assert "Catatan Supervisor:" in (row.description or "")

    with pytest.raises(InvalidStateError):
        service.decide_intake_escalation(
            created.complaint_id,
            IntakeEscalationDecisionRequest(
                decision="CANCEL",
                note="Tidak boleh batalkan lagi setelah ESCALATE_CANCELLED status.",
            ),
            actor_id="supervisor-1",
        )


def test_api_518_re_escalate_after_cancelled_keeps_history(
    service: CmBatch1Service, store: Batch1Store
) -> None:
    from app.modules.cm_batch1.schemas import IntakeEscalationRequestBody

    created = confirmed_create(
        service,
        CreateComplaintBatch1Request(
            customerId="CUST-10001",
            category="BILLING",
            channel="BRANCH",
            subject="Cancel then re-escalate",
            description="Keluhan awal\n\n---\nAlasan eskalasi:\nButuh pusat untuk kasus kompleks",
            intakeDisposition="ESCALATE_PENDING_APPROVAL",
        ),
        request_id="esc-re-1",
        actor_id="agent-1",
    )
    service.decide_intake_escalation(
        created.complaint_id,
        IntakeEscalationDecisionRequest(
            decision="APPROVE",
            note="Disetujui sementara sebelum dibatalkan oleh supervisor.",
            priority="HIGH",
        ),
        actor_id="supervisor-1",
    )
    cancelled = service.decide_intake_escalation(
        created.complaint_id,
        IntakeEscalationDecisionRequest(
            decision="CANCEL",
            note="Batalkan Eskalasi: pelanggan minta ditangani di cabang dulu.",
        ),
        actor_id="supervisor-1",
    )
    assert cancelled.intake_disposition == "ESCALATE_CANCELLED"
    assert cancelled.cancellation_note is not None

    re_requested = service.request_intake_escalation(
        created.complaint_id,
        IntakeEscalationRequestBody(
            reason="Ajuan ulang: bukti cabang tidak cukup, perlu tinjauan Pusat."
        ),
        actor_id="agent-1",
    )
    assert re_requested.intake_disposition == "ESCALATE_PENDING_APPROVAL"
    assert re_requested.cancellation_note is not None
    assert "cabang" in re_requested.cancellation_note.lower()
    assert re_requested.supervisor_note is not None
    assert re_requested.escalation_reason is not None
    assert "Ajuan ulang" in re_requested.escalation_reason
    assert "kasus kompleks" in re_requested.escalation_reason.lower()
    assert "bukti cabang tidak cukup" in re_requested.escalation_reason.lower()

    row = store.get(created.complaint_id)
    assert row is not None
    desc = row.description or ""
    assert "Batalkan Eskalasi:" in desc
    assert "Catatan Supervisor:" in desc
    assert "Alasan eskalasi:" in desc
    assert "[Ajuan ulang]" in desc


def test_api_518_re_escalate_after_rejected_keeps_history(
    service: CmBatch1Service, store: Batch1Store
) -> None:
    from app.modules.cm_batch1.schemas import IntakeEscalationRequestBody

    created = confirmed_create(
        service,
        CreateComplaintBatch1Request(
            customerId="CUST-10001",
            category="BILLING",
            channel="BRANCH",
            subject="Reject then re-escalate",
            description="Keluhan\n\n---\nAlasan eskalasi:\nPerlu eskalasi karena regulasi",
            intakeDisposition="ESCALATE_PENDING_APPROVAL",
        ),
        request_id="esc-re-2",
        actor_id="agent-1",
    )
    rejected = service.decide_intake_escalation(
        created.complaint_id,
        IntakeEscalationDecisionRequest(
            decision="REJECT",
            note="Tolak: masih bisa diselesaikan di cabang dengan bukti lengkap.",
        ),
        actor_id="supervisor-1",
    )
    assert rejected.intake_disposition == "ESCALATE_REJECTED"

    re_requested = service.request_intake_escalation(
        created.complaint_id,
        IntakeEscalationRequestBody(
            reason="Ajuan ulang setelah bukti tambahan: lampiran kontrak lengkap."
        ),
        actor_id="agent-1",
    )
    assert re_requested.intake_disposition == "ESCALATE_PENDING_APPROVAL"
    assert re_requested.rejection_note is not None
    assert "cabang" in re_requested.rejection_note.lower()
    row = store.get(created.complaint_id)
    assert row is not None
    assert "Penolakan Eskalasi:" in (row.description or "")


def test_api_518_re_escalate_idempotent_when_already_pending(
    service: CmBatch1Service,
) -> None:
    from app.modules.cm_batch1.schemas import IntakeEscalationRequestBody

    created = confirmed_create(
        service,
        CreateComplaintBatch1Request(
            customerId="CUST-10001",
            category="BILLING",
            channel="BRANCH",
            subject="Idempotent re-escalate",
            description="Keluhan\n\n---\nAlasan eskalasi:\nButuh pusat untuk uji idempotent",
            intakeDisposition="ESCALATE_PENDING_APPROVAL",
        ),
        request_id="esc-re-idem-1",
        actor_id="agent-1",
    )
    service.decide_intake_escalation(
        created.complaint_id,
        IntakeEscalationDecisionRequest(
            decision="APPROVE",
            note="Disetujui sementara sebelum dibatalkan untuk uji idempotent.",
            priority="MEDIUM",
        ),
        actor_id="supervisor-1",
    )
    service.decide_intake_escalation(
        created.complaint_id,
        IntakeEscalationDecisionRequest(
            decision="CANCEL",
            note="Batalkan Eskalasi: uji double submit setelah ajuan ulang.",
        ),
        actor_id="supervisor-1",
    )
    first = service.request_intake_escalation(
        created.complaint_id,
        IntakeEscalationRequestBody(
            reason="Ajuan ulang pertama setelah batalkan untuk uji idempotent."
        ),
        actor_id="agent-1",
    )
    assert first.intake_disposition == "ESCALATE_PENDING_APPROVAL"
    second = service.request_intake_escalation(
        created.complaint_id,
        IntakeEscalationRequestBody(
            reason="Ajuan ulang kedua yang harus idempotent tanpa error state."
        ),
        actor_id="agent-1",
    )
    assert second.intake_disposition == "ESCALATE_PENDING_APPROVAL"
    assert second.cancellation_note is not None


def test_api_518_re_escalate_blocked_when_approved(
    service: CmBatch1Service,
) -> None:
    from app.modules.cm_batch1.schemas import IntakeEscalationRequestBody

    created = confirmed_create(
        service,
        CreateComplaintBatch1Request(
            customerId="CUST-10001",
            category="BILLING",
            channel="BRANCH",
            subject="Approved cannot re-escalate",
            description="Keluhan\n\n---\nAlasan eskalasi:\nSudah disetujui belum dibatalkan",
            intakeDisposition="ESCALATE_PENDING_APPROVAL",
        ),
        request_id="esc-re-3",
        actor_id="agent-1",
    )
    service.decide_intake_escalation(
        created.complaint_id,
        IntakeEscalationDecisionRequest(
            decision="APPROVE",
            note="Disetujui ke Pusat; jangan ajukan ulang tanpa batalkan.",
            priority="HIGH",
        ),
        actor_id="supervisor-1",
    )
    with pytest.raises(InvalidStateError):
        service.request_intake_escalation(
            created.complaint_id,
            IntakeEscalationRequestBody(
                reason="Tidak boleh ajukan ulang saat masih ESCALATE_APPROVED."
            ),
            actor_id="agent-1",
        )


def test_api_515_cancel_blocked_after_hq_accepted(
    service: CmBatch1Service, store: Batch1Store
) -> None:
    from datetime import UTC, datetime

    created = confirmed_create(
        service,
        CreateComplaintBatch1Request(
            customerId="CUST-10001",
            category="BILLING",
            channel="BRANCH",
            subject="HQ accepted blocks cancel",
            description="Keluhan\n\n---\nAlasan eskalasi:\nButuh pusat HQ accept",
            intakeDisposition="ESCALATE_PENDING_APPROVAL",
            duplicateOverrideJustification=(
                "Lab override for HQ-accepted cancel block test."
            ),
        ),
        request_id="esc-hq-accepted-1",
        actor_id="agent-1",
    )
    service.decide_intake_escalation(
        created.complaint_id,
        IntakeEscalationDecisionRequest(
            decision="APPROVE",
            note="Disetujui sebelum Pusat menerima pengaduan ini.",
            priority="HIGH",
        ),
        actor_id="supervisor-1",
    )
    row = store.get(created.complaint_id)
    assert row is not None
    row.hq_accepted_at = datetime.now(UTC)

    with pytest.raises(InvalidStateError):
        service.decide_intake_escalation(
            created.complaint_id,
            IntakeEscalationDecisionRequest(
                decision="CANCEL",
                note="Tidak boleh batalkan setelah Pusat menerima pengaduan.",
            ),
            actor_id="supervisor-1",
        )
    loaded = service.get_complaint(created.complaint_id)
    assert loaded.hq_accepted_at is not None
    assert loaded.intake_disposition == "ESCALATE_APPROVED"


def test_api_516_hq_accept_and_517_schedule(
    service: CmBatch1Service, store: Batch1Store
) -> None:
    created = confirmed_create(
        service,
        CreateComplaintBatch1Request(
            customerId="CUST-10001",
            category="BILLING",
            channel="BRANCH",
            subject="HQ accept and schedule",
            description="Keluhan\n\n---\nAlasan eskalasi:\nButuh jadwal pusat",
            intakeDisposition="ESCALATE_PENDING_APPROVAL",
            duplicateOverrideJustification=(
                "Lab override for HQ accept and schedule arrival test."
            ),
        ),
        request_id="esc-hq-schedule-1",
        actor_id="agent-1",
    )
    service.decide_intake_escalation(
        created.complaint_id,
        IntakeEscalationDecisionRequest(
            decision="APPROVE",
            note="Disetujui agar Pusat dapat menerima dan menjadwalkan.",
            priority="MEDIUM",
        ),
        actor_id="supervisor-1",
    )

    from datetime import date

    from app.modules.cm_batch1.schemas import (
        HqAcceptAndScheduleRequest,
        HqAcceptRequest,
        HqScheduleArrivalRequest,
    )

    with pytest.raises(InvalidStateError):
        service.schedule_hq_arrival(
            created.complaint_id,
            HqScheduleArrivalRequest(
                arrivalDate=date(2026, 8, 10), arrivalTime="09:30"
            ),
            actor_id="hq-1",
        )

    scheduled = service.accept_and_schedule_at_hq(
        created.complaint_id,
        HqAcceptAndScheduleRequest(
            arrivalDate=date(2026, 8, 10),
            arrivalTime="09:30",
            note="Bawa KTP asli dan bukti pembayaran terakhir.",
        ),
        actor_id="hq-1",
    )
    assert scheduled.hq_accepted_at is not None
    assert scheduled.intake_disposition == "HQ_SCHEDULED"
    assert scheduled.hq_arrival_date == date(2026, 8, 10)
    assert scheduled.hq_arrival_time == "09:30"
    row = store.get(created.complaint_id)
    assert row is not None
    assert "Penerimaan Pusat:" in (row.description or "")
    assert "Jadwal kedatangan:" in (row.description or "")
    assert row.intake_disposition == "HQ_SCHEDULED"

    rescheduled = service.schedule_hq_arrival(
        created.complaint_id,
        HqScheduleArrivalRequest(
            arrivalDate=date(2026, 8, 11),
            arrivalTime="10:00",
            note="Jadwal digeser — kabari pelanggan lagi.",
        ),
        actor_id="hq-1",
    )
    assert rescheduled.hq_arrival_date == date(2026, 8, 11)
    assert rescheduled.intake_disposition == "HQ_SCHEDULED"

    with pytest.raises(InvalidStateError):
        service.decide_intake_escalation(
            created.complaint_id,
            IntakeEscalationDecisionRequest(
                decision="CANCEL",
                note="Tidak boleh batalkan setelah Pusat menerima pengaduan ini.",
            ),
            actor_id="supervisor-1",
        )

    with pytest.raises(InvalidStateError):
        service.accept_at_hq(
            created.complaint_id,
            HqAcceptRequest(note="Sudah diterima sebelumnya."),
            actor_id="hq-1",
        )


def test_api_519_hq_return_to_branch(
    service: CmBatch1Service, store: Batch1Store
) -> None:
    created = confirmed_create(
        service,
        CreateComplaintBatch1Request(
            customerId="CUST-10001",
            category="BILLING",
            channel="BRANCH",
            subject="HQ return to branch",
            description="Keluhan\n\n---\nAlasan eskalasi:\nButuh berkas pusat",
            intakeDisposition="ESCALATE_PENDING_APPROVAL",
            duplicateOverrideJustification=(
                "Lab override for HQ return to branch test."
            ),
        ),
        request_id="esc-hq-return-1",
        actor_id="agent-1",
    )
    service.decide_intake_escalation(
        created.complaint_id,
        IntakeEscalationDecisionRequest(
            decision="APPROVE",
            note="Disetujui agar Pusat dapat mengembalikan ke cabang.",
            priority="MEDIUM",
        ),
        actor_id="supervisor-1",
    )

    from app.modules.cm_batch1.schemas import (
        HqReturnRequest,
        IntakeEscalationRequestBody,
    )

    with pytest.raises(ValidationAppError):
        service.return_from_hq(
            created.complaint_id,
            HqReturnRequest(reasonCode="MISSING_ATTACHMENT", note="short"),
            actor_id="hq-1",
        )

    returned = service.return_from_hq(
        created.complaint_id,
        HqReturnRequest(
            reasonCode="MISSING_ATTACHMENT",
            note="Lampirkan bukti pembayaran dan KTP asli pelanggan.",
        ),
        actor_id="hq-1",
    )
    assert returned.intake_disposition == "RETURNED_TO_BRANCH"
    assert returned.hq_return_note is not None
    row = store.get(created.complaint_id)
    assert row is not None
    assert "Pengembalian Pusat" in (row.description or "")
    assert "[MISSING_ATTACHMENT]" in (row.description or "")

    re_requested = service.request_intake_escalation(
        created.complaint_id,
        IntakeEscalationRequestBody(
            reason="Berkas sudah dilengkapi: bukti bayar + KTP terlampir lengkap."
        ),
        actor_id="agent-1",
    )
    assert re_requested.intake_disposition == "ESCALATE_PENDING_APPROVAL"


def test_api_515_cancel_requires_note(service: CmBatch1Service) -> None:
    created = confirmed_create(
        service,
        CreateComplaintBatch1Request(
            customerId="CUST-10001",
            category="BILLING",
            channel="BRANCH",
            subject="Cancel note required unique",
            description="Keluhan unik cancel note\n\n---\nAlasan eskalasi:\nButuh pusat",
            intakeDisposition="ESCALATE_PENDING_APPROVAL",
            duplicateOverrideJustification=(
                "Lab override for cancel-note validation test row."
            ),
        ),
        request_id="esc-cancel-note",
        actor_id="agent-1",
    )
    service.decide_intake_escalation(
        created.complaint_id,
        IntakeEscalationDecisionRequest(
            decision="APPROVE",
            note="Disetujui agar bisa diuji validasi batal eskalasi.",
            priority="LOW",
        ),
        actor_id="supervisor-1",
    )
    with pytest.raises(ValidationAppError):
        service.decide_intake_escalation(
            created.complaint_id,
            IntakeEscalationDecisionRequest(decision="CANCEL", note="short"),
            actor_id="supervisor-1",
        )


def test_api_515_wrong_disposition_conflict(service: CmBatch1Service) -> None:
    created = confirmed_create(
        service,
        CreateComplaintBatch1Request(
            customerId="CUST-10001",
            category="BILLING",
            channel="BRANCH",
            subject="No escalate flag",
            description="Ordinary registered complaint",
            duplicateOverrideJustification=(
                "Lab override for wrong-disposition conflict guard."
            ),
        ),
        request_id="esc-wrong-1",
        actor_id="agent-1",
    )
    with pytest.raises(InvalidStateError):
        service.decide_intake_escalation(
            created.complaint_id,
            IntakeEscalationDecisionRequest(decision="APPROVE"),
            actor_id="supervisor-1",
        )


def test_api_515_list_filter_intake_disposition(service: CmBatch1Service) -> None:
    pending = confirmed_create(
        service,
        CreateComplaintBatch1Request(
            customerId="CUST-10001",
            category="BILLING",
            channel="BRANCH",
            subject="Pending filter unique A",
            description="Keluhan filter\n\n---\nAlasan eskalasi:\nFilter list perlu pusat",
            intakeDisposition="ESCALATE_PENDING_APPROVAL",
            duplicateOverrideJustification=(
                "Lab override for filter test pending disposition row."
            ),
        ),
        request_id="esc-filter-1",
        actor_id="agent-1",
    )
    confirmed_create(
        service,
        CreateComplaintBatch1Request(
            customerId="CUST-10001",
            category="BILLING",
            channel="BRANCH",
            subject="Ordinary filter unique B",
            description="No disposition",
            duplicateOverrideJustification=(
                "Lab override for filter test ordinary disposition row."
            ),
        ),
        request_id="esc-filter-2",
        actor_id="agent-1",
    )
    rows, total = service.list_complaints(
        page=1,
        page_size=20,
        intake_disposition="ESCALATE_PENDING_APPROVAL",
    )
    assert total >= 1
    assert all(r.intake_disposition == "ESCALATE_PENDING_APPROVAL" for r in rows)
    assert any(r.complaint_id == pending.complaint_id for r in rows)


def test_api_515_second_decision_invalid_state(service: CmBatch1Service) -> None:
    created = confirmed_create(
        service,
        CreateComplaintBatch1Request(
            customerId="CUST-10001",
            category="BILLING",
            channel="BRANCH",
            subject="Second decision",
            description="Keluhan second\n\n---\nAlasan eskalasi:\nSecond decision guard",
            intakeDisposition="ESCALATE_PENDING_APPROVAL",
            duplicateOverrideJustification=(
                "Lab override for second decision invalid-state guard."
            ),
        ),
        request_id="esc-second-1",
        actor_id="agent-1",
    )
    service.decide_intake_escalation(
        created.complaint_id,
        IntakeEscalationDecisionRequest(
            decision="APPROVE",
            note="Disetujui untuk uji guard keputusan kedua ke Pusat.",
            priority="CRITICAL",
        ),
        actor_id="supervisor-1",
    )
    with pytest.raises(InvalidStateError):
        service.decide_intake_escalation(
            created.complaint_id,
            IntakeEscalationDecisionRequest(
                decision="APPROVE",
                note="Disetujui ulang tidak boleh setelah APPROVED.",
                priority="HIGH",
            ),
            actor_id="supervisor-1",
        )


class _StubDirectory:
    """Directory port double — Mode B swaps the adapter, not this contract."""

    def __init__(self, names: dict[str, str]) -> None:
        self._names = names

    def display_names(self, user_ids: set[str]) -> dict[str, str]:
        return {uid: self._names[uid] for uid in user_ids if uid in self._names}


def test_pic_name_exposed_on_list_and_detail(store: Batch1Store) -> None:
    """Supervisor/Manager must see who handled intake (createdBy → createdByName)."""
    service = CmBatch1Service(
        customer_provider=StubCustomerProvider(),
        guard=EnumerationGuard(max_failures=3, window_seconds=60, block_seconds=30),
        store=store,
        user_directory=_StubDirectory({"agent-77": "Ayu Kusuma"}),
    )
    created = confirmed_create(
        service,
        CreateComplaintBatch1Request(
            customerId="CUST-10001",
            category="BILLING",
            channel="BRANCH",
            subject="PIC visibility unique subject",
            description="Keluhan untuk uji PIC",
            duplicateOverrideJustification=(
                "Lab override for PIC visibility assertion row."
            ),
        ),
        request_id="pic-1",
        actor_id="agent-77",
    )
    assert created.created_by == "agent-77"
    assert created.created_by_name == "Ayu Kusuma"

    rows, _ = service.list_complaints(page=1, page_size=20)
    row = next(r for r in rows if r.complaint_id == created.complaint_id)
    assert row.created_by_name == "Ayu Kusuma"


def test_pic_name_absent_when_directory_has_no_entry(service: CmBatch1Service) -> None:
    """Unknown actor keys degrade to null — never block the Aggregate read."""
    created = confirmed_create(
        service,
        CreateComplaintBatch1Request(
            customerId="CUST-10001",
            category="BILLING",
            channel="BRANCH",
            subject="PIC unresolved unique subject",
            description="Keluhan tanpa direktori",
            duplicateOverrideJustification=(
                "Lab override for unresolved PIC assertion row."
            ),
        ),
        request_id="pic-2",
        actor_id="agent-unknown",
    )
    assert created.created_by == "agent-unknown"
    assert created.created_by_name is None


class _FakeTimelineRepo:
    def __init__(self, entries: list) -> None:
        self._entries = entries

    def list_by_aggregate(self, *, aggregate_type, aggregate_id, page=1, page_size=100):
        _ = aggregate_type, aggregate_id, page, page_size
        return list(self._entries), len(self._entries)


def _timeline_entry(
    event_type: str,
    metadata: dict,
    *,
    minute: int,
    actor: str,
    actor_name: str | None = None,
):
    from datetime import UTC, datetime

    from app.modules.timeline.domain.entity import TimelineEntry

    return TimelineEntry(
        id=uuid.uuid4(),
        aggregate_type="Complaint",
        aggregate_id=uuid.uuid4(),
        event_type=event_type,
        title=event_type,
        description=None,
        actor_type="USER",
        actor_id=actor,
        actor_name=actor_name,
        metadata=metadata,
        created_at=datetime(2026, 8, 7, 9, minute, tzinfo=UTC),
    )


def test_intake_history_is_chronological_with_stable_codes() -> None:
    """Every decision is its own entry — the description blob cannot show this."""
    from app.modules.cm_batch1.history import CmBatch1HistoryService

    entries = [
        _timeline_entry("ComplaintRegistered", {}, minute=1, actor="agent-77"),
        _timeline_entry(
            "IntakeDispositionRecorded",
            {"intakeDisposition": "ESCALATE_PENDING_APPROVAL"},
            minute=2,
            actor="agent-77",
        ),
        _timeline_entry(
            "IntakeEscalationDecided",
            {"decision": "CANCEL"},
            minute=3,
            actor="spv-1",
        ),
        _timeline_entry(
            "IntakeEscalationDecided",
            {"decision": "RE_ESCALATE"},
            minute=4,
            actor="agent-77",
        ),
        _timeline_entry(
            "IntakeEscalationDecided",
            {"decision": "APPROVE", "priority": "HIGH"},
            minute=5,
            actor="spv-1",
        ),
    ]
    service = CmBatch1HistoryService(
        _FakeTimelineRepo(entries),
        user_directory=_StubDirectory({"agent-77": "Ayu Kusuma", "spv-1": "Budi"}),
    )
    items = service.list_history(str(uuid.uuid4()))

    assert [i.event_code for i in items] == [
        "REGISTERED",
        "ESCALATION_REQUESTED",
        "ESCALATION_CANCELLED",
        "ESCALATION_RE_REQUESTED",
        "ESCALATION_APPROVED",
    ]
    assert [i.actor_name for i in items] == [
        "Ayu Kusuma",
        "Ayu Kusuma",
        "Budi",
        "Ayu Kusuma",
        "Budi",
    ]
    assert items[-1].priority == "HIGH"
    assert items[0].occurred_at < items[-1].occurred_at


def test_intake_history_branch_closed_after_same_burst_attachments() -> None:
    """Create+close then bind files: narrative puts Ditutup after ATTACHMENT_BOUND."""
    from datetime import UTC, datetime, timedelta

    from app.modules.cm_batch1.history import CmBatch1HistoryService
    from app.modules.timeline.domain.entity import TimelineEntry

    base = datetime(2026, 8, 11, 8, 2, tzinfo=UTC)
    agg = uuid.uuid4()

    def entry(event_type: str, metadata: dict, *, offset_s: float) -> TimelineEntry:
        return TimelineEntry(
            id=uuid.uuid4(),
            aggregate_type="Complaint",
            aggregate_id=agg,
            event_type=event_type,
            title=event_type,
            description=None,
            actor_type="USER",
            actor_id="admin-1",
            actor_name=None,
            metadata=metadata,
            created_at=base + timedelta(seconds=offset_s),
        )

    raw = [
        entry("ComplaintRegistered", {"priority": "MEDIUM"}, offset_s=0),
        entry(
            "IntakeDispositionRecorded",
            {"intakeDisposition": "BRANCH_CLOSED", "note": "adsads", "priority": "MEDIUM"},
            offset_s=0.1,
        ),
        entry("AttachmentBound", {}, offset_s=1.5),
    ]
    service = CmBatch1HistoryService(
        _FakeTimelineRepo(raw),
        user_directory=_StubDirectory({"admin-1": "ECMP Lab Admin"}),
    )
    items = service.list_history(str(agg))
    assert [i.event_code for i in items] == [
        "REGISTERED",
        "ATTACHMENT_BOUND",
        "BRANCH_CLOSED",
    ]
    assert items[-1].note == "adsads"


def test_intake_history_empty_for_unknown_complaint_id() -> None:
    from app.modules.cm_batch1.history import CmBatch1HistoryService

    service = CmBatch1HistoryService(_FakeTimelineRepo([]))
    assert service.list_history("not-a-uuid") == []


def test_history_maps_case_events_instead_of_other() -> None:
    from app.modules.cm_batch1.history import event_code

    created = _timeline_entry("CaseCreated", {"caseNumber": "CASE-1"}, minute=1, actor="a")
    started = _timeline_entry("CaseWorkStarted", {"caseStatus": "IN_PROGRESS"}, minute=2, actor="a")
    closed = _timeline_entry("CaseClosed", {"caseStatus": "CLOSED"}, minute=4, actor="a")
    unknown = _timeline_entry("SomethingUnmapped", {}, minute=3, actor="a")
    assert event_code(created) == "CASE_CREATED"
    assert event_code(started) == "CASE_WORK_STARTED"
    assert event_code(closed) == "CASE_CLOSED"
    assert event_code(unknown) == "OTHER"
    continued = _timeline_entry("HandlingContinued", {}, minute=5, actor="a")
    taken = _timeline_entry("HandlingTakenOver", {}, minute=6, actor="b")
    assert event_code(continued) == "HANDLING_CONTINUED"
    assert event_code(taken) == "HANDLING_TAKEN_OVER"


def test_history_replaces_uuid_actor_name_from_directory() -> None:
    from app.modules.cm_batch1.history import CmBatch1HistoryService

    officer_id = str(uuid.uuid4())
    entries = [
        _timeline_entry(
            "ComplaintRegistered",
            {},
            minute=1,
            actor=officer_id,
            actor_name=officer_id,
        )
    ]
    service = CmBatch1HistoryService(
        _FakeTimelineRepo(entries),
        user_directory=_StubDirectory({officer_id: "Ahmad Santoso"}),
    )
    items = service.list_history(str(uuid.uuid4()))
    assert items[0].actor_name == "Ahmad Santoso"


def test_history_directory_failure_does_not_raise() -> None:
    from app.modules.cm_batch1.history import CmBatch1HistoryService

    class _BoomDirectory:
        def display_names(self, user_ids: set[str]) -> dict[str, str]:
            raise RuntimeError("directory down")

    entries = [_timeline_entry("ComplaintRegistered", {}, minute=1, actor="agent-1")]
    service = CmBatch1HistoryService(
        _FakeTimelineRepo(entries),
        user_directory=_BoomDirectory(),
    )
    items = service.list_history(str(uuid.uuid4()))
    assert items[0].actor_name is None


def test_history_hides_work_started_but_lists_case_created() -> None:
    from app.modules.cm_batch1.history import CmBatch1HistoryService

    entries = [
        _timeline_entry("ComplaintRegistered", {}, minute=1, actor="a"),
        _timeline_entry("CaseCreated", {"caseNumber": "CASE-1"}, minute=2, actor="a"),
        _timeline_entry("HandlingContinued", {}, minute=3, actor="a"),
        _timeline_entry("CaseWorkStarted", {}, minute=4, actor="a"),
        _timeline_entry("CaseResolved", {"caseNumber": "CASE-1"}, minute=5, actor="a"),
        _timeline_entry("CaseOwnerAccepted", {"caseNumber": "CASE-1"}, minute=6, actor="a"),
        _timeline_entry("CaseClosed", {"caseNumber": "CASE-1"}, minute=7, actor="a"),
    ]
    service = CmBatch1HistoryService(_FakeTimelineRepo(entries))
    items = service.list_history(str(uuid.uuid4()))
    assert [i.event_code for i in items] == [
        "REGISTERED",
        "CASE_CREATED",
        "HANDLING_CONTINUED",
        "CASE_CLOSED",
    ]
    assert items[1].case_number == "CASE-1"


def test_history_carries_intake_action_on_case_created() -> None:
    from app.modules.cm_batch1.history import CmBatch1HistoryService

    entries = [
        _timeline_entry(
            "CaseCreated",
            {"caseNumber": "CASE-2", "intakeAction": "escalate", "note": "Perlu Pusat"},
            minute=1,
            actor="a",
        )
    ]
    items = CmBatch1HistoryService(_FakeTimelineRepo(entries)).list_history(
        str(uuid.uuid4())
    )
    assert items[0].intake_action == "escalate"
    assert items[0].note == "Perlu Pusat"


def test_history_carries_note_and_priority_per_event() -> None:
    """Each row must stand alone: who, when, priority, and the note itself."""
    from app.modules.cm_batch1.history import CmBatch1HistoryService

    entries = [
        _timeline_entry(
            "IntakeEscalationDecided",
            {
                "decision": "CANCEL",
                "note": "Pelanggan menarik permintaan eskalasi hari ini.",
            },
            minute=1,
            actor="spv-1",
        ),
        _timeline_entry(
            "IntakeEscalationDecided",
            {
                "decision": "APPROVE",
                "priority": "HIGH",
                "note": "Disetujui, Pusat menangani karena nilai transaksi besar.",
            },
            minute=2,
            actor="spv-1",
        ),
    ]
    service = CmBatch1HistoryService(
        _FakeTimelineRepo(entries),
        user_directory=_StubDirectory({"spv-1": "Budi"}),
    )
    items = service.list_history(str(uuid.uuid4()))

    assert items[0].note == "Pelanggan menarik permintaan eskalasi hari ini."
    assert items[0].priority is None
    assert items[1].note.startswith("Disetujui, Pusat menangani")
    assert items[1].priority == "HIGH"


def test_event_note_is_clipped_not_dropped() -> None:
    from app.modules.cm_batch1 import event_factory as ev

    assert ev.clip_note("  ") is None
    assert ev.clip_note(" catatan ") == "catatan"
    long_note = "x" * 5000
    clipped = ev.clip_note(long_note)
    assert clipped is not None
    assert len(clipped) == 4001 and clipped.endswith("…")


def test_api_516_hq_accept_without_schedule(
    service: CmBatch1Service, store: Batch1Store
) -> None:
    from app.modules.cm_batch1.schemas import HqAcceptRequest

    created = confirmed_create(
        service,
        CreateComplaintBatch1Request(
            customerId="CUST-10001",
            category="BILLING",
            channel="BRANCH",
            subject="HQ accept only",
            description="Keluhan\n\n---\nAlasan eskalasi:\nButuh terima pusat saja",
            intakeDisposition="ESCALATE_PENDING_APPROVAL",
            duplicateOverrideJustification=(
                "Lab override for HQ accept-only (no schedule) path."
            ),
        ),
        request_id="esc-hq-accept-only-1",
        actor_id="agent-1",
    )
    with pytest.raises(InvalidStateError):
        service.accept_at_hq(
            created.complaint_id,
            HqAcceptRequest(note="Belum disetujui supervisor cabang."),
            actor_id="hq-1",
        )
    service.decide_intake_escalation(
        created.complaint_id,
        IntakeEscalationDecisionRequest(
            decision="APPROVE",
            note="Disetujui agar Pusat menerima tanpa menjadwalkan dulu.",
            priority="HIGH",
        ),
        actor_id="supervisor-1",
    )
    with pytest.raises(ValidationAppError):
        service.accept_at_hq(
            created.complaint_id,
            HqAcceptRequest(note="terlalu pendek"),
            actor_id="hq-1",
        )
    with pytest.raises(NotFoundError):
        service.accept_at_hq(
            str(uuid.uuid4()),
            HqAcceptRequest(),
            actor_id="hq-1",
        )
    accepted = service.accept_at_hq(
        created.complaint_id,
        HqAcceptRequest(),
        actor_id="hq-1",
    )
    assert accepted.hq_accepted_at is not None
    assert accepted.intake_disposition == "ESCALATE_APPROVED"
    row = store.get(created.complaint_id)
    assert row is not None
    assert "Penerimaan Pusat:" in (row.description or "")
    with pytest.raises(InvalidStateError):
        service.accept_at_hq(
            created.complaint_id,
            HqAcceptRequest(note="Sudah diterima sebelumnya oleh Pusat."),
            actor_id="hq-1",
        )
