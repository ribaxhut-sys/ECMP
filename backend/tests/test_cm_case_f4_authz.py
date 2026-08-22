"""F4 AuthZ / visibility / SoD regression — party, role, unit, creator conflict.

Domain dual-acceptance tests remain in ``test_cm_case_mode_a.py``.
This module covers gaps A–D (Owner visibility, party/unit, Agent vs
Supervisor/Manager, creator SoD) without rebuilding the domain rules.
"""

from __future__ import annotations

import uuid
from collections.abc import Generator
from typing import Any

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker
from sqlalchemy.pool import StaticPool

from app.core.authorization.authentication import get_current_principal
from app.core.authorization.case_acceptance import (
    assert_case_acceptance_authorized,
    assert_case_resolve_accept_authorized,
    principal_is_case_agent,
    principal_may_give_case_acceptance,
)
from app.core.authorization.org_unit_guard import enforce_org_scope_any
from app.core.authorization.principal import Principal
from app.core.authorization.visibility import DEFAULT_PUSAT_UNIT_CODES, VisibilityClass
from app.core.config import Settings, get_settings
from app.core.errors import OrgScopeDeniedError, PermissionDeniedError
from app.db.base import Base
from app.db.session import get_db_session
from app.main import create_app
from app.modules.cm_batch1.models import CmBatch1ComplaintORM
from app.modules.cm_case.api.router import get_case_service
from app.modules.cm_case.application.dto import (
    CreateCaseCommand,
    UpdateStatusCommand,
)
from app.modules.cm_case.application.services import (
    CaseApplicationService,
    NoOpSideEffects,
)
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
    owning_unit_id: str | None = "UPPPD-GAMBIR",
    created_by: str | None = "seed-creator",
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
        status="REGISTERED",
        case_created=False,
        created_by=created_by,
        owning_unit_id=owning_unit_id,
    )
    session.add(row)
    session.commit()
    return str(row.id)


def _svc(session: Session) -> CaseApplicationService:
    return CaseApplicationService(
        SqlAlchemyCaseRepository(session),
        side_effects=NoOpSideEffects(),
    )


def _principal(
    *,
    user_id: uuid.UUID | None = None,
    roles: tuple[str, ...] = (),
    org_unit_id: str | None = None,
    permissions: frozenset[str] | None = None,
) -> Principal:
    return Principal(
        user_id=user_id or uuid.uuid4(),
        roles=roles,
        org_unit_id=org_unit_id,
        permissions=permissions
        or frozenset({"complaints:create", "complaints:read", "complaints:update"}),
    )


def _jwt_settings() -> Settings:
    return Settings(
        environment="development",
        ecmp_auth_mode="jwt",
        ecmp_env="shared",
        oidc_issuer="http://localhost:8180/realms/ecmp",
        oidc_audience="ecmp-api",
        oidc_jwks_url="http://jwks.test/certs",
        jwt_secret_key="test-secret-key-for-f4-authz",
        jwt_algorithm="HS256",
    )


# --- Pure AuthZ helpers -----------------------------------------------------


def test_agent_may_accept_on_own_unit_only() -> None:
    agent = _principal(roles=("AGENT",), org_unit_id="UPPPD-GAMBIR")
    assert principal_is_case_agent(agent) is True
    assert principal_may_give_case_acceptance(agent) is False
    # Own Handling Unit — Mode A Tutup allowed.
    assert_case_acceptance_authorized(
        agent,
        party="HANDLING_UNIT",
        owner_unit_id="UPPPD-GAMBIR",
        handling_unit_id="UPPPD-GAMBIR",
        actor_unit_id="UPPPD-GAMBIR",
        complaint_creator_id=None,
    )
    assert_case_acceptance_authorized(
        agent,
        party="OWNER",
        owner_unit_id="UPPPD-GAMBIR",
        handling_unit_id="PUSAT",
        actor_unit_id="UPPPD-GAMBIR",
        complaint_creator_id=None,
    )
    # Cross-unit Owner (agent at Gambir, owner is Pusat) — denied.
    with pytest.raises(PermissionDeniedError):
        assert_case_acceptance_authorized(
            agent,
            party="OWNER",
            owner_unit_id="PUSAT",
            handling_unit_id="PUSAT",
            actor_unit_id="UPPPD-GAMBIR",
            complaint_creator_id=None,
        )
    # Cross-unit Handling — denied.
    with pytest.raises(PermissionDeniedError):
        assert_case_acceptance_authorized(
            agent,
            party="HANDLING_UNIT",
            owner_unit_id="UPPPD-GAMBIR",
            handling_unit_id="PUSAT",
            actor_unit_id="UPPPD-GAMBIR",
            complaint_creator_id=None,
        )


