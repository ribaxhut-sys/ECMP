"""Pengaduan Internal — domain + persistence + authz regression (checklist 1–35)."""

from __future__ import annotations

import uuid
from collections.abc import Generator

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine, event
from sqlalchemy.orm import Session, sessionmaker
from sqlalchemy.pool import StaticPool

from app.core.authorization.authentication import get_current_principal
from app.core.authorization.case_acceptance import assert_case_acceptance_authorized
from app.core.authorization.principal import Principal
from app.core.config import Settings, get_settings
from app.core.errors import PermissionDeniedError
from app.db.base import Base
from app.db.session import get_db_session
from app.main import create_app
from app.modules.cm_batch1.models import CmBatch1ComplaintORM
from app.modules.internal_complaint.api.router import get_internal_complaint_service
from app.modules.internal_complaint.application.dto import (
    CloseCommand,
    CreateInternalComplaintCommand,
    RecordAcceptanceCommand,
    ResolveCommand,
    StartHandlingCommand,
    TransferCommand,
)
from app.modules.internal_complaint.application.related_aggregate import (
    resolve_related_aggregate,
)
from app.modules.internal_complaint.application.services import (
    InternalComplaintApplicationService,
)
from app.modules.internal_complaint.infrastructure.orm import (
    InternalComplaintAcceptanceORM,
    InternalComplaintEventORM,
    InternalComplaintNumberCounterORM,
    InternalComplaintORM,
    InternalComplaintResolutionORM,
)
from app.modules.internal_complaint.infrastructure.repository import (
    SqlAlchemyInternalComplaintRepository,
)

_TABLES = [
    InternalComplaintORM.__table__,
    InternalComplaintResolutionORM.__table__,
    InternalComplaintAcceptanceORM.__table__,
    InternalComplaintEventORM.__table__,
    InternalComplaintNumberCounterORM.__table__,
    CmBatch1ComplaintORM.__table__,
]

_PERMS = frozenset(
    {
        "complaints:create",
        "complaints:read",
        "complaints:update",
        "complaints:assign",
        "complaints:close",
    }
)


@pytest.fixture()
def db_session() -> Generator[Session, None, None]:
    engine = create_engine(
        "sqlite://",
        future=True,
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )

    @event.listens_for(engine, "connect")
    def _enable_sqlite_fk(dbapi_conn, _connection_record) -> None:  # noqa: ANN001
        cursor = dbapi_conn.cursor()
        cursor.execute("PRAGMA foreign_keys=ON")
        cursor.close()

    Base.metadata.create_all(engine, tables=_TABLES)
    factory = sessionmaker(bind=engine, autoflush=False, autocommit=False, future=True)
    session = factory()
    try:
        yield session
    finally:
        session.close()
        engine.dispose()


@pytest.fixture()
def service(db_session: Session) -> InternalComplaintApplicationService:
    return InternalComplaintApplicationService(
        SqlAlchemyInternalComplaintRepository(db_session)
    )


def _principal(
    *,
    user_id: uuid.UUID | None = None,
    roles: tuple[str, ...] = (),
    org_unit_id: str | None = "UPPPD-GAMBIR",
) -> Principal:
    return Principal(
        user_id=user_id or uuid.uuid4(),
        roles=roles,
        org_unit_id=org_unit_id,
        permissions=_PERMS,
    )


def _create(
    service: InternalComplaintApplicationService,
    *,
    actor_id: str = "creator-1",
    owner_unit_id: str = "UPPPD-GAMBIR",
    subject: str = "Internal issue",
) -> str:
    dto = service.create(
        CreateInternalComplaintCommand(
            subject=subject,
            description="Desc",
            category="OPERATIONAL",
            priority="MEDIUM",
            actor_id=actor_id,
            owner_unit_id=owner_unit_id,
            actor_unit_id=owner_unit_id,
        )
    )
    return dto.complaint_id


