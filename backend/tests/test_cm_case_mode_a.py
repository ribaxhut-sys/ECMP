"""CAP-008 Mode A Case Management — FR-001…FR-006 integration tests."""

from __future__ import annotations

import uuid
from collections.abc import Generator

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker
from sqlalchemy.pool import StaticPool

from app.core.authorization.authentication import get_current_principal
from app.core.authorization.principal import Principal
from app.core.errors import ApiError
from app.db.base import Base
from app.db.session import get_db_session
from app.main import create_app
from app.modules.cm_batch1.models import CmBatch1ComplaintORM
from app.modules.cm_case.api.router import get_case_service
from app.modules.cm_case.application.dto import (
    CloseCaseCommand,
    CreateCaseCommand,
    RecordAcceptanceCommand,
    ResolveCaseCommand,
    UpdateStatusCommand,
)
from app.modules.cm_case.application.services import (
    AuditTimelineSideEffects,
    CaseApplicationService,
    NoOpSideEffects,
)
from app.modules.cm_case.domain.aggregate import CaseAggregate
from app.modules.cm_case.domain.value_objects import CaseNumber, CaseStatus
from app.modules.cm_case.infrastructure.orm import (
    CmCaseAcceptanceORM,
    CmCaseNumberCounterORM,
    CmCaseORM,
    CmCaseResolutionORM,
)
from app.modules.cm_case.infrastructure.repository import SqlAlchemyCaseRepository

_TABLES = [
    CmBatch1ComplaintORM.__table__,
    CmCaseORM.__table__,
    CmCaseResolutionORM.__table__,
    CmCaseAcceptanceORM.__table__,
    CmCaseNumberCounterORM.__table__,
]