def test_agent_resolve_accept_allowed_on_own_handling_unit() -> None:
    agent = _principal(roles=("AGENT",), org_unit_id="UPPPD-GAMBIR")
    assert_case_resolve_accept_authorized(
        agent,
        handling_unit_id="UPPPD-GAMBIR",
        actor_unit_id="UPPPD-GAMBIR",
        complaint_creator_id=None,
    )
    with pytest.raises(PermissionDeniedError):
        assert_case_resolve_accept_authorized(
            agent,
            handling_unit_id="PUSAT",
            actor_unit_id="UPPPD-GAMBIR",
            complaint_creator_id=None,
        )


def test_supervisor_authorized_on_matching_unit() -> None:
    uid = uuid.uuid4()
    supervisor = _principal(
        user_id=uid, roles=("SUPERVISOR",), org_unit_id="UPPPD-GAMBIR"
    )
    assert_case_acceptance_authorized(
        supervisor,
        party="OWNER",
        owner_unit_id="UPPPD-GAMBIR",
        handling_unit_id="PUSAT",
        actor_unit_id="UPPPD-GAMBIR",
        complaint_creator_id=None,
    )


def test_manager_authorized_on_matching_unit() -> None:
    manager = _principal(roles=("MANAGER",), org_unit_id="PUSAT")
    assert_case_acceptance_authorized(
        manager,
        party="HANDLING_UNIT",
        owner_unit_id="UPPPD-GAMBIR",
        handling_unit_id="PUSAT",
        actor_unit_id="PUSAT",
        complaint_creator_id=None,
    )


def test_owner_party_requires_owner_unit_not_handling_unit() -> None:
    supervisor = _principal(roles=("SUPERVISOR",), org_unit_id="PUSAT")
    with pytest.raises(PermissionDeniedError):
        assert_case_acceptance_authorized(
            supervisor,
            party="OWNER",
            owner_unit_id="UPPPD-GAMBIR",
            handling_unit_id="PUSAT",
            actor_unit_id="PUSAT",
            complaint_creator_id=None,
        )


def test_handling_party_requires_current_handling_unit() -> None:
    supervisor = _principal(roles=("SUPERVISOR",), org_unit_id="UPPPD-GAMBIR")
    with pytest.raises(PermissionDeniedError):
        assert_case_acceptance_authorized(
            supervisor,
            party="HANDLING_UNIT",
            owner_unit_id="UPPPD-GAMBIR",
            handling_unit_id="PUSAT",
            actor_unit_id="UPPPD-GAMBIR",
            complaint_creator_id=None,
        )


def test_creator_sod_allows_own_unit_supervisor_self_close() -> None:
    """2026-08-19: Supervisor/Manager closing a case they authored on their
    own unit does not need a second Supervisor/Manager (mirrors the Agent
    own-unit exemption)."""
    creator = uuid.uuid4()
    supervisor = _principal(
        user_id=creator, roles=("SUPERVISOR",), org_unit_id="UPPPD-GAMBIR"
    )
    assert_case_acceptance_authorized(
        supervisor,
        party="OWNER",
        owner_unit_id="UPPPD-GAMBIR",
        handling_unit_id="UPPPD-GAMBIR",
        actor_unit_id="UPPPD-GAMBIR",
        complaint_creator_id=str(creator),
    )


def test_creator_sod_blocks_cross_unit_self_approval() -> None:
    """Creator SoD still applies when the approver is not on the party's
    own unit — the own-unit exemption does not extend cross-unit."""
    creator = uuid.uuid4()
    supervisor = _principal(
        user_id=creator, roles=("SUPERVISOR",), org_unit_id="UPPPD-GAMBIR"
    )
    with pytest.raises(PermissionDeniedError):
        assert_case_acceptance_authorized(
            supervisor,
            party="OWNER",
            owner_unit_id="PUSAT",
            handling_unit_id="PUSAT",
            actor_unit_id="UPPPD-GAMBIR",
            complaint_creator_id=str(creator),
        )