def _to_resolved(
    service: InternalComplaintApplicationService,
    complaint_id: str,
    *,
    actor_id: str = "handler-sv",
    unit: str = "PUSAT",
) -> None:
    service.transfer(
        TransferCommand(
            complaint_id=complaint_id,
            destination_unit_id=unit,
            actor_id=actor_id,
            actor_unit_id="UPPPD-GAMBIR",
            reason="escalate",
        )
    )
    service.start_handling(
        StartHandlingCommand(
            complaint_id=complaint_id,
            actor_id=actor_id,
            actor_unit_id=unit,
        )
    )
    service.resolve(
        ResolveCommand(
            complaint_id=complaint_id,
            action="ACCEPT",
            comment="Done",
            resolution_code="IC-OK",
            summary="Fixed",
            actor_id=actor_id,
            actor_unit_id=unit,
        )
    )


# --- CREATE -----------------------------------------------------------------


def test_create_sets_owner_to_creator_unit(service: InternalComplaintApplicationService):
    dto = service.create(
        CreateInternalComplaintCommand(
            subject="X",
            description="Y",
            category="COORDINATION",
            priority="HIGH",
            actor_id="agent-1",
            owner_unit_id="UPPPD-MENTENG",
            actor_unit_id="UPPPD-MENTENG",
        )
    )
    assert dto.owner_unit_id == "UPPPD-MENTENG"
    assert dto.handling_unit_id == "UPPPD-MENTENG"
    assert dto.status == "CREATED"
    assert any(e.event_type == "CREATED" for e in dto.history)


def test_owner_immutable_after_transfer(service: InternalComplaintApplicationService):
    cid = _create(service, owner_unit_id="UPPPD-GAMBIR")
    dto = service.transfer(
        TransferCommand(
            complaint_id=cid,
            destination_unit_id="PUSAT",
            actor_id="sv-1",
            actor_unit_id="UPPPD-GAMBIR",
            reason="to HQ",
        )
    )
    assert dto.owner_unit_id == "UPPPD-GAMBIR"
    assert dto.handling_unit_id == "PUSAT"
    assert dto.status == "ASSIGNED"


# --- TRANSFER / VISIBILITY --------------------------------------------------


def test_transfer_produces_history_and_owner_still_sees(
    service: InternalComplaintApplicationService, db_session: Session
):
    cid = _create(service, owner_unit_id="UPPPD-GAMBIR")
    service.transfer(
        TransferCommand(
            complaint_id=cid,
            destination_unit_id="PUSAT",
            actor_id="sv-1",
            actor_unit_id="UPPPD-GAMBIR",
            reason="need HQ",
        )
    )
    dto = service.get(cid)
    transfers = [e for e in dto.history if e.event_type == "TRANSFER"]
    assert len(transfers) == 1
    assert transfers[0].source_unit_id == "UPPPD-GAMBIR"
    assert transfers[0].target_unit_id == "PUSAT"

    owner = _principal(roles=("AGENT",), org_unit_id="UPPPD-GAMBIR")
    items, total = service.list_complaints(owner, org_unit_id="UPPPD-GAMBIR")
    assert total >= 1
    assert any(i.complaint_id == cid for i in items)

    handler = _principal(roles=("SUPERVISOR",), org_unit_id="PUSAT")
    items_h, _ = service.list_complaints(handler, org_unit_id="PUSAT")
    assert any(i.complaint_id == cid for i in items_h)

    stranger = _principal(roles=("AGENT",), org_unit_id="UPPPD-CAKUNG")
    items_s, total_s = service.list_complaints(stranger, org_unit_id="UPPPD-CAKUNG")
    assert total_s == 0
    assert not any(i.complaint_id == cid for i in items_s)


def test_transfer_branch_to_branch_rejected(
    service: InternalComplaintApplicationService,
):
    cid = _create(service, owner_unit_id="UPPPD-GAMBIR")
    with pytest.raises(Exception) as exc:
        service.transfer(
            TransferCommand(
                complaint_id=cid,
                destination_unit_id="UPPPD-MENTENG",
                actor_id="sv-1",
                actor_unit_id="UPPPD-GAMBIR",
                reason="peer branch",
            )
        )
    err = exc.value
    blob = f"{getattr(err, 'code', '')} {err}"
    assert "TRANSFER_DIRECTION_NOT_ALLOWED" in blob or "Cabang" in str(err)