@pytest.fixture()
def db_session() -> Generator[Session, None, None]:
    engine = create_engine(
        "sqlite://",
        future=True,
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    Base.metadata.create_all(engine, tables=_TABLES)
    factory = sessionmaker(bind=engine, autoflush=False, autocommit=False, future=True)
    session = factory()
    try:
        yield session
    finally:
        session.close()
        engine.dispose()


def _seed_complaint(
    session: Session,
    *,
    status: str = "REGISTERED",
    owning_unit_id: str | None = None,
) -> str:
    row = CmBatch1ComplaintORM(
        id=uuid.uuid4(),
        complaint_number=f"CMP-{uuid.uuid4().hex[:8].upper()}",
        customer_id="CUST-10001",
        category="BILLING",
        channel="WALK_IN",
        subject="Seed complaint",
        description="Seed",
        priority="MEDIUM",
        status=status,
        case_created=False,
        created_by="seed",
        owning_unit_id=owning_unit_id,
    )
    session.add(row)
    session.commit()
    return str(row.id)


@pytest.fixture()
def service(db_session: Session) -> CaseApplicationService:
    return CaseApplicationService(
        SqlAlchemyCaseRepository(db_session),
        side_effects=NoOpSideEffects(),
    )


def test_fr001_create_case_created_status(service: CaseApplicationService, db_session: Session) -> None:
    complaint_id = _seed_complaint(db_session)
    dto = service.create_case(
        CreateCaseCommand(
            complaint_id=complaint_id,
            case_type="BILLING",
            subject="Tagihan",
            description="Koreksi tagihan",
            priority="HIGH",
            actor_id="actor-1",
        )
    )
    assert dto.status == "CREATED"
    assert dto.case_number.startswith("CASE-")
    assert dto.sla_countdown_active is False
    assert dto.owning_unit_id is None


def test_create_and_handle_claim_timeline_events(db_session: Session) -> None:
    from unittest.mock import MagicMock

    effects = MagicMock()
    service = CaseApplicationService(
        SqlAlchemyCaseRepository(db_session),
        side_effects=effects,
    )
    complaint_id = _seed_complaint(db_session)
    dto = service.create_case(
        CreateCaseCommand(
            complaint_id=complaint_id,
            case_type="BILLING",
            subject="Tagihan",
            description="Koreksi tagihan",
            priority="HIGH",
            actor_id="seed",
        )
    )
    names = [
        call.kwargs["event_name"]
        for call in effects.record_case_event.call_args_list
    ]
    assert names == ["CaseCreated", "HandlingContinued"]
    assert dto.handling_claimed_by == "seed"

    effects.record_case_event.reset_mock()
    with pytest.raises(ApiError) as claimed_exc:
        service.update_status(
            UpdateStatusCommand(
                case_id=dto.case_id,
                to_status=dto.status,
                actor_id="other-agent",
                reason="HANDLE_CLAIM",
            )
        )
    assert claimed_exc.value.code == "HANDLING_ALREADY_CLAIMED"

    reassigned = service.update_status(
        UpdateStatusCommand(
            case_id=dto.case_id,
            to_status=dto.status,
            actor_id="supervisor-1",
            reason="HANDLE_REASSIGN",
            handling_claimed_by="other-agent",
            actor_can_reassign=True,
        )
    )
    assert reassigned.handling_claimed_by == "other-agent"
    names = [
        call.kwargs["event_name"]
        for call in effects.record_case_event.call_args_list
    ]
    assert names == ["HandlingTakenOver"]

    parent = db_session.get(CmBatch1ComplaintORM, uuid.UUID(complaint_id))
    assert parent is not None
    assert parent.status == "IN_PROGRESS"
    assert parent.case_created is True


def test_handling_claim_guards_and_same_officer_reclaim(
    service: CaseApplicationService, db_session: Session
) -> None:
    complaint_id = _seed_complaint(db_session)
    created = service.create_case(
        CreateCaseCommand(
            complaint_id=complaint_id,
            case_type="BILLING",
            subject="Claim guards",
            description="desc",
            priority="MEDIUM",
            actor_id="officer-1",
        )
    )
    with pytest.raises(ApiError) as forbidden:
        service.update_status(
            UpdateStatusCommand(
                case_id=created.case_id,
                to_status=created.status,
                actor_id="officer-1",
                reason="HANDLE_REASSIGN",
                handling_claimed_by="officer-2",
                actor_can_reassign=False,
            )
        )
    assert forbidden.value.code == "HANDLING_REASSIGN_FORBIDDEN"

    with pytest.raises(ApiError) as empty_target:
        service.update_status(
            UpdateStatusCommand(
                case_id=created.case_id,
                to_status=created.status,
                actor_id="supervisor-1",
                reason="HANDLE_REASSIGN",
                handling_claimed_by="  ",
                actor_can_reassign=True,
            )
        )
    assert empty_target.value.status_code == 400

    with pytest.raises(ApiError) as other_worker:
        service.update_status(
            UpdateStatusCommand(
                case_id=created.case_id,
                to_status="IN_PROGRESS",
                actor_id="officer-2",
            )
        )
    assert other_worker.value.code == "HANDLING_CLAIMER_ONLY"

    row = db_session.get(CmCaseORM, uuid.UUID(created.case_id))
    assert row is not None
    row.handling_claimed_by = None
    db_session.commit()

    with pytest.raises(ApiError) as need_claim:
        service.update_status(
            UpdateStatusCommand(
                case_id=created.case_id,
                to_status="IN_PROGRESS",
                actor_id="officer-2",
            )
        )
    assert need_claim.value.code == "HANDLING_CLAIM_REQUIRED"

    claimed = service.update_status(
        UpdateStatusCommand(
            case_id=created.case_id,
            to_status=created.status,
            actor_id="officer-2",
            reason="HANDLE_CLAIM",
        )
    )
    assert claimed.handling_claimed_by == "officer-2"

    again = service.update_status(
        UpdateStatusCommand(
            case_id=created.case_id,
            to_status=claimed.status,
            actor_id="officer-2",
            reason="HANDLE_CLAIM",
        )
    )
    assert again.handling_claimed_by == "officer-2"


def test_handling_claim_rejected_when_case_terminal(
    service: CaseApplicationService, db_session: Session
) -> None:
    complaint_id = _seed_complaint(db_session)
    created = service.create_case(
        CreateCaseCommand(
            complaint_id=complaint_id,
            case_type="BILLING",
            subject="Terminal claim",
            description="desc",
            priority="MEDIUM",
            actor_id="officer-1",
        )
    )
    cancelled = service.update_status(
        UpdateStatusCommand(
            case_id=created.case_id,
            to_status="CANCELLED",
            actor_id="officer-1",
            cancel_reason="DUPLICATE",
            reason="DUPLICATE",
        )
    )
    assert cancelled.status == "CANCELLED"
    with pytest.raises(ApiError) as claim_exc:
        service.update_status(
            UpdateStatusCommand(
                case_id=created.case_id,
                to_status="CANCELLED",
                actor_id="officer-1",
                reason="HANDLE_CLAIM",
            )
        )
    assert "terminal" in str(claim_exc.value).lower()
    with pytest.raises(ApiError) as reassign_exc:
        service.update_status(
            UpdateStatusCommand(
                case_id=created.case_id,
                to_status="CANCELLED",
                actor_id="supervisor-1",
                reason="HANDLE_REASSIGN",
                handling_claimed_by="officer-2",
                actor_can_reassign=True,
            )
        )
    assert "terminal" in str(reassign_exc.value).lower()


def test_cancelled_requires_reason(
    service: CaseApplicationService, db_session: Session
) -> None:
    complaint_id = _seed_complaint(db_session)
    created = service.create_case(
        CreateCaseCommand(
            complaint_id=complaint_id,
            case_type="BILLING",
            subject="Cancel reason",
            description="desc",
            priority="MEDIUM",
            actor_id="officer-1",
        )
    )
    with pytest.raises(ApiError) as exc:
        service.update_status(
            UpdateStatusCommand(
                case_id=created.case_id,
                to_status="CANCELLED",
                actor_id="officer-1",
                reason="",
            )
        )
    assert exc.value.status_code == 400


def test_resolve_reject_and_invalid_commands(
    service: CaseApplicationService, db_session: Session
) -> None:
    complaint_id = _seed_complaint(db_session)
    created = service.create_case(
        CreateCaseCommand(
            complaint_id=complaint_id,
            case_type="BILLING",
            subject="Reject proposal",
            description="desc",
            priority="MEDIUM",
            destination_unit_id="UNIT-1",
            actor_id="officer-1",
        )
    )
    service.update_status(
        UpdateStatusCommand(
            case_id=created.case_id,
            to_status="IN_PROGRESS",
            actor_id="officer-1",
        )
    )
    service.resolve(
        ResolveCaseCommand(
            case_id=created.case_id,
            action="PROPOSE",
            comment="Usulan",
            resolution_code="FIXED",
            summary="Selesai",
            actor_id="officer-1",
        )
    )
    with pytest.raises(ApiError):
        service.resolve(
            ResolveCaseCommand(
                case_id=created.case_id,
                action="NOPE",
                comment="x",
                actor_id="officer-1",
            )
        )
    rejected = service.resolve(
        ResolveCaseCommand(
            case_id=created.case_id,
            action="REJECT",
            comment="Belum cukup",
            rejection_reason="INCOMPLETE_EVIDENCE",
            actor_id="supervisor-1",
        )
    )
    assert rejected.status == "IN_PROGRESS"
    assert rejected.resolution is not None
    assert rejected.resolution.status == "REJECTED"
    with pytest.raises(ApiError):
        service.record_acceptance(
            RecordAcceptanceCommand(
                case_id=created.case_id,
                party="NOT_A_PARTY",
                decision="ACCEPT",
                actor_id="hq-1",
            )
        )
    with pytest.raises(ApiError):
        service.record_acceptance(
            RecordAcceptanceCommand(
                case_id=created.case_id,
                party="OWNER",
                decision="MAYBE",
                actor_id="hq-1",
            )
        )
    with pytest.raises(ApiError) as missing:
        service.get_case(str(uuid.uuid4()))
    assert missing.value.status_code == 404
    with pytest.raises(ApiError) as ctx_exc:
        service.get_case(created.case_id, complaint_id_context=str(uuid.uuid4()))
    assert ctx_exc.value.code == "CASE_COMPLAINT_MEMBERSHIP_MISMATCH"


def test_fr001_create_with_unit_assigned(service: CaseApplicationService, db_session: Session) -> None:
    complaint_id = _seed_complaint(db_session)
    dto = service.create_case(
        CreateCaseCommand(
            complaint_id=complaint_id,
            case_type="BILLING",
            subject="Tagihan",
            description="Koreksi",
            priority="MEDIUM",
            destination_unit_id="UNIT-JKT-01",
            actor_id="actor-1",
        )
    )
    assert dto.status == "ASSIGNED"
    assert dto.owning_unit_id == "UNIT-JKT-01"


def test_fr001_reject_assigned_user(service: CaseApplicationService, db_session: Session) -> None:
    complaint_id = _seed_complaint(db_session)
    with pytest.raises(ApiError) as exc:
        service.create_case(
            CreateCaseCommand(
                complaint_id=complaint_id,
                case_type="BILLING",
                subject="X",
                description="Y",
                priority="LOW",
                assigned_user_id="user-9",
                actor_id="actor-1",
            )
        )
    assert exc.value.code == "ASSIGNED_USER_NOT_ALLOWED_MODE_A"


def test_fr001_reject_closed_complaint(service: CaseApplicationService, db_session: Session) -> None:
    complaint_id = _seed_complaint(db_session, status="CLOSED")
    with pytest.raises(ApiError) as exc:
        service.create_case(
            CreateCaseCommand(
                complaint_id=complaint_id,
                case_type="BILLING",
                subject="X",
                description="Y",
                priority="LOW",
                actor_id="actor-1",
            )
        )
    assert exc.value.code == "COMPLAINT_CLOSED"


def test_fr002_add_case_and_max_five(service: CaseApplicationService, db_session: Session) -> None:
    complaint_id = _seed_complaint(db_session, status="IN_PROGRESS")
    for i in range(5):
        service.create_case(
            CreateCaseCommand(
                complaint_id=complaint_id,
                case_type="BILLING",
                subject=f"Case {i}",
                description="desc",
                priority="MEDIUM",
                actor_id="actor-1",
            )
        )
    with pytest.raises(ApiError) as exc:
        service.create_case(
            CreateCaseCommand(
                complaint_id=complaint_id,
                case_type="BILLING",
                subject="Overflow",
                description="desc",
                priority="MEDIUM",
                actor_id="actor-1",
            )
        )
    assert exc.value.code == "MAX_CASES_EXCEEDED"


def test_fr003_view_and_membership(service: CaseApplicationService, db_session: Session) -> None:
    complaint_id = _seed_complaint(db_session)
    other = _seed_complaint(db_session)
    created = service.create_case(
        CreateCaseCommand(
            complaint_id=complaint_id,
            case_type="BILLING",
            subject="View me",
            description="desc",
            priority="MEDIUM",
            actor_id="actor-1",
        )
    )
    viewed = service.get_case(created.case_id, complaint_id_context=complaint_id)
    assert viewed.case_id == created.case_id
    with pytest.raises(ApiError) as exc:
        service.get_case(created.case_id, complaint_id_context=other)
    assert exc.value.code == "CASE_COMPLAINT_MEMBERSHIP_MISMATCH"


def test_fr004_to_fr006_happy_path(service: CaseApplicationService, db_session: Session) -> None:
    complaint_id = _seed_complaint(db_session)
    created = service.create_case(
        CreateCaseCommand(
            complaint_id=complaint_id,
            case_type="BILLING",
            subject="Lifecycle",
            description="desc",
            priority="MEDIUM",
            destination_unit_id="UNIT-1",
            actor_id="actor-1",
        )
    )
    assert created.status == "ASSIGNED"
    started = service.update_status(
        UpdateStatusCommand(
            case_id=created.case_id,
            to_status="IN_PROGRESS",
            actor_id="actor-1",
        )
    )
    assert started.status == "IN_PROGRESS"

    with pytest.raises(ApiError) as exc:
        service.update_status(
            UpdateStatusCommand(
                case_id=created.case_id,
                to_status="PENDING",
                actor_id="actor-1",
            )
        )
    assert exc.value.code == "STATE_NOT_EXPOSED_MODE_A"

    proposed = service.resolve(
        ResolveCaseCommand(
            case_id=created.case_id,
            action="PROPOSE",
            comment="Catatan kerja",
            resolution_code="FIXED",
            summary="Selesai",
            actor_id="actor-1",
        )
    )
    assert proposed.status == "IN_PROGRESS"
    assert proposed.resolution is not None
    assert proposed.resolution.status == "PENDING_APPROVAL"

    resolved = service.resolve(
        ResolveCaseCommand(
            case_id=created.case_id,
            action="ACCEPT",
            comment="Disetujui",
            resolution_code="FIXED",
            summary="Selesai",
            actor_id="supervisor-1",
        )
    )
    assert resolved.status == "RESOLVED"
    # F4 closure rule — reaching RESOLVED via ACCEPT already counts as the
    # Handling Unit's acceptance; Owner's is still outstanding.
    assert resolved.handling_unit_acceptance is not None
    assert resolved.handling_unit_acceptance.decision == "ACCEPT"
    assert resolved.owner_acceptance is None

    # RESOLVED alone must not be enough to Close (F4 closure rule).
    with pytest.raises(ApiError) as exc:
        service.close(CloseCaseCommand(case_id=created.case_id, actor_id="supervisor-1"))
    assert exc.value.code == "OWNER_ACCEPTANCE_REQUIRED"

    owner_accepted = service.record_acceptance(
        RecordAcceptanceCommand(
            case_id=created.case_id,
            party="OWNER",
            decision="ACCEPT",
            actor_id="owner-1",
        )
    )
    # Second ACCEPT (Owner) triggers CLOSED — no third approval step.
    assert owner_accepted.status == "CLOSED"
    assert owner_accepted.owner_acceptance is not None
    assert owner_accepted.owner_acceptance.decision == "ACCEPT"
    assert owner_accepted.closed_by == "owner-1"
    # Compatibility close is idempotent once dual-acceptance closed the Case.
    closed = service.close(
        CloseCaseCommand(case_id=created.case_id, actor_id="supervisor-1")
    )
    assert closed.status == "CLOSED"
    parent = db_session.get(CmBatch1ComplaintORM, uuid.UUID(complaint_id))
    assert parent is not None
    # Mode A 2026-08-12: sole Case CLOSED → Aggregate CLOSED.
    assert parent.status == "CLOSED"
    assert (parent.intake_disposition or "").upper() == "BRANCH_CLOSED"


def test_parent_stays_open_while_sibling_case_active(
    service: CaseApplicationService, db_session: Session
) -> None:
    complaint_id = _seed_complaint(db_session, owning_unit_id="UPPPD-GAMBIR")
    first = service.create_case(
        CreateCaseCommand(
            complaint_id=complaint_id,
            case_type="BILLING",
            subject="First",
            description="d",
            priority="MEDIUM",
            destination_unit_id="UPPPD-GAMBIR",
            actor_id="handler-1",
        )
    )
    second = service.create_case(
        CreateCaseCommand(
            complaint_id=complaint_id,
            case_type="BILLING",
            subject="Second",
            description="d",
            priority="MEDIUM",
            destination_unit_id="UPPPD-GAMBIR",
            actor_id="handler-1",
        )
    )
    _resolve_to_resolved(service, first.case_id)
    service.record_acceptance(
        RecordAcceptanceCommand(
            case_id=first.case_id,
            party="OWNER",
            decision="ACCEPT",
            actor_id="owner-1",
            actor_unit_id="UPPPD-GAMBIR",
        )
    )
    parent = db_session.get(CmBatch1ComplaintORM, uuid.UUID(complaint_id))
    assert parent is not None
    assert parent.status != "CLOSED"
    assert second.status in {"CREATED", "ASSIGNED"}


def test_fr004_cancel_mode_a(service: CaseApplicationService, db_session: Session) -> None:
    complaint_id = _seed_complaint(db_session)
    created = service.create_case(
        CreateCaseCommand(
            complaint_id=complaint_id,
            case_type="BILLING",
            subject="Cancel me",
            description="desc",
            priority="LOW",
            actor_id="actor-1",
        )
    )
    cancelled = service.update_status(
        UpdateStatusCommand(
            case_id=created.case_id,
            to_status="CANCELLED",
            cancel_reason="DUPLICATE",
            reason="Duplikat",
            actor_id="supervisor-1",
        )
    )
    assert cancelled.status == "CANCELLED"
    assert cancelled.cancel_reason == "DUPLICATE"
    parent = db_session.get(CmBatch1ComplaintORM, uuid.UUID(complaint_id))
    assert parent is not None
    # DEC-025: sole CANCELLED does not close the parent.
    assert parent.status == "IN_PROGRESS"
    assert parent.status != "CLOSED"


def test_dec025_all_cancelled_parent_stays_open(
    service: CaseApplicationService, db_session: Session
) -> None:
    complaint_id = _seed_complaint(db_session, owning_unit_id="UPPPD-GAMBIR")
    first = service.create_case(
        CreateCaseCommand(
            complaint_id=complaint_id,
            case_type="BILLING",
            subject="One",
            description="d",
            priority="LOW",
            destination_unit_id="UPPPD-GAMBIR",
            actor_id="handler-1",
        )
    )
    second = service.create_case(
        CreateCaseCommand(
            complaint_id=complaint_id,
            case_type="BILLING",
            subject="Two",
            description="d",
            priority="LOW",
            destination_unit_id="UPPPD-GAMBIR",
            actor_id="handler-1",
        )
    )
    for case_id in (first.case_id, second.case_id):
        service.update_status(
            UpdateStatusCommand(
                case_id=case_id,
                to_status="CANCELLED",
                cancel_reason="CUSTOMER_CANCELLATION",
                reason="Pelanggan batal",
                actor_id="supervisor-1",
            )
        )
    parent = db_session.get(CmBatch1ComplaintORM, uuid.UUID(complaint_id))
    assert parent is not None
    assert parent.status == "IN_PROGRESS"


def test_dec025_closed_plus_cancelled_parent_closes(
    service: CaseApplicationService, db_session: Session
) -> None:
    complaint_id = _seed_complaint(db_session, owning_unit_id="UPPPD-GAMBIR")
    keeper = service.create_case(
        CreateCaseCommand(
            complaint_id=complaint_id,
            case_type="BILLING",
            subject="Keep",
            description="d",
            priority="MEDIUM",
            destination_unit_id="UPPPD-GAMBIR",
            actor_id="handler-1",
        )
    )
    extra = service.create_case(
        CreateCaseCommand(
            complaint_id=complaint_id,
            case_type="BILLING",
            subject="Cancel",
            description="d",
            priority="LOW",
            destination_unit_id="UPPPD-GAMBIR",
            actor_id="handler-1",
        )
    )
    service.update_status(
        UpdateStatusCommand(
            case_id=extra.case_id,
            to_status="CANCELLED",
            cancel_reason="DUPLICATE",
            reason="Duplikat",
            actor_id="supervisor-1",
        )
    )
    _resolve_to_resolved(service, keeper.case_id)
    service.record_acceptance(
        RecordAcceptanceCommand(
            case_id=keeper.case_id,
            party="OWNER",
            decision="ACCEPT",
            actor_id="owner-1",
            actor_unit_id="UPPPD-GAMBIR",
        )
    )
    parent = db_session.get(CmBatch1ComplaintORM, uuid.UUID(complaint_id))
    assert parent is not None
    assert parent.status == "CLOSED"


def test_dec025_aggregate_response_exposes_in_progress(
    service: CaseApplicationService, db_session: Session
) -> None:
    from app.integrations.customer import StubCustomerProvider
    from app.modules.cm_batch1.enumeration import EnumerationGuard
    from app.modules.cm_batch1.repository import CmBatch1Repository
    from app.modules.cm_batch1.service import CmBatch1Service

    complaint_id = _seed_complaint(db_session)
    service.create_case(
        CreateCaseCommand(
            complaint_id=complaint_id,
            case_type="BILLING",
            subject="Expose status",
            description="d",
            priority="LOW",
            actor_id="actor-1",
        )
    )
    batch1 = CmBatch1Service(
        customer_provider=StubCustomerProvider(),
        guard=EnumerationGuard(max_failures=3, window_seconds=60, block_seconds=30),
        store=CmBatch1Repository(db_session),
        strict_master=False,
    )
    got = batch1.get_complaint(complaint_id)
    assert got.status == "IN_PROGRESS"
    assert got.case_created is True


@pytest.fixture()
def api_client(db_session: Session) -> Generator[TestClient, None, None]:
    app = create_app()
    svc = CaseApplicationService(
        SqlAlchemyCaseRepository(db_session),
        side_effects=NoOpSideEffects(),
    )
    # Stable actor — F4 acceptance requires Supervisor/Manager on the unit.
    actor_id = uuid.uuid4()

    def _principal() -> Principal:
        return Principal(
            user_id=actor_id,
            roles=("SUPERVISOR",),
            org_unit_id="UNIT-API",
            permissions=frozenset(
                {"complaints:create", "complaints:read", "complaints:update"}
            ),
        )

    app.dependency_overrides[get_case_service] = lambda: svc
    app.dependency_overrides[get_current_principal] = _principal
    app.dependency_overrides[get_db_session] = lambda: db_session
    client = TestClient(app)
    try:
        yield client
    finally:
        app.dependency_overrides.clear()


def test_api_create_get_resolve_close(api_client: TestClient, db_session: Session) -> None:
    complaint_id = _seed_complaint(db_session, owning_unit_id="UNIT-API")
    create = api_client.post(
        "/api/v1/cm/cases",
        json={
            "complaintId": complaint_id,
            "caseType": "BILLING",
            "subject": "API Case",
            "description": "via HTTP",
            "priority": "MEDIUM",
            "destinationUnitId": "UNIT-API",
        },
    )
    assert create.status_code == 201, create.text
    body = create.json()["data"]
    case_id = body["caseId"]
    assert body["status"] == "ASSIGNED"
    assert body["caseNumber"].startswith("CASE-")

    viewed = api_client.get(f"/api/v1/cm/cases/{case_id}")
    assert viewed.status_code == 200
    assert viewed.json()["data"]["caseId"] == case_id

    add = api_client.post(
        f"/api/v1/cm/complaints/{complaint_id}/cases",
        json={
            "caseType": "SERVICE",
            "subject": "Second",
            "description": "add",
            "priority": "LOW",
        },
    )
    assert add.status_code == 201

    status = api_client.patch(
        f"/api/v1/cm/cases/{case_id}/status",
        json={"toStatus": "IN_PROGRESS"},
    )
    assert status.status_code == 200
    assert status.json()["data"]["status"] == "IN_PROGRESS"

    resolve = api_client.post(
        f"/api/v1/cm/cases/{case_id}/resolve",
        json={
            "action": "ACCEPT",
            "comment": "OK",
            "resolutionCode": "FIXED",
            "summary": "Done",
        },
    )
    assert resolve.status_code == 200
    assert resolve.json()["data"]["status"] == "RESOLVED"
    assert resolve.json()["data"]["handlingUnitAcceptance"]["decision"] == "ACCEPT"
    assert resolve.json()["data"]["ownerAcceptance"] is None

    # F4 closure rule — RESOLVED alone (Handling Unit side) is not enough.
    premature_close = api_client.post(f"/api/v1/cm/cases/{case_id}/close", json={})
    assert premature_close.status_code == 409
    assert premature_close.json()["code"] == "OWNER_ACCEPTANCE_REQUIRED"

    owner_accept = api_client.post(
        f"/api/v1/cm/cases/{case_id}/acceptance",
        json={"party": "OWNER", "decision": "ACCEPT"},
    )
    assert owner_accept.status_code == 200
    assert owner_accept.json()["data"]["ownerAcceptance"]["decision"] == "ACCEPT"
    assert owner_accept.json()["data"]["status"] == "CLOSED"

    # Compatibility close cannot bypass dual-acceptance; once closed it is
    # idempotent.
    close = api_client.post(f"/api/v1/cm/cases/{case_id}/close", json={})
    assert close.status_code == 200
    assert close.json()["data"]["status"] == "CLOSED"


def test_api_create_returns_401_without_auth(db_session: Session) -> None:
    """CAP-008 AuthN: unauthenticated POST must not be 404."""
    app = create_app()
    app.dependency_overrides[get_case_service] = lambda: CaseApplicationService(
        SqlAlchemyCaseRepository(db_session),
        side_effects=NoOpSideEffects(),
    )
    client = TestClient(app)
    try:
        resp = client.post(
            "/api/v1/cm/cases",
            json={
                "complaintId": str(uuid.uuid4()),
                "caseType": "BILLING",
                "subject": "No auth",
                "description": "must 401",
                "priority": "LOW",
            },
        )
        assert resp.status_code == 401
        assert resp.json()["code"] == "UNAUTHENTICATED"
    finally:
        app.dependency_overrides.clear()


def test_api_create_returns_403_without_permission(db_session: Session) -> None:
    """CAP-008 AuthZ: principal without complaints:create must be 403."""
    app = create_app()
    app.dependency_overrides[get_case_service] = lambda: CaseApplicationService(
        SqlAlchemyCaseRepository(db_session),
        side_effects=NoOpSideEffects(),
    )
    app.dependency_overrides[get_current_principal] = lambda: Principal(
        user_id=uuid.uuid4(),
        permissions=frozenset({"complaints:read"}),
    )
    client = TestClient(app)
    try:
        resp = client.post(
            "/api/v1/cm/cases",
            json={
                "complaintId": str(uuid.uuid4()),
                "caseType": "BILLING",
                "subject": "No perm",
                "description": "must 403",
                "priority": "LOW",
            },
        )
        assert resp.status_code == 403
        assert resp.json()["code"] == "FORBIDDEN"
    finally:
        app.dependency_overrides.clear()


def test_audit_timeline_side_effects_records_audit_and_timeline() -> None:
    """Production wiring: AuditTimelineSideEffects writes audit + complaint timeline."""
    from unittest.mock import MagicMock

    audit = MagicMock()
    timeline = MagicMock()
    effects = AuditTimelineSideEffects(session=MagicMock(), audit=audit, timeline=timeline)
    case = CaseAggregate.create(
        complaint_id=str(uuid.uuid4()),
        customer_id="CUST-1",
        case_number=CaseNumber.format(2026, 1),
        case_type="BILLING",
        subject="Side effect",
        description="desc",
        priority="MEDIUM",
        created_by="actor-1",
    )
    assert case.status == CaseStatus.CREATED
    effects.record_case_event(
        case=case,
        event_name="CaseCreated",
        title="Case created",
        actor_id=str(uuid.uuid4()),
        after={"status": case.status.value},
    )
    assert audit.log.call_count == 1
    assert timeline.add.call_count == 1
    assert audit.log.call_args.kwargs["entity_type"] == "Case"
    assert audit.log.call_args.kwargs["event_type"] == "CaseCreated"


# --- P0 gap closure: org-scope enforcement on /api/v1/cm/cases ------------


@pytest.fixture()
def jwt_org_api_client(
    db_session: Session,
) -> Generator[dict[str, object], None, None]:
    """Same real SQLite-backed case service as ``api_client``, but jwt-mode
    org-scope settings + a swappable principal, to prove the P0 fix denies
    cross-unit access to a real persisted CmCaseORM row (not a mock)."""
    from app.core.config import Settings, get_settings

    app = create_app()
    svc = CaseApplicationService(
        SqlAlchemyCaseRepository(db_session),
        side_effects=NoOpSideEffects(),
    )
    settings = Settings(
        environment="development",
        ecmp_auth_mode="jwt",
        ecmp_env="shared",
        oidc_issuer="http://localhost:8180/realms/ecmp",
        oidc_audience="ecmp-api",
        oidc_jwks_url="http://jwks.test/certs",
        jwt_secret_key="test-secret-key-for-cm-case-org-scope",
        jwt_algorithm="HS256",
    )
    state: dict[str, Principal] = {
        "principal": Principal(
            user_id=uuid.uuid4(),
            permissions=frozenset(
                {"complaints:create", "complaints:read", "complaints:update"}
            ),
            org_unit_id="OU-A",
        )
    }

    app.dependency_overrides[get_case_service] = lambda: svc
    app.dependency_overrides[get_current_principal] = lambda: state["principal"]
    app.dependency_overrides[get_db_session] = lambda: db_session
    app.dependency_overrides[get_settings] = lambda: settings
    client = TestClient(app)
    try:
        yield {"client": client, "state": state}
    finally:
        app.dependency_overrides.clear()


def _principal_for(org_unit_id: str | None) -> Principal:
    return Principal(
        user_id=uuid.uuid4(),
        permissions=frozenset(
            {"complaints:create", "complaints:read", "complaints:update"}
        ),
        org_unit_id=org_unit_id,
    )


def test_http_cross_unit_case_read_denied(
    jwt_org_api_client: dict[str, object], db_session: Session
) -> None:
    client: TestClient = jwt_org_api_client["client"]  # type: ignore[assignment]
    state: dict[str, Principal] = jwt_org_api_client["state"]  # type: ignore[assignment]
    complaint_id = _seed_complaint(db_session)

    create = client.post(
        "/api/v1/cm/cases",
        json={
            "complaintId": complaint_id,
            "caseType": "BILLING",
            "subject": "Org scope case",
            "description": "via HTTP",
            "priority": "MEDIUM",
            "destinationUnitId": "OU-A",
        },
    )
    assert create.status_code == 201, create.text
    case_id = create.json()["data"]["caseId"]

    # Cross-unit read denied.
    state["principal"] = _principal_for("OU-B")
    denied = client.get(f"/api/v1/cm/cases/{case_id}")
    assert denied.status_code == 403
    assert denied.json()["code"] == "ORG_SCOPE_DENIED"

    # Same-unit read allowed.
    state["principal"] = _principal_for("OU-A")
    allowed = client.get(f"/api/v1/cm/cases/{case_id}")
    assert allowed.status_code == 200
    assert allowed.json()["data"]["caseId"] == case_id


def test_http_cross_unit_case_mutation_denied(
    jwt_org_api_client: dict[str, object], db_session: Session
) -> None:
    """Cross-unit status change / resolve / close must 403 before mutating."""
    client: TestClient = jwt_org_api_client["client"]  # type: ignore[assignment]
    state: dict[str, Principal] = jwt_org_api_client["state"]  # type: ignore[assignment]
    complaint_id = _seed_complaint(db_session)

    create = client.post(
        "/api/v1/cm/cases",
        json={
            "complaintId": complaint_id,
            "caseType": "BILLING",
            "subject": "Org scope case",
            "description": "via HTTP",
            "priority": "MEDIUM",
            "destinationUnitId": "OU-A",
        },
    )
    case_id = create.json()["data"]["caseId"]

    state["principal"] = _principal_for("OU-B")
    status_denied = client.patch(
        f"/api/v1/cm/cases/{case_id}/status",
        json={"toStatus": "IN_PROGRESS"},
    )
    assert status_denied.status_code == 403
    assert status_denied.json()["code"] == "ORG_SCOPE_DENIED"

    # Mutation must not have gone through despite the earlier gap.
    state["principal"] = _principal_for("OU-A")
    unchanged = client.get(f"/api/v1/cm/cases/{case_id}")
    assert unchanged.json()["data"]["status"] == "ASSIGNED"

    state["principal"] = _principal_for("OU-B")
    close_denied = client.post(f"/api/v1/cm/cases/{case_id}/close", json={})
    assert close_denied.status_code == 403
    assert close_denied.json()["code"] == "ORG_SCOPE_DENIED"


def test_api_536_list_visibility_self_unit_admin(db_session: Session) -> None:
    """DEC-024: agent SELF vs supervisor UNIT vs admin ALL."""
    from app.modules.cm_case.application.dto import CreateCaseCommand

    agent_a = uuid.uuid4()
    agent_b = uuid.uuid4()
    repo = SqlAlchemyCaseRepository(db_session)
    svc = CaseApplicationService(repo, side_effects=NoOpSideEffects())
    c1 = _seed_complaint(db_session)
    c2 = _seed_complaint(db_session)

    case_a = svc.create_case(
        CreateCaseCommand(
            complaint_id=c1,
            case_type="BILLING",
            subject="Agent A case",
            description="a",
            priority="MEDIUM",
            destination_unit_id="BR-A",
            actor_id=str(agent_a),
        )
    )
    case_b = svc.create_case(
        CreateCaseCommand(
            complaint_id=c2,
            case_type="BILLING",
            subject="Agent B case",
            description="b",
            priority="MEDIUM",
            destination_unit_id="BR-B",
            actor_id=str(agent_b),
        )
    )

    app = create_app()
    state: dict[str, Principal] = {
        "principal": Principal(
            user_id=agent_a,
            roles=("AGENT",),
            permissions=frozenset({"complaints:read"}),
            org_unit_id="BR-A",
        )
    }
    app.dependency_overrides[get_case_service] = lambda: svc
    app.dependency_overrides[get_current_principal] = lambda: state["principal"]
    app.dependency_overrides[get_db_session] = lambda: db_session
    with TestClient(app) as client:
        self_list = client.get("/api/v1/cm/cases")
        assert self_list.status_code == 200, self_list.text
        ids = {row["caseId"] for row in self_list.json()["data"]}
        assert case_a.case_id in ids
        assert case_b.case_id not in ids

        state["principal"] = Principal(
            user_id=uuid.uuid4(),
            roles=("SUPERVISOR",),
            permissions=frozenset({"complaints:read"}),
            org_unit_id="BR-A",
        )
        unit_list = client.get("/api/v1/cm/cases")
        assert unit_list.status_code == 200, unit_list.text
        unit_ids = {row["caseId"] for row in unit_list.json()["data"]}
        assert case_a.case_id in unit_ids
        assert case_b.case_id not in unit_ids

        state["principal"] = Principal(
            user_id=uuid.uuid4(),
            roles=("SUPERVISOR",),
            permissions=frozenset({"complaints:read"}),
            org_unit_id="BR-B",
        )
        other_branch = client.get("/api/v1/cm/cases")
        other_ids = {row["caseId"] for row in other_branch.json()["data"]}
        assert case_a.case_id not in other_ids
        assert case_b.case_id in other_ids

        state["principal"] = Principal(
            user_id=uuid.uuid4(),
            roles=("ADMIN",),
            permissions=frozenset({"complaints:read", "*"}),
        )
        admin_list = client.get("/api/v1/cm/cases")
        assert admin_list.status_code == 200
        admin_ids = {row["caseId"] for row in admin_list.json()["data"]}
        assert case_a.case_id in admin_ids and case_b.case_id in admin_ids
        assert admin_list.json()["meta"]["totalItems"] >= 2

    app.dependency_overrides.clear()


# ---------------------------------------------------------------------------
# F4 business rules — Complaint Owner vs Handling Unit, closure acceptance.
# ---------------------------------------------------------------------------


def test_f4_owner_set_from_parent_complaint_at_creation(
    service: CaseApplicationService, db_session: Session
) -> None:
    """Owner = unit that created the Complaint, snapshotted onto the Case."""
    complaint_id = _seed_complaint(db_session, owning_unit_id="UPPPD-GAMBIR")
    created = service.create_case(
        CreateCaseCommand(
            complaint_id=complaint_id,
            case_type="BILLING",
            subject="Owner snapshot",
            description="desc",
            priority="MEDIUM",
            actor_id="agent-1",
        )
    )
    assert created.owner_unit_id == "UPPPD-GAMBIR"
    # No initial destination — handling unit is not yet assigned.
    assert created.owning_unit_id is None


def test_f4_owner_survives_reload_from_repository(
    service: CaseApplicationService, db_session: Session
) -> None:
    """Owner must persist across save/get round-trips, not just in memory."""
    complaint_id = _seed_complaint(db_session, owning_unit_id="UPPPD-GAMBIR")
    created = service.create_case(
        CreateCaseCommand(
            complaint_id=complaint_id,
            case_type="BILLING",
            subject="Owner reload",
            description="desc",
            priority="MEDIUM",
            actor_id="agent-1",
        )
    )
    reloaded = service.get_case(created.case_id)
    assert reloaded.owner_unit_id == "UPPPD-GAMBIR"


def test_f4_transfer_does_not_change_owner_but_changes_handling_unit(
    service: CaseApplicationService, db_session: Session
) -> None:
    """Cabang → Pusat handoff: owner stays Cabang, handling unit becomes Pusat."""
    complaint_id = _seed_complaint(db_session, owning_unit_id="UPPPD-GAMBIR")
    created = service.create_case(
        CreateCaseCommand(
            complaint_id=complaint_id,
            case_type="BILLING",
            subject="Transfer",
            description="desc",
            priority="MEDIUM",
            destination_unit_id="UPPPD-GAMBIR",  # starts handled at the branch
            actor_id="agent-1",
        )
    )
    assert created.owner_unit_id == "UPPPD-GAMBIR"
    assert created.owning_unit_id == "UPPPD-GAMBIR"

    transferred = service.update_status(
        UpdateStatusCommand(
            case_id=created.case_id,
            to_status="ASSIGNED",
            actor_id="agent-1",
            destination_unit_id="PUSAT",
        )
    )
    # Handling unit moved to Pusat...
    assert transferred.owning_unit_id == "PUSAT"
    # ...but owner is still the branch that created the Complaint.
    assert transferred.owner_unit_id == "UPPPD-GAMBIR"

    returned = service.update_status(
        UpdateStatusCommand(
            case_id=created.case_id,
            to_status="ASSIGNED",
            actor_id="hq-1",
            destination_unit_id="UPPPD-GAMBIR",
        )
    )
    # Sent back to the branch — handling unit changes again, owner still fixed.
    assert returned.owning_unit_id == "UPPPD-GAMBIR"
    assert returned.owner_unit_id == "UPPPD-GAMBIR"


def test_f4_owner_immutable_when_complaint_created_by_pusat(
    service: CaseApplicationService, db_session: Session
) -> None:
    """Pusat-initiated Complaint: owner = Pusat, even after handing to a branch."""
    complaint_id = _seed_complaint(db_session, owning_unit_id="PUSAT")
    created = service.create_case(
        CreateCaseCommand(
            complaint_id=complaint_id,
            case_type="BILLING",
            subject="Pusat-created",
            description="desc",
            priority="MEDIUM",
            destination_unit_id="PUSAT",
            actor_id="hq-1",
        )
    )
    assert created.owner_unit_id == "PUSAT"

    handed_to_branch = service.update_status(
        UpdateStatusCommand(
            case_id=created.case_id,
            to_status="ASSIGNED",
            actor_id="hq-1",
            destination_unit_id="UPPPD-GAMBIR",
        )
    )
    assert handed_to_branch.owning_unit_id == "UPPPD-GAMBIR"
    assert handed_to_branch.owner_unit_id == "PUSAT"  # unchanged


def test_f4_transfer_history_captures_who_unit_and_when(
    db_session: Session,
) -> None:
    """Every handling-unit transfer must produce a history/event entry
    answering: what happened, who, which unit, when, which Complaint."""
    events: list[dict] = []

    class RecordingSideEffects:
        def record_case_event(self, **kwargs):
            events.append(kwargs)

    service = CaseApplicationService(
        SqlAlchemyCaseRepository(db_session),
        side_effects=RecordingSideEffects(),
    )
    complaint_id = _seed_complaint(db_session, owning_unit_id="UPPPD-GAMBIR")
    created = service.create_case(
        CreateCaseCommand(
            complaint_id=complaint_id,
            case_type="BILLING",
            subject="History",
            description="desc",
            priority="MEDIUM",
            destination_unit_id="UPPPD-GAMBIR",
            actor_id="agent-1",
            actor_unit_id="UPPPD-GAMBIR",
        )
    )
    events.clear()  # only care about the transfer event below

    service.update_status(
        UpdateStatusCommand(
            case_id=created.case_id,
            to_status="ASSIGNED",
            actor_id="agent-1",
            actor_unit_id="UPPPD-GAMBIR",
            destination_unit_id="PUSAT",
            reason="Eskalasi ke Pusat — butuh kewenangan lebih tinggi.",
        )
    )
    assert len(events) == 1
    evt = events[0]
    assert evt["event_name"] == "CaseAssigned"  # apa tindakan yang terjadi
    assert evt["actor_id"] == "agent-1"  # siapa yang melakukan
    assert evt["actor_unit_id"] == "UPPPD-GAMBIR"  # unit yang melakukan
    assert evt["case"].complaint_id == complaint_id  # complaint yang terdampak
    assert evt["note"] == "Eskalasi ke Pusat — butuh kewenangan lebih tinggi."
    # perpindahan handling unit tercermin di before/after snapshot
    assert evt["before"]["owningUnitId"] == "UPPPD-GAMBIR"
    assert evt["after"]["owningUnitId"] == "PUSAT"
    assert evt["after"]["ownerUnitId"] == "UPPPD-GAMBIR"


def test_dec021_accept_comment_only_uses_branch_done_sentinel(
    service: CaseApplicationService, db_session: Session
) -> None:
    """DEC-021: ACCEPT without resolutionCode/summary persists BRANCH_DONE."""
    complaint_id = _seed_complaint(db_session, owning_unit_id="UPPPD-GAMBIR")
    created = service.create_case(
        CreateCaseCommand(
            complaint_id=complaint_id,
            case_type="BILLING",
            subject="Comment-only close",
            description="desc",
            priority="MEDIUM",
            destination_unit_id="UPPPD-GAMBIR",
            actor_id="handler-1",
        )
    )
    service.update_status(
        UpdateStatusCommand(
            case_id=created.case_id,
            to_status="IN_PROGRESS",
            actor_id="handler-1",
        )
    )
    resolved = service.resolve(
        ResolveCaseCommand(
            case_id=created.case_id,
            action="ACCEPT",
            comment="Selesai di cabang tanpa kode resolusi",
            actor_id="supervisor-1",
            actor_unit_id="UPPPD-GAMBIR",
        )
    )
    assert resolved.status == "RESOLVED"
    assert resolved.resolution is not None
    assert resolved.resolution.resolution_code == "BRANCH_DONE"
    assert resolved.resolution.summary == "Selesai di cabang tanpa kode resolusi"


def _resolve_to_resolved(service: CaseApplicationService, case_id: str) -> None:
    """Drive to RESOLVED, tolerating a Case already sitting at IN_PROGRESS
    (e.g. after a prior owner REJECT put it back there)."""
    current = service.get_case(case_id)
    handler = current.handling_claimed_by or "handler-1"
    if current.status != "IN_PROGRESS":
        service.update_status(
            UpdateStatusCommand(
                case_id=case_id, to_status="IN_PROGRESS", actor_id=handler
            )
        )
    service.resolve(
        ResolveCaseCommand(
            case_id=case_id,
            action="ACCEPT",
            comment="Selesai ditangani",
            resolution_code="FIXED",
            summary="Perbaikan diterapkan",
            actor_id="handler-1",
            actor_unit_id="PUSAT",
        )
    )


def test_f4_resolved_does_not_auto_close(
    service: CaseApplicationService, db_session: Session
) -> None:
    complaint_id = _seed_complaint(db_session, owning_unit_id="UPPPD-GAMBIR")
    created = service.create_case(
        CreateCaseCommand(
            complaint_id=complaint_id,
            case_type="BILLING",
            subject="No auto close",
            description="desc",
            priority="MEDIUM",
            destination_unit_id="PUSAT",
            actor_id="hq-1",
        )
    )
    _resolve_to_resolved(service, created.case_id)
    resolved = service.get_case(created.case_id)
    assert resolved.status == "RESOLVED"
    with pytest.raises(ApiError) as exc:
        service.close(CloseCaseCommand(case_id=created.case_id, actor_id="hq-1"))
    assert exc.value.code == "OWNER_ACCEPTANCE_REQUIRED"


def test_f4_handling_unit_acceptance_alone_not_enough_for_close(
    service: CaseApplicationService, db_session: Session
) -> None:
    complaint_id = _seed_complaint(db_session, owning_unit_id="UPPPD-GAMBIR")
    created = service.create_case(
        CreateCaseCommand(
            complaint_id=complaint_id,
            case_type="BILLING",
            subject="Handler only",
            description="desc",
            priority="MEDIUM",
            destination_unit_id="PUSAT",
            actor_id="hq-1",
        )
    )
    _resolve_to_resolved(service, created.case_id)  # stamps Handling Unit ACCEPT
    with pytest.raises(ApiError) as exc:
        service.close(CloseCaseCommand(case_id=created.case_id, actor_id="hq-1"))
    assert exc.value.code == "OWNER_ACCEPTANCE_REQUIRED"


def test_f4_owner_acceptance_alone_not_enough_for_close(
    service: CaseApplicationService, db_session: Session
) -> None:
    """Owner cannot close unilaterally — Handling Unit must also have accepted."""
    complaint_id = _seed_complaint(db_session, owning_unit_id="UPPPD-GAMBIR")
    created = service.create_case(
        CreateCaseCommand(
            complaint_id=complaint_id,
            case_type="BILLING",
            subject="Owner only",
            description="desc",
            priority="MEDIUM",
            destination_unit_id="PUSAT",
            actor_id="hq-1",
        )
    )
    # Reach IN_PROGRESS but do NOT resolve — status is not RESOLVED yet, so
    # even attempting acceptance is rejected: Owner cannot act before the
    # Handling Unit has declared the work done.
    service.update_status(
        UpdateStatusCommand(case_id=created.case_id, to_status="IN_PROGRESS", actor_id="hq-1")
    )
    with pytest.raises(ApiError) as exc:
        service.record_acceptance(
            RecordAcceptanceCommand(
                case_id=created.case_id,
                party="OWNER",
                decision="ACCEPT",
                actor_id="owner-1",
            )
        )
    assert exc.value.code == "INVALID_STATE"

    # Now let the Handling Unit resolve — Owner acceptance alone is still
    # not enough without the Handling Unit's (already-stamped) acceptance
    # being ACCEPT too — simulate by rejecting Handling Unit's own proposal
    # is not possible post-ACCEPT, so instead verify close requires BOTH by
    # checking handling_unit_acceptance is present once RESOLVED is reached.
    _resolve_to_resolved(service, created.case_id)
    resolved = service.get_case(created.case_id)
    assert resolved.handling_unit_acceptance is not None
    owner_only = service.record_acceptance(
        RecordAcceptanceCommand(
            case_id=created.case_id,
            party="OWNER",
            decision="ACCEPT",
            actor_id="owner-1",
        )
    )
    # Both acceptances present → second ACCEPT triggers CLOSED.
    assert owner_only.handling_unit_acceptance is not None
    assert owner_only.owner_acceptance is not None
    assert owner_only.status == "CLOSED"


def test_f4_both_acceptances_result_in_closed(
    service: CaseApplicationService, db_session: Session
) -> None:
    complaint_id = _seed_complaint(db_session, owning_unit_id="UPPPD-GAMBIR")
    created = service.create_case(
        CreateCaseCommand(
            complaint_id=complaint_id,
            case_type="BILLING",
            subject="Both accept",
            description="desc",
            priority="MEDIUM",
            destination_unit_id="PUSAT",
            actor_id="hq-1",
        )
    )
    _resolve_to_resolved(service, created.case_id)
    closed = service.record_acceptance(
        RecordAcceptanceCommand(
            case_id=created.case_id, party="OWNER", decision="ACCEPT", actor_id="owner-1"
        )
    )
    assert closed.status == "CLOSED"
    assert closed.closed_by == "owner-1"


def test_f4_owner_rejection_prevents_close_and_returns_to_review(
    service: CaseApplicationService, db_session: Session
) -> None:
    complaint_id = _seed_complaint(db_session, owning_unit_id="UPPPD-GAMBIR")
    created = service.create_case(
        CreateCaseCommand(
            complaint_id=complaint_id,
            case_type="BILLING",
            subject="Owner rejects",
            description="desc",
            priority="MEDIUM",
            destination_unit_id="PUSAT",
            actor_id="hq-1",
        )
    )
    _resolve_to_resolved(service, created.case_id)

    with pytest.raises(ApiError) as exc:
        service.record_acceptance(
            RecordAcceptanceCommand(
                case_id=created.case_id,
                party="OWNER",
                decision="REJECT",
                actor_id="owner-1",
                # no note — must fail validation
            )
        )
    assert exc.value.code == "VALIDATION_ERROR"

    rejected = service.record_acceptance(
        RecordAcceptanceCommand(
            case_id=created.case_id,
            party="OWNER",
            decision="REJECT",
            actor_id="owner-1",
            actor_unit_id="UPPPD-GAMBIR",
            note="Hasil belum sesuai — mohon perbaiki kembali.",
        )
    )
    # Existing state machine represents "back to handling" as IN_PROGRESS —
    # no new CaseStatus was introduced.
    assert rejected.status == "IN_PROGRESS"
    assert rejected.handling_unit_acceptance is None
    assert rejected.owner_acceptance is None

    with pytest.raises(ApiError) as exc:
        service.close(CloseCaseCommand(case_id=created.case_id, actor_id="hq-1"))
    # Close requires RESOLVED first (existing state machine) — after a
    # rejection the Case is back at IN_PROGRESS, so this fails even before
    # reaching the acceptance checks. Either way, CLOSED is unreachable.
    assert exc.value.code == "INVALID_STATE"
    reloaded = service.get_case(created.case_id)
    assert reloaded.status != "CLOSED"


def test_f4_owner_rejection_produces_history(db_session: Session) -> None:
    events: list[dict] = []

    class RecordingSideEffects:
        def record_case_event(self, **kwargs):
            events.append(kwargs)

    service = CaseApplicationService(
        SqlAlchemyCaseRepository(db_session),
        side_effects=RecordingSideEffects(),
    )
    complaint_id = _seed_complaint(db_session, owning_unit_id="UPPPD-GAMBIR")
    created = service.create_case(
        CreateCaseCommand(
            complaint_id=complaint_id,
            case_type="BILLING",
            subject="Owner rejects — history",
            description="desc",
            priority="MEDIUM",
            destination_unit_id="PUSAT",
            actor_id="hq-1",
        )
    )
    _resolve_to_resolved(service, created.case_id)
    events.clear()

    service.record_acceptance(
        RecordAcceptanceCommand(
            case_id=created.case_id,
            party="OWNER",
            decision="REJECT",
            actor_id="owner-1",
            actor_unit_id="UPPPD-GAMBIR",
            note="Belum sesuai kebutuhan pelapor.",
        )
    )
    assert len(events) == 1
    evt = events[0]
    assert evt["event_name"] == "CaseOwnerRejected"
    assert evt["actor_id"] == "owner-1"
    assert evt["actor_unit_id"] == "UPPPD-GAMBIR"
    assert evt["note"] == "Belum sesuai kebutuhan pelapor."
    assert evt["case"].complaint_id == complaint_id


def test_f4_both_acceptances_produce_history(db_session: Session) -> None:
    events: list[dict] = []

    class RecordingSideEffects:
        def record_case_event(self, **kwargs):
            events.append(kwargs)

    service = CaseApplicationService(
        SqlAlchemyCaseRepository(db_session),
        side_effects=RecordingSideEffects(),
    )
    complaint_id = _seed_complaint(db_session, owning_unit_id="UPPPD-GAMBIR")
    created = service.create_case(
        CreateCaseCommand(
            complaint_id=complaint_id,
            case_type="BILLING",
            subject="Both accept — history",
            description="desc",
            priority="MEDIUM",
            destination_unit_id="PUSAT",
            actor_id="hq-1",
        )
    )
    _resolve_to_resolved(service, created.case_id)
    events.clear()

    service.record_acceptance(
        RecordAcceptanceCommand(
            case_id=created.case_id,
            party="OWNER",
            decision="ACCEPT",
            actor_id="owner-1",
            actor_unit_id="UPPPD-GAMBIR",
        )
    )

    event_names = [e["event_name"] for e in events]
    assert "CaseOwnerAccepted" in event_names
    assert "CaseClosed" in event_names


def test_f4_history_immutable_after_rejection_cycle(
    service: CaseApplicationService, db_session: Session
) -> None:
    """Old acceptance history must remain readable after a reject → re-resolve
    → accept cycle — nothing is deleted or overwritten (only current-state
    pointers move forward)."""
    complaint_id = _seed_complaint(db_session, owning_unit_id="UPPPD-GAMBIR")
    created = service.create_case(
        CreateCaseCommand(
            complaint_id=complaint_id,
            case_type="BILLING",
            subject="Immutable history",
            description="desc",
            priority="MEDIUM",
            destination_unit_id="PUSAT",
            actor_id="hq-1",
        )
    )
    _resolve_to_resolved(service, created.case_id)
    service.record_acceptance(
        RecordAcceptanceCommand(
            case_id=created.case_id,
            party="OWNER",
            decision="REJECT",
            actor_id="owner-1",
            note="Belum sesuai — perbaiki dahulu.",
        )
    )
    # Re-resolve and get both acceptances this time.
    _resolve_to_resolved(service, created.case_id)
    service.record_acceptance(
        RecordAcceptanceCommand(
            case_id=created.case_id, party="OWNER", decision="ACCEPT", actor_id="owner-1"
        )
    )
    reloaded = service.get_case(created.case_id)
    assert reloaded.status == "CLOSED"

    # The full history — including the first cycle's REJECT — is still there.
    decisions = [(a.party, a.decision) for a in reloaded.acceptance_history]
    assert ("OWNER", "REJECT") in decisions
    assert ("OWNER", "ACCEPT") in decisions
    assert decisions.count(("HANDLING_UNIT", "ACCEPT")) == 2  # once per resolve cycle
    # Current state reflects only the final, satisfied cycle.
    assert reloaded.owner_acceptance is not None
    assert reloaded.owner_acceptance.decision == "ACCEPT"