def test_creator_sod_blocks_admin_unconditionally() -> None:
    creator = uuid.uuid4()
    admin = _principal(user_id=creator, roles=("ADMIN",), org_unit_id="UPPPD-GAMBIR")
    with pytest.raises(PermissionDeniedError):
        assert_case_acceptance_authorized(
            admin,
            party="OWNER",
            owner_unit_id="UPPPD-GAMBIR",
            handling_unit_id="UPPPD-GAMBIR",
            actor_unit_id="UPPPD-GAMBIR",
            complaint_creator_id=str(creator),
        )


def test_agent_resolve_accept_denied() -> None:
    agent = _principal(roles=("AGENT",), org_unit_id="UPPPD-GAMBIR")
    with pytest.raises(PermissionDeniedError):
        assert_case_resolve_accept_authorized(
            agent,
            handling_unit_id="PUSAT",
            actor_unit_id="UPPPD-GAMBIR",
            complaint_creator_id=None,
        )


def test_enforce_org_scope_any_allows_owner_or_handling() -> None:
    settings = _jwt_settings()
    owner = _principal(org_unit_id="UPPPD-GAMBIR")
    enforce_org_scope_any(owner, ("PUSAT", "UPPPD-GAMBIR"), settings)
    stranger = _principal(org_unit_id="OTHER")
    with pytest.raises(OrgScopeDeniedError):
        enforce_org_scope_any(stranger, ("PUSAT", "UPPPD-GAMBIR"), settings)


# --- List / repository visibility (gap A) -----------------------------------


def test_owner_unit_sees_case_in_list_after_handling_transfer(
    db_session: Session,
) -> None:
    svc = _svc(db_session)
    complaint_id = _seed_complaint(db_session, owning_unit_id="UPPPD-GAMBIR")
    created = svc.create_case(
        CreateCaseCommand(
            complaint_id=complaint_id,
            case_type="BILLING",
            subject="Owner visibility",
            description="desc",
            priority="MEDIUM",
            destination_unit_id="UPPPD-GAMBIR",
            actor_id="agent-1",
        )
    )
    svc.update_status(
        UpdateStatusCommand(
            case_id=created.case_id,
            to_status="ASSIGNED",
            actor_id="agent-1",
            destination_unit_id="PUSAT",
        )
    )
    repo = SqlAlchemyCaseRepository(db_session)
    rows, total = repo.list_summaries(
        visibility=VisibilityClass.UNIT.value,
        actor_id="supervisor-branch",
        org_unit_id="UPPPD-GAMBIR",
        pusat_unit_codes=DEFAULT_PUSAT_UNIT_CODES,
    )
    assert total == 1
    assert str(rows[0].id) == created.case_id
    assert rows[0].owning_unit_id == "PUSAT"
    assert rows[0].owner_unit_id == "UPPPD-GAMBIR"


def test_pusat_queue_includes_cases_held_by_a_pusat_sub_unit(
    db_session: Session,
) -> None:
    """Handling moved to a Pusat sub-unit (Suban) must stay in the Pusat queue."""
    svc = _svc(db_session)
    complaint_id = _seed_complaint(db_session, owning_unit_id="UPPPD-GAMBIR")
    created = svc.create_case(
        CreateCaseCommand(
            complaint_id=complaint_id,
            case_type="BILLING",
            subject="Suban handling",
            description="desc",
            priority="MEDIUM",
            destination_unit_id="UPPPD-GAMBIR",
            actor_id="agent-1",
        )
    )
    svc.update_status(
        UpdateStatusCommand(
            case_id=created.case_id,
            to_status="ASSIGNED",
            actor_id="agent-1",
            destination_unit_id="PUSAT-SUBAN-1",
        )
    )
    repo = SqlAlchemyCaseRepository(db_session)
    rows, total = repo.list_summaries(
        visibility=VisibilityClass.PUSAT.value,
        actor_id="hq-supervisor",
        org_unit_id="PUSAT-CRO",
        pusat_unit_codes=DEFAULT_PUSAT_UNIT_CODES,
    )
    assert total == 1
    assert rows[0].owning_unit_id == "PUSAT-SUBAN-1"