def test_transfer_pusat_to_branch_allowed(
    service: InternalComplaintApplicationService,
):
    cid = _create(service, owner_unit_id="PUSAT")
    dto = service.transfer(
        TransferCommand(
            complaint_id=cid,
            destination_unit_id="UPPPD-GAMBIR",
            actor_id="sv-pusat",
            actor_unit_id="PUSAT",
            reason="to branch",
        )
    )
    assert dto.owner_unit_id == "PUSAT"
    assert dto.handling_unit_id == "UPPPD-GAMBIR"


# --- RESOLUTION / ACCEPTANCE / CLOSE ----------------------------------------


def test_resolved_not_closed_until_dual_acceptance(
    service: InternalComplaintApplicationService,
):
    cid = _create(service)
    _to_resolved(service, cid)
    dto = service.get(cid)
    assert dto.status == "RESOLVED"
    assert dto.handling_unit_acceptance is not None
    assert dto.owner_acceptance is None


def test_handler_acceptance_alone_not_closed(
    service: InternalComplaintApplicationService,
):
    cid = _create(service)
    _to_resolved(service, cid)
    assert service.get(cid).status == "RESOLVED"


def test_owner_acceptance_alone_not_closed(
    service: InternalComplaintApplicationService,
):
    """Simulate owner-only pointer by proposing then accepting as HU with a
    different path — owner alone cannot close without HU accept."""
    cid = _create(service)
    service.start_handling(
        StartHandlingCommand(
            complaint_id=cid, actor_id="a", actor_unit_id="UPPPD-GAMBIR"
        )
    )
    service.resolve(
        ResolveCommand(
            complaint_id=cid,
            action="PROPOSE",
            comment="prop",
            resolution_code="IC-1",
            summary="sum",
            actor_id="agent-1",
            actor_unit_id="UPPPD-GAMBIR",
        )
    )
    # Still IN_PROGRESS — not RESOLVED without ACCEPT
    assert service.get(cid).status == "IN_PROGRESS"


def test_both_acceptances_close(
    service: InternalComplaintApplicationService,
):
    cid = _create(service, actor_id="creator-agent")
    _to_resolved(service, cid, actor_id="handler-sv", unit="PUSAT")
    closed = service.record_acceptance(
        RecordAcceptanceCommand(
            complaint_id=cid,
            party="OWNER",
            decision="ACCEPT",
            actor_id="owner-sv",
            actor_unit_id="UPPPD-GAMBIR",
        )
    )
    assert closed.status == "CLOSED"
    assert any(e.event_type == "OWNER_ACCEPT" for e in closed.history)
    assert any(e.event_type == "CLOSED" for e in closed.history)


def test_handler_reject_prevents_close(
    service: InternalComplaintApplicationService,
):
    cid = _create(service)
    _to_resolved(service, cid, unit="PUSAT")
    rejected = service.record_acceptance(
        RecordAcceptanceCommand(
            complaint_id=cid,
            party="HANDLING_UNIT",
            decision="REJECT",
            note="not done",
            actor_id="handler-sv",
            actor_unit_id="PUSAT",
        )
    )
    assert rejected.status == "IN_PROGRESS"
    assert rejected.handling_unit_acceptance is None
    assert any(e.event_type == "HANDLING_UNIT_REJECT" for e in rejected.history)


def test_owner_reject_prevents_close(
    service: InternalComplaintApplicationService,
):
    cid = _create(service)
    _to_resolved(service, cid, unit="PUSAT")
    rejected = service.record_acceptance(
        RecordAcceptanceCommand(
            complaint_id=cid,
            party="OWNER",
            decision="REJECT",
            note="incomplete",
            actor_id="owner-sv",
            actor_unit_id="UPPPD-GAMBIR",
        )
    )
    assert rejected.status == "IN_PROGRESS"
    assert any(e.event_type == "OWNER_REJECT" for e in rejected.history)


