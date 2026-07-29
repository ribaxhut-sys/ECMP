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
from app.core.errors import RateLimitedError, ValidationAppError
from app.db.base import Base
from app.main import create_app
from app.integrations.customer import StubCustomerProvider
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
)
from app.modules.cm_batch1.service import CmBatch1Service
from app.modules.cm_batch1.store import Batch1Store

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
        CustomerSearchRequest(customerNumber="CN-10001"),
        principal_key="p1",
    )
    assert result.verification_status == "verified"
    assert result.customer_id == "CUST-10001"
    assert result.enumeration_outcome == "allowed"


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
            CustomerSearchRequest(customerNumber="CN-10001"),
            principal_key="p1",
        )


def test_tc_cm_fr002_07_two_keys_rejected(service: CmBatch1Service) -> None:
    with pytest.raises(ValidationAppError) as exc:
        service.search_customer(
            CustomerSearchRequest(customerNumber="CN-10001", identityNumber="ID-10001"),
            principal_key="p1",
        )
    assert "Exactly one" in exc.value.message


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
        CustomerSearchRequest(customerNumber="CN-10001"),
        principal_key="p1",
    )
    assert result.as_of is not None
    view = service.customer_360_minimum("CUST-10001")
    assert view.as_of is not None
    assert view.complaint_count == 0
    assert "displayName" in view.profile


def test_tc_cm_fr001_01_create_registered_no_case(service: CmBatch1Service) -> None:
    created = service.create_complaint(
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


def test_tc_cm_fr001_02_customer_id_only(service: CmBatch1Service) -> None:
    created = service.create_complaint(
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
        service.create_complaint(
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


def test_tc_cm_fr001_10_request_id_replay(service: CmBatch1Service) -> None:
    first = service.create_complaint(
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
    second = service.create_complaint(
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
    first = service.create_complaint(
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
    second = service.create_complaint(
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
    service.create_complaint(
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
            user_id=uuid.uuid4(),
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
        json={"customerNumber": "CN-10001"},
    )
    assert search.status_code == 200, search.text
    body = search.json()["data"]
    assert body["customerId"] == "CUST-10001"

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


# --- S2 Task 01 persistence ---


def test_s2_persistence_create_get_idempotent(persistent_service: CmBatch1Service) -> None:
    created = persistent_service.create_complaint(
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

    replay = persistent_service.create_complaint(
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

    persistent_service.create_complaint(
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

    replay_ch = persistent_service.create_complaint(
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
    created = service.create_complaint(
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
    assert "Reason Required" in exc.value.message or "justification" in exc.value.message.lower()


def test_tc_cm_fr003_04_override_with_justification(
    service: CmBatch1Service,
) -> None:
    _seed_complaint(service, request_id="dup-ov-1")
    created = service.create_complaint(
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
        service.create_complaint(
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
    first = persistent_service.create_complaint(
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