def test_pusat_owner_sees_case_after_handoff_to_branch(db_session: Session) -> None:
    svc = _svc(db_session)
    complaint_id = _seed_complaint(db_session, owning_unit_id="PUSAT")
    created = svc.create_case(
        CreateCaseCommand(
            complaint_id=complaint_id,
            case_type="BILLING",
            subject="Pusat owner",
            description="desc",
            priority="MEDIUM",
            destination_unit_id="PUSAT",
            actor_id="hq-1",
        )
    )
    svc.update_status(
        UpdateStatusCommand(
            case_id=created.case_id,
            to_status="ASSIGNED",
            actor_id="hq-1",
            destination_unit_id="UPPPD-GAMBIR",
        )
    )
    repo = SqlAlchemyCaseRepository(db_session)
    rows, total = repo.list_summaries(
        visibility=VisibilityClass.PUSAT.value,
        actor_id="hq-supervisor",
        org_unit_id="PUSAT",
        pusat_unit_codes=DEFAULT_PUSAT_UNIT_CODES,
    )
    assert total == 1
    assert rows[0].owner_unit_id == "PUSAT"
    assert rows[0].owning_unit_id == "UPPPD-GAMBIR"


# --- HTTP AuthZ -------------------------------------------------------------


def _http_client(
    db_session: Session,
    *,
    principal: Principal,
    jwt: bool = False,
) -> tuple[TestClient, dict[str, Any]]:
    app = create_app()
    svc = _svc(db_session)
    state: dict[str, Any] = {"principal": principal}
    app.dependency_overrides[get_case_service] = lambda: svc
    app.dependency_overrides[get_current_principal] = lambda: state["principal"]
    app.dependency_overrides[get_db_session] = lambda: db_session
    if jwt:
        settings = _jwt_settings()
        app.dependency_overrides[get_settings] = lambda: settings
    client = TestClient(app)
    return client, state


def _bring_to_resolved(
    client: TestClient,
    *,
    complaint_id: str,
    unit: str,
) -> str:
    create = client.post(
        "/api/v1/cm/cases",
        json={
            "complaintId": complaint_id,
            "caseType": "BILLING",
            "subject": "F4 authz",
            "description": "via HTTP",
            "priority": "MEDIUM",
            "destinationUnitId": unit,
        },
    )
    assert create.status_code == 201, create.text
    case_id = create.json()["data"]["caseId"]
    assert (
        client.patch(
            f"/api/v1/cm/cases/{case_id}/status",
            json={"toStatus": "IN_PROGRESS"},
        ).status_code
        == 200
    )
    resolve = client.post(
        f"/api/v1/cm/cases/{case_id}/resolve",
        json={
            "action": "ACCEPT",
            "comment": "OK",
            "resolutionCode": "FIXED",
            "summary": "Done",
        },
    )
    assert resolve.status_code == 200, resolve.text
    return case_id


def test_http_agent_can_handler_and_owner_acceptance_on_own_unit(
    db_session: Session,
) -> None:
    agent_id = uuid.uuid4()
    agent = _principal(
        user_id=agent_id, roles=("AGENT",), org_unit_id="UPPPD-GAMBIR"
    )
    # Seed + bring to IN_PROGRESS as Agent, then ACCEPT resolve (HU stamp).
    client, state = _http_client(db_session, principal=agent)
    try:
        complaint_id = _seed_complaint(db_session, owning_unit_id="UPPPD-GAMBIR")
        create = client.post(
            "/api/v1/cm/cases",
            json={
                "complaintId": complaint_id,
                "caseType": "BILLING",
                "subject": "Agent own-unit close",
                "description": "desc",
                "priority": "MEDIUM",
                "destinationUnitId": "UPPPD-GAMBIR",
            },
        )
        assert create.status_code == 201, create.text
        case_id = create.json()["data"]["caseId"]
        assert (
            client.patch(
                f"/api/v1/cm/cases/{case_id}/status",
                json={"toStatus": "IN_PROGRESS"},
            ).status_code
            == 200
        )
        resolve = client.post(
            f"/api/v1/cm/cases/{case_id}/resolve",
            json={
                "action": "ACCEPT",
                "comment": "Selesai di cabang",
                "resolutionCode": "FIXED",
                "summary": "Done",
            },
        )
        assert resolve.status_code == 200, resolve.text

        # Explicit Owner ACCEPT on same unit also allowed for Agent.
        owner = client.post(
            f"/api/v1/cm/cases/{case_id}/acceptance",
            json={"party": "OWNER", "decision": "ACCEPT", "note": "OK"},
        )
        # May be 200 (needed) or 409/4xx if already satisfied — not 403 role deny.
        assert owner.status_code != 403, owner.text
    finally:
        client.app.dependency_overrides.clear()