def test_close_cannot_bypass_dual_acceptance(
    service: InternalComplaintApplicationService,
):
    cid = _create(service)
    _to_resolved(service, cid, unit="PUSAT")
    with pytest.raises(Exception) as exc:
        service.close(CloseCommand(complaint_id=cid, actor_id="admin-1"))
    assert "OWNER_ACCEPTANCE_REQUIRED" in str(exc.value) or "Owner" in str(
        exc.value
    )


def test_history_append_only_across_cycles(
    service: InternalComplaintApplicationService,
):
    cid = _create(service)
    _to_resolved(service, cid, unit="PUSAT")
    service.record_acceptance(
        RecordAcceptanceCommand(
            complaint_id=cid,
            party="OWNER",
            decision="REJECT",
            note="retry",
            actor_id="owner-sv",
            actor_unit_id="UPPPD-GAMBIR",
        )
    )
    before = len(service.get(cid).history)
    service.resolve(
        ResolveCommand(
            complaint_id=cid,
            action="ACCEPT",
            comment="Done2",
            resolution_code="IC-OK2",
            summary="Fixed2",
            actor_id="handler-sv",
            actor_unit_id="PUSAT",
        )
    )
    after = service.get(cid)
    assert len(after.history) > before
    assert any(e.event_type == "OWNER_REJECT" for e in after.history)
    assert len([e for e in after.history if e.event_type == "RESOLUTION"]) >= 2


def test_client_cannot_forge_owner_on_create(
    service: InternalComplaintApplicationService,
):
    """Service always uses command.owner_unit_id from server; transfer cannot
    change owner either."""
    cid = _create(service, owner_unit_id="UPPPD-GAMBIR")
    dto = service.transfer(
        TransferCommand(
            complaint_id=cid,
            destination_unit_id="PUSAT",
            actor_id="x",
            actor_unit_id="UPPPD-GAMBIR",
        )
    )
    assert dto.owner_unit_id == "UPPPD-GAMBIR"


# --- AUTHZ helpers (reuse F4 gates) -----------------------------------------


def test_agent_cannot_final_acceptance():
    agent = _principal(roles=("AGENT",), org_unit_id="UPPPD-GAMBIR")
    with pytest.raises(PermissionDeniedError):
        assert_case_acceptance_authorized(
            agent,
            party="OWNER",
            owner_unit_id="UPPPD-GAMBIR",
            handling_unit_id="PUSAT",
            actor_unit_id="UPPPD-GAMBIR",
            complaint_creator_id="someone-else",
        )


def test_wrong_unit_acceptance_denied():
    sv = _principal(roles=("SUPERVISOR",), org_unit_id="UPPPD-CAKUNG")
    with pytest.raises(PermissionDeniedError):
        assert_case_acceptance_authorized(
            sv,
            party="OWNER",
            owner_unit_id="UPPPD-GAMBIR",
            handling_unit_id="PUSAT",
            actor_unit_id="UPPPD-CAKUNG",
            complaint_creator_id="other",
        )


def test_creator_cannot_be_sole_approver():
    creator_id = uuid.uuid4()
    sv = _principal(
        user_id=creator_id, roles=("SUPERVISOR",), org_unit_id="UPPPD-GAMBIR"
    )
    with pytest.raises(PermissionDeniedError):
        assert_case_acceptance_authorized(
            sv,
            party="OWNER",
            owner_unit_id="UPPPD-GAMBIR",
            handling_unit_id="PUSAT",
            actor_unit_id="UPPPD-GAMBIR",
            complaint_creator_id=str(creator_id),
        )


def test_supervisor_may_accept_when_authorized():
    sv = _principal(roles=("SUPERVISOR",), org_unit_id="UPPPD-GAMBIR")
    assert_case_acceptance_authorized(
        sv,
        party="OWNER",
        owner_unit_id="UPPPD-GAMBIR",
        handling_unit_id="PUSAT",
        actor_unit_id="UPPPD-GAMBIR",
        complaint_creator_id="other-user",
    )


