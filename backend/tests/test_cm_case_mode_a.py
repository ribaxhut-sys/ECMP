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
    CmCaseNumberCounterORM,
    CmCaseORM,
    CmCaseResolutionORM,
)
from app.modules.cm_case.infrastructure.repository import SqlAlchemyCaseRepository

_TABLES = [
    CmBatch1ComplaintORM.__table__,
    CmCaseORM.__table__,
    CmCaseResolutionORM.__table__,
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


def _seed_complaint(session: Session, *, status: str = "REGISTERED") -> str:
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
    parent = db_session.get(CmBatch1ComplaintORM, uuid.UUID(complaint_id))
    assert parent is not None
    assert parent.status == "IN_PROGRESS"
    assert parent.case_created is True


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
            actor_id="handler-1",
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

    closed = service.close(
        CloseCaseCommand(case_id=created.case_id, actor_id="supervisor-1")
    )
    assert closed.status == "CLOSED"
    assert closed.closed_by == "supervisor-1"
    parent = db_session.get(CmBatch1ComplaintORM, uuid.UUID(complaint_id))
    assert parent is not None
    assert parent.status != "CLOSED"  # BQ-007


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


@pytest.fixture()
def api_client(db_session: Session) -> Generator[TestClient, None, None]:
    app = create_app()
    svc = CaseApplicationService(
        SqlAlchemyCaseRepository(db_session),
        side_effects=NoOpSideEffects(),
    )

    def _principal() -> Principal:
        return Principal(
            user_id=uuid.uuid4(),
            permissions=frozenset(
                {"complaints:create", "complaints:read", "complaints:update", "*"}
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
    complaint_id = _seed_complaint(db_session)
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