def test_http_agent_can_resolve_accept_on_own_unit(db_session: Session) -> None:
    agent = _principal(roles=("AGENT",), org_unit_id="UPPPD-GAMBIR")
    client, _state = _http_client(db_session, principal=agent)
    try:
        complaint_id = _seed_complaint(db_session, owning_unit_id="UPPPD-GAMBIR")
        create = client.post(
            "/api/v1/cm/cases",
            json={
                "complaintId": complaint_id,
                "caseType": "BILLING",
                "subject": "Agent accept",
                "description": "desc",
                "priority": "MEDIUM",
                "destinationUnitId": "UPPPD-GAMBIR",
            },
        )
        case_id = create.json()["data"]["caseId"]
        client.patch(
            f"/api/v1/cm/cases/{case_id}/status",
            json={"toStatus": "IN_PROGRESS"},
        )
        accepted = client.post(
            f"/api/v1/cm/cases/{case_id}/resolve",
            json={
                "action": "ACCEPT",
                "comment": "OK",
                "resolutionCode": "FIXED",
                "summary": "Done",
            },
        )
        assert accepted.status_code == 200, accepted.text
        assert accepted.json()["data"]["status"] in {
            "RESOLVED",
            "CLOSED",
            "IN_PROGRESS",
        }
        # PROPOSE still available as alternate path.
        propose_case = client.post(
            "/api/v1/cm/cases",
            json={
                "complaintId": complaint_id,
                "caseType": "BILLING",
                "subject": "Agent propose still works",
                "description": "desc",
                "priority": "MEDIUM",
                "destinationUnitId": "UPPPD-GAMBIR",
            },
        )
        propose_id = propose_case.json()["data"]["caseId"]
        client.patch(
            f"/api/v1/cm/cases/{propose_id}/status",
            json={"toStatus": "IN_PROGRESS"},
        )
        propose = client.post(
            f"/api/v1/cm/cases/{propose_id}/resolve",
            json={
                "action": "PROPOSE",
                "comment": "Please review",
                "resolutionCode": "FIXED",
                "summary": "Proposed fix",
            },
        )
        assert propose.status_code == 200, propose.text
    finally:
        client.app.dependency_overrides.clear()


def test_http_supervisor_creator_can_close_on_own_unit(
    db_session: Session,
) -> None:
    """2026-08-19: creator Supervisor may close their own-unit case alone."""
    creator = uuid.uuid4()
    client, state = _http_client(
        db_session,
        principal=_principal(
            user_id=creator, roles=("SUPERVISOR",), org_unit_id="UPPPD-GAMBIR"
        ),
    )
    try:
        complaint_id = _seed_complaint(
            db_session,
            owning_unit_id="UPPPD-GAMBIR",
            created_by=str(creator),
        )
        case_id = _bring_to_resolved(
            client, complaint_id=complaint_id, unit="UPPPD-GAMBIR"
        )
        allowed = client.post(
            f"/api/v1/cm/cases/{case_id}/acceptance",
            json={"party": "OWNER", "decision": "ACCEPT"},
        )
        assert allowed.status_code == 200, allowed.text
        assert allowed.json()["data"]["status"] == "CLOSED"
    finally:
        client.app.dependency_overrides.clear()