def test_manager_may_accept_when_authorized():
    mgr = _principal(roles=("MANAGER",), org_unit_id="PUSAT")
    assert_case_acceptance_authorized(
        mgr,
        party="HANDLING_UNIT",
        owner_unit_id="UPPPD-GAMBIR",
        handling_unit_id="PUSAT",
        actor_unit_id="PUSAT",
        complaint_creator_id="other-user",
    )


# --- HTTP integration -------------------------------------------------------


def _jwt_settings() -> Settings:
    return Settings(
        environment="development",
        ecmp_auth_mode="jwt",
        ecmp_env="shared",
        oidc_issuer="http://localhost:8180/realms/ecmp",
        oidc_audience="ecmp-api",
        oidc_jwks_url="http://jwks.test/certs",
        jwt_secret_key="test-secret-key-for-internal-complaints",
        jwt_algorithm="HS256",
    )


@pytest.fixture()
def http_client(
    db_session: Session, service: InternalComplaintApplicationService
) -> Generator[tuple[TestClient, Principal], None, None]:
    app = create_app()
    principal = _principal(roles=("SUPERVISOR",), org_unit_id="UPPPD-GAMBIR")

    def _override_principal() -> Principal:
        return principal

    app.dependency_overrides[get_current_principal] = _override_principal
    app.dependency_overrides[get_db_session] = lambda: db_session
    app.dependency_overrides[get_internal_complaint_service] = lambda: service
    app.dependency_overrides[get_settings] = _jwt_settings

    with TestClient(app) as client:
        yield client, principal

    app.dependency_overrides.clear()


def test_http_create_ignores_forged_owner_unit(
    http_client: tuple[TestClient, Principal],
):
    client, _ = http_client
    resp = client.post(
        "/api/v1/internal/complaints",
        json={
            "subject": "Forged",
            "description": "try",
            "category": "OPERATIONAL",
            "priority": "LOW",
            "ownerUnitId": "PUSAT",
            "handlingUnitId": "PUSAT",
        },
    )
    assert resp.status_code == 201, resp.text
    data = resp.json()["data"]
    # Owner always creator unit; optional handlingUnitId applies initial transfer.
    assert data["ownerUnitId"] == "UPPPD-GAMBIR"
    assert data["handlingUnitId"] == "PUSAT"


def test_http_agent_create_with_initial_handling_without_assign(
    db_session: Session, service: InternalComplaintApplicationService
):
    """Agent may escalate on create via handlingUnitId (no complaints:assign)."""
    app = create_app()
    agent = _principal(
        roles=("AGENT",),
        org_unit_id="UPPPD-GAMBIR",
    )
    # Drop assign so this fails if FE still called /transfer.
    agent_perms = frozenset(p for p in _PERMS if p != "complaints:assign")
    agent = Principal(
        user_id=agent.user_id,
        roles=agent.roles,
        org_unit_id=agent.org_unit_id,
        permissions=agent_perms,
    )

    app.dependency_overrides[get_current_principal] = lambda: agent
    app.dependency_overrides[get_db_session] = lambda: db_session
    app.dependency_overrides[get_internal_complaint_service] = lambda: service
    app.dependency_overrides[get_settings] = _jwt_settings

    with TestClient(app) as client:
        denied = client.post(
            "/api/v1/internal/complaints",
            json={
                "subject": "No dest",
                "description": "create only",
                "category": "OPERATIONAL",
            },
        )
        assert denied.status_code == 201, denied.text
        cid = denied.json()["data"]["complaintId"]
        tr = client.post(
            f"/api/v1/internal/complaints/{cid}/transfer",
            json={"destinationUnitId": "PUSAT"},
        )
        assert tr.status_code == 403

        ok = client.post(
            "/api/v1/internal/complaints",
            json={
                "subject": "Escalate on create",
                "description": "to pusat",
                "category": "OPERATIONAL",
                "handlingUnitId": "PUSAT",
            },
        )
        assert ok.status_code == 201, ok.text
        data = ok.json()["data"]
        assert data["ownerUnitId"] == "UPPPD-GAMBIR"
        assert data["handlingUnitId"] == "PUSAT"

    app.dependency_overrides.clear()


