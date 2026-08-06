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
from app.core.errors import InvalidStateError, RateLimitedError, ValidationAppError
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
    assert created.complaint_number.startswith("CM-")


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
        assert "resolution" in str(exc).lower() or "BRANCH_CLOSED" in str(
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
            "description": "desc",
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
            "description": "desc",
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
    assert created.complaint_number.startswith("CM-")

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
            "description": "Detail",
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
            description="Ajuan eskalasi: butuh pusat karena kompleks",
            intakeDisposition="ESCALATE_PENDING_APPROVAL",
        ),
        request_id="esc-approve-1",
        actor_id="agent-1",
    )
    assert created.intake_disposition == "ESCALATE_PENDING_APPROVAL"
    assert created.status == "REGISTERED"

    decided = service.decide_intake_escalation(
        created.complaint_id,
        IntakeEscalationDecisionRequest(decision="APPROVE", note="ok lanjut"),
        actor_id="supervisor-1",
    )
    assert decided.status == "REGISTERED"
    assert decided.intake_disposition == "ESCALATE_APPROVED"
    assert decided.case_created is False
    row = store.get(created.complaint_id)
    assert row is not None
    assert row.intake_disposition == "ESCALATE_APPROVED"


def test_api_515_reject_requires_note(service: CmBatch1Service) -> None:
    created = confirmed_create(
        service,
        CreateComplaintBatch1Request(
            customerId="CUST-10001",
            category="BILLING",
            channel="BRANCH",
            subject="Escalate reject",
            description="Ajuan eskalasi: uji tolak",
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


def test_api_515_wrong_disposition_conflict(service: CmBatch1Service) -> None:
    created = confirmed_create(
        service,
        CreateComplaintBatch1Request(
            customerId="CUST-10001",
            category="BILLING",
            channel="BRANCH",
            subject="No escalate flag",
            description="Ordinary registered complaint",
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
            description="Ajuan eskalasi: filter list",
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
            description="Ajuan eskalasi: second decision guard",
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
        IntakeEscalationDecisionRequest(decision="APPROVE"),
        actor_id="supervisor-1",
    )
    with pytest.raises(InvalidStateError):
        service.decide_intake_escalation(
            created.complaint_id,
            IntakeEscalationDecisionRequest(decision="APPROVE"),
            actor_id="supervisor-1",
        )