def test_http_supervisor_creator_sod_blocks_cross_unit_owner_acceptance(
    db_session: Session,
) -> None:
    """Creator SoD still applies when the Supervisor is acting cross-unit."""
    creator = uuid.uuid4()
    client, state = _http_client(
        db_session,
        principal=_principal(
            user_id=creator, roles=("SUPERVISOR",), org_unit_id="PUSAT"
        ),
    )
    try:
        complaint_id = _seed_complaint(
            db_session,
            owning_unit_id="UPPPD-GAMBIR",
            created_by=str(creator),
        )
        # Handling unit = Pusat (creator's own unit) so the resolve-ACCEPT
        # step itself succeeds; Owner unit stays Gambir for the real test.
        case_id = _bring_to_resolved(
            client, complaint_id=complaint_id, unit="PUSAT"
        )
        # Creator Supervisor at Pusat, Owner unit is Gambir — SoD deny.
        denied = client.post(
            f"/api/v1/cm/cases/{case_id}/acceptance",
            json={"party": "OWNER", "decision": "ACCEPT"},
        )
        assert denied.status_code == 403
        # Different Supervisor on Owner unit may accept.
        other = uuid.uuid4()
        state["principal"] = _principal(
            user_id=other, roles=("SUPERVISOR",), org_unit_id="UPPPD-GAMBIR"
        )
        allowed = client.post(
            f"/api/v1/cm/cases/{case_id}/acceptance",
            json={"party": "OWNER", "decision": "ACCEPT"},
        )
        assert allowed.status_code == 200, allowed.text
        assert allowed.json()["data"]["status"] == "CLOSED"
    finally:
        client.app.dependency_overrides.clear()


def test_http_manager_creator_can_resolve_accept_on_own_unit(
    db_session: Session,
) -> None:
    """2026-08-19: Manager may resolve-ACCEPT (own-unit Handling stamp) on a
    case they created themselves without a second Supervisor/Manager."""
    creator = uuid.uuid4()
    client, _state = _http_client(
        db_session,
        principal=_principal(
            user_id=creator, roles=("MANAGER",), org_unit_id="UPPPD-GAMBIR"
        ),
    )
    try:
        complaint_id = _seed_complaint(
            db_session,
            owning_unit_id="UPPPD-GAMBIR",
            created_by=str(creator),
        )
        create = client.post(
            "/api/v1/cm/cases",
            json={
                "complaintId": complaint_id,
                "caseType": "BILLING",
                "subject": "Manager creator",
                "description": "desc",
                "priority": "MEDIUM",
                "destinationUnitId": "UPPPD-GAMBIR",
            },
        )
        case_id = create.json()["data"]["caseId"]
        client.patch(
            f"/api/v1/cm/cases/{case_id}/status",
            json={"toStatus": "IN_PROGRESS"},
        )
        allowed = client.post(
            f"/api/v1/cm/cases/{case_id}/resolve",
            json={
                "action": "ACCEPT",
                "comment": "OK",
                "resolutionCode": "FIXED",
                "summary": "Done",
            },
        )
        assert allowed.status_code == 200, allowed.text
    finally:
        client.app.dependency_overrides.clear()


def test_http_manager_creator_sod_blocks_cross_unit_resolve_accept(
    db_session: Session,
) -> None:
    """Creator SoD still applies for a Manager resolving cross-unit."""
    creator = uuid.uuid4()
    client, _state = _http_client(
        db_session,
        principal=_principal(
            user_id=creator, roles=("MANAGER",), org_unit_id="PUSAT"
        ),
    )
    try:
        complaint_id = _seed_complaint(
            db_session,
            owning_unit_id="UPPPD-GAMBIR",
            created_by=str(creator),
        )
        create = client.post(
            "/api/v1/cm/cases",
            json={
                "complaintId": complaint_id,
                "caseType": "BILLING",
                "subject": "Manager creator cross-unit",
                "description": "desc",
                "priority": "MEDIUM",
                "destinationUnitId": "UPPPD-GAMBIR",
            },
        )
        case_id = create.json()["data"]["caseId"]
        client.patch(
            f"/api/v1/cm/cases/{case_id}/status",
            json={"toStatus": "IN_PROGRESS"},
        )
        denied = client.post(
            f"/api/v1/cm/cases/{case_id}/resolve",
            json={
                "action": "ACCEPT",
                "comment": "OK",
                "resolutionCode": "FIXED",
                "summary": "Done",
            },
        )
        assert denied.status_code == 403
    finally:
        client.app.dependency_overrides.clear()