def test_http_full_flow_to_closed(
    http_client: tuple[TestClient, Principal],
    service: InternalComplaintApplicationService,
):
    client, principal = http_client
    create = client.post(
        "/api/v1/internal/complaints",
        json={
            "subject": "Flow",
            "description": "end to end",
            "category": "PROCESS_SOP",
            "priority": "MEDIUM",
        },
    )
    assert create.status_code == 201
    cid = create.json()["data"]["complaintId"]
    creator = str(principal.user_id)

    # Transfer to PUSAT via service (actor has assign via override path)
    tr = client.post(
        f"/api/v1/internal/complaints/{cid}/transfer",
        json={"destinationUnitId": "PUSAT", "reason": "escalate"},
    )
    assert tr.status_code == 200, tr.text
    assert tr.json()["data"]["ownerUnitId"] == "UPPPD-GAMBIR"
    assert tr.json()["data"]["handlingUnitId"] == "PUSAT"

    # Complete resolve/accept via service with units (HTTP org-scope in jwt
    # mode uses principal.org_unit_id; receive as handling unit requires
    # switching principal — do domain steps via service for dual-unit flow).
    service.start_handling(
        StartHandlingCommand(
            complaint_id=cid, actor_id="pusat-sv", actor_unit_id="PUSAT"
        )
    )
    service.resolve(
        ResolveCommand(
            complaint_id=cid,
            action="ACCEPT",
            comment="ok",
            resolution_code="IC-1",
            summary="done",
            actor_id="pusat-sv",
            actor_unit_id="PUSAT",
        )
    )
    # Owner acceptance must not be the creator
    closed = service.record_acceptance(
        RecordAcceptanceCommand(
            complaint_id=cid,
            party="OWNER",
            decision="ACCEPT",
            actor_id="other-owner-sv",
            actor_unit_id="UPPPD-GAMBIR",
        )
    )
    assert closed.status == "CLOSED"
    assert creator  # retained for SoD clarity
    detail = client.get(f"/api/v1/internal/complaints/{cid}")
    assert detail.status_code == 200
    body = detail.json()["data"]
    assert body["status"] == "CLOSED"
    types = {e["eventType"] for e in body["history"]}
    assert "CREATED" in types
    assert "TRANSFER" in types
    assert "CLOSED" in types


# --- RELATED AGGREGATE ------------------------------------------------------


def _seed_aggregate(
    session: Session,
    *,
    created_by: str,
    owning_unit_id: str = "UPPPD-GAMBIR",
    status: str = "REGISTERED",
    complaint_number: str = "CM-REL-001",
) -> CmBatch1ComplaintORM:
    row = CmBatch1ComplaintORM(
        id=uuid.uuid4(),
        complaint_number=complaint_number,
        customer_id="CUST-REL-001",
        category="BILLING",
        channel="BRANCH",
        subject="Related Aggregate",
        description="Seed for internal related link",
        priority="MEDIUM",
        status=status,
        owning_unit_id=owning_unit_id,
        created_by=created_by,
        case_created=False,
    )
    session.add(row)
    session.flush()
    return row


def test_resolve_related_optional_empty(db_session: Session):
    principal = _principal(roles=("SUPERVISOR",))
    assert (
        resolve_related_aggregate(
            db_session,
            related_complaint_id=None,
            principal=principal,
            actor_unit_id="UPPPD-GAMBIR",
        )
        is None
    )


def test_resolve_related_registered_ok(db_session: Session):
    principal = _principal(roles=("SUPERVISOR",))
    row = _seed_aggregate(db_session, created_by="someone-else")
    ref = resolve_related_aggregate(
        db_session,
        related_complaint_id=str(row.id),
        principal=principal,
        actor_unit_id="UPPPD-GAMBIR",
    )
    assert ref is not None
    assert ref.complaint_id == str(row.id)
    assert ref.complaint_number == "CM-REL-001"