def test_http_owner_visibility_after_transfer_jwt(db_session: Session) -> None:
    """Gap A: Owner unit still GET Case after Handling Unit moves (jwt org-scope)."""
    branch_supervisor = _principal(
        roles=("SUPERVISOR",), org_unit_id="UPPPD-GAMBIR"
    )
    client, state = _http_client(
        db_session, principal=branch_supervisor, jwt=True
    )
    try:
        complaint_id = _seed_complaint(db_session, owning_unit_id="UPPPD-GAMBIR")
        create = client.post(
            "/api/v1/cm/cases",
            json={
                "complaintId": complaint_id,
                "caseType": "BILLING",
                "subject": "Transfer visibility",
                "description": "desc",
                "priority": "MEDIUM",
                "destinationUnitId": "UPPPD-GAMBIR",
            },
        )
        case_id = create.json()["data"]["caseId"]
        # Hand off to Pusat (handling mutation from current handling unit).
        handoff = client.patch(
            f"/api/v1/cm/cases/{case_id}/status",
            json={"toStatus": "ASSIGNED", "destinationUnitId": "PUSAT"},
        )
        assert handoff.status_code == 200, handoff.text
        assert handoff.json()["data"]["owningUnitId"] == "PUSAT"
        assert handoff.json()["data"]["ownerUnitId"] == "UPPPD-GAMBIR"

        # Owner unit still reads Case + acceptance history fields.
        state["principal"] = _principal(
            roles=("SUPERVISOR",), org_unit_id="UPPPD-GAMBIR"
        )
        got = client.get(f"/api/v1/cm/cases/{case_id}")
        assert got.status_code == 200, got.text
        body = got.json()["data"]
        assert body["ownerUnitId"] == "UPPPD-GAMBIR"
        assert body["owningUnitId"] == "PUSAT"
        assert "acceptanceHistory" in body

        # Unrelated unit still denied.
        state["principal"] = _principal(roles=("SUPERVISOR",), org_unit_id="OTHER")
        denied = client.get(f"/api/v1/cm/cases/{case_id}")
        assert denied.status_code == 403
        assert denied.json()["code"] == "ORG_SCOPE_DENIED"
    finally:
        client.app.dependency_overrides.clear()


def test_http_owner_acceptance_after_transfer_by_owner_supervisor(
    db_session: Session,
) -> None:
    """Gap B+C: OWNER party binds to Owner unit; HANDLING_UNIT to current HU."""
    pusat = _principal(roles=("SUPERVISOR",), org_unit_id="PUSAT")
    client, state = _http_client(db_session, principal=pusat, jwt=True)
    try:
        complaint_id = _seed_complaint(db_session, owning_unit_id="UPPPD-GAMBIR")
        # Create under Pusat handling (destination) while Owner = Cabang.
        create = client.post(
            "/api/v1/cm/cases",
            json={
                "complaintId": complaint_id,
                "caseType": "BILLING",
                "subject": "Party unit",
                "description": "desc",
                "priority": "MEDIUM",
                "destinationUnitId": "PUSAT",
            },
        )
        case_id = create.json()["data"]["caseId"]
        client.patch(
            f"/api/v1/cm/cases/{case_id}/status",
            json={"toStatus": "IN_PROGRESS"},
        )
        assert (
            client.post(
                f"/api/v1/cm/cases/{case_id}/resolve",
                json={
                    "action": "ACCEPT",
                    "comment": "OK",
                    "resolutionCode": "FIXED",
                    "summary": "Done",
                },
            ).status_code
            == 200
        )

        # Handling Unit Supervisor must not submit OWNER acceptance.
        wrong = client.post(
            f"/api/v1/cm/cases/{case_id}/acceptance",
            json={"party": "OWNER", "decision": "ACCEPT"},
        )
        assert wrong.status_code == 403

        # Owner-unit Supervisor may submit Owner acceptance.
        state["principal"] = _principal(
            roles=("SUPERVISOR",), org_unit_id="UPPPD-GAMBIR"
        )
        ok = client.post(
            f"/api/v1/cm/cases/{case_id}/acceptance",
            json={"party": "OWNER", "decision": "ACCEPT"},
        )
        assert ok.status_code == 200, ok.text
        assert ok.json()["data"]["ownerAcceptance"]["decision"] == "ACCEPT"
        assert ok.json()["data"]["status"] == "CLOSED"
    finally:
        client.app.dependency_overrides.clear()


def test_http_manager_can_owner_acceptance(db_session: Session) -> None:
    supervisor = _principal(roles=("SUPERVISOR",), org_unit_id="UPPPD-GAMBIR")
    client, state = _http_client(db_session, principal=supervisor)
    try:
        complaint_id = _seed_complaint(db_session, owning_unit_id="UPPPD-GAMBIR")
        case_id = _bring_to_resolved(
            client, complaint_id=complaint_id, unit="UPPPD-GAMBIR"
        )
        state["principal"] = _principal(
            roles=("MANAGER",), org_unit_id="UPPPD-GAMBIR"
        )
        ok = client.post(
            f"/api/v1/cm/cases/{case_id}/acceptance",
            json={"party": "OWNER", "decision": "ACCEPT"},
        )
        assert ok.status_code == 200, ok.text
        assert ok.json()["data"]["status"] == "CLOSED"
    finally:
        client.app.dependency_overrides.clear()


def test_roles_agent_supervisor_manager_can_create_via_permission(
    db_session: Session,
) -> None:
    """Creation: Agent / Supervisor / Manager with complaints:create."""
    for role in ("AGENT", "SUPERVISOR", "MANAGER"):
        principal = _principal(roles=(role,), org_unit_id="UPPPD-GAMBIR")
        client, _ = _http_client(db_session, principal=principal)
        try:
            complaint_id = _seed_complaint(
                db_session,
                owning_unit_id="UPPPD-GAMBIR",
                created_by=str(principal.user_id),
            )
            resp = client.post(
                "/api/v1/cm/cases",
                json={
                    "complaintId": complaint_id,
                    "caseType": "BILLING",
                    "subject": f"Create by {role}",
                    "description": "desc",
                    "priority": "MEDIUM",
                    "destinationUnitId": "UPPPD-GAMBIR",
                },
            )
            assert resp.status_code == 201, (role, resp.text)
            assert resp.json()["data"]["ownerUnitId"] == "UPPPD-GAMBIR"
        finally:
            client.app.dependency_overrides.clear()


def test_http_close_cannot_bypass_dual_acceptance(db_session: Session) -> None:
    supervisor = _principal(roles=("SUPERVISOR",), org_unit_id="UPPPD-GAMBIR")
    client, _ = _http_client(db_session, principal=supervisor)
    try:
        complaint_id = _seed_complaint(db_session, owning_unit_id="UPPPD-GAMBIR")
        case_id = _bring_to_resolved(
            client, complaint_id=complaint_id, unit="UPPPD-GAMBIR"
        )
        bypass = client.post(f"/api/v1/cm/cases/{case_id}/close", json={})
        assert bypass.status_code == 409
        assert bypass.json()["code"] == "OWNER_ACCEPTANCE_REQUIRED"
        assert client.get(f"/api/v1/cm/cases/{case_id}").json()["data"]["status"] == (
            "RESOLVED"
        )
    finally:
        client.app.dependency_overrides.clear()


def test_http_second_acceptance_triggers_closed(db_session: Session) -> None:
    supervisor = _principal(roles=("SUPERVISOR",), org_unit_id="UPPPD-GAMBIR")
    client, _ = _http_client(db_session, principal=supervisor)
    try:
        complaint_id = _seed_complaint(db_session, owning_unit_id="UPPPD-GAMBIR")
        case_id = _bring_to_resolved(
            client, complaint_id=complaint_id, unit="UPPPD-GAMBIR"
        )
        # HU already ACCEPT via resolve — Owner ACCEPT is the second party.
        closed = client.post(
            f"/api/v1/cm/cases/{case_id}/acceptance",
            json={"party": "OWNER", "decision": "ACCEPT"},
        )
        assert closed.status_code == 200, closed.text
        body = closed.json()["data"]
        assert body["status"] == "CLOSED"
        assert body["handlingUnitAcceptance"]["decision"] == "ACCEPT"
        assert body["ownerAcceptance"]["decision"] == "ACCEPT"
        assert len(body["acceptanceHistory"]) >= 2
    finally:
        client.app.dependency_overrides.clear()


def test_manager_escalate_and_close_gates_allow_manager() -> None:
    from app.core.authorization.gates import (
        require_complaint_close,
        require_supervisor_escalate,
    )

    manager = _principal(
        roles=("MANAGER",),
        permissions=frozenset(
            {
                "complaints:escalate",
                "complaints:close",
            }
        ),
    )
    assert require_supervisor_escalate(manager) is manager
    assert require_complaint_close(manager) is manager