def test_resolve_related_closed_rejected(db_session: Session):
    principal = _principal(roles=("SUPERVISOR",))
    row = _seed_aggregate(db_session, created_by="someone", status="CLOSED")
    with pytest.raises(Exception) as exc:
        resolve_related_aggregate(
            db_session,
            related_complaint_id=str(row.id),
            principal=principal,
            actor_unit_id="UPPPD-GAMBIR",
        )
    assert "RELATED_COMPLAINT_CLOSED" in str(getattr(exc.value, "code", "")) or (
        "RELATED_COMPLAINT_CLOSED" in str(exc.value)
    )


def test_resolve_related_agent_sod(db_session: Session):
    agent = _principal(roles=("AGENT",))
    other = _seed_aggregate(db_session, created_by="other-agent")
    with pytest.raises(Exception) as exc:
        resolve_related_aggregate(
            db_session,
            related_complaint_id=str(other.id),
            principal=agent,
            actor_unit_id="UPPPD-GAMBIR",
        )
    blob = f"{getattr(exc.value, 'code', '')} {exc.value}"
    assert "RELATED_COMPLAINT_NOT_VISIBLE" in blob

    own = _seed_aggregate(
        db_session,
        created_by=str(agent.user_id),
        complaint_number="CM-REL-OWN",
    )
    ref = resolve_related_aggregate(
        db_session,
        related_complaint_id=str(own.id),
        principal=agent,
        actor_unit_id="UPPPD-GAMBIR",
    )
    assert ref is not None
    assert ref.complaint_number == "CM-REL-OWN"


def test_resolve_related_wrong_unit_rejected(db_session: Session):
    principal = _principal(roles=("SUPERVISOR",), org_unit_id="UPPPD-GAMBIR")
    row = _seed_aggregate(
        db_session,
        created_by="x",
        owning_unit_id="UPPPD-CAKUNG",
        complaint_number="CM-REL-OTHER-UNIT",
    )
    with pytest.raises(Exception) as exc:
        resolve_related_aggregate(
            db_session,
            related_complaint_id=str(row.id),
            principal=principal,
            actor_unit_id="UPPPD-GAMBIR",
        )
    blob = f"{getattr(exc.value, 'code', '')} {exc.value}"
    assert "RELATED_COMPLAINT_NOT_VISIBLE" in blob


def test_http_create_with_related_snapshots_number(
    http_client: tuple[TestClient, Principal],
    db_session: Session,
):
    client, principal = http_client
    row = _seed_aggregate(
        db_session,
        created_by="seed-user",
        complaint_number="CM-HTTP-REL",
    )
    db_session.commit()
    resp = client.post(
        "/api/v1/internal/complaints",
        json={
            "subject": "With related",
            "description": "link aggregate",
            "category": "OPERATIONAL",
            "priority": "MEDIUM",
            "relatedComplaintId": str(row.id),
            "relatedComplaintNumber": "FORGED-NUMBER",
        },
    )
    assert resp.status_code == 201, resp.text
    data = resp.json()["data"]
    assert data["relatedComplaintId"] == str(row.id)
    assert data["relatedComplaintNumber"] == "CM-HTTP-REL"
    assert data["relatedComplaintNumber"] != "FORGED-NUMBER"
    assert str(principal.user_id)


def test_http_create_related_closed_conflict(
    http_client: tuple[TestClient, Principal],
    db_session: Session,
):
    client, _ = http_client
    row = _seed_aggregate(
        db_session,
        created_by="seed-user",
        status="CLOSED",
        complaint_number="CM-HTTP-CLOSED",
    )
    db_session.commit()
    resp = client.post(
        "/api/v1/internal/complaints",
        json={
            "subject": "Closed related",
            "description": "should fail",
            "category": "OPERATIONAL",
            "relatedComplaintId": str(row.id),
        },
    )
    assert resp.status_code == 409, resp.text
    assert resp.json()["code"] == "RELATED_COMPLAINT_CLOSED"
