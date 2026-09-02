"""Pengaduan Internal — domain + persistence + authz regression (checklist 1–35)."""

from __future__ import annotations

import uuid
from collections.abc import Callable, Generator

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine, event
from sqlalchemy.orm import Session, sessionmaker
from sqlalchemy.pool import StaticPool

from app.core.authorization.authentication import get_current_principal
from app.core.authorization.case_acceptance import assert_case_acceptance_authorized
from app.core.authorization.principal import Principal
from app.core.config import Settings, get_settings
from app.core.errors import ApiError, PermissionDeniedError
from app.db.base import Base
from app.db.session import get_db_session
from app.main import create_app
from app.modules.cm_batch1.models import CmBatch1ComplaintORM
from app.modules.internal_complaint.api.router import get_internal_complaint_service
from app.modules.internal_complaint.application.dto import (
    CloseCommand,
    CreateInternalComplaintCommand,
    DecideTransferRequestCommand,
    DecideWithdrawRequestCommand,
    RecordAcceptanceCommand,
    RequestTransferCommand,
    RequestWithdrawCommand,
    ResendToPusatCommand,
    ResolveCommand,
    ReturnForCompletionCommand,
    StartHandlingCommand,
    TransferCommand,
    WithdrawCommand,
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
    InternalComplaintUnitCounterORM,
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
    InternalComplaintUnitCounterORM.__table__,
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


def _to_in_progress(
    service: InternalComplaintApplicationService,
    complaint_id: str,
    *,
    actor_id: str = "handler-sv",
    unit: str = "PUSAT",
) -> None:
    current = service.get(complaint_id)
    if current.handling_unit_id != unit:
        service.transfer(
            TransferCommand(
                complaint_id=complaint_id,
                destination_unit_id=unit,
                actor_id=actor_id,
                actor_unit_id=current.owner_unit_id,
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


def _propose_resolution(
    service: InternalComplaintApplicationService,
    complaint_id: str,
    *,
    actor_id: str,
    unit: str,
    comment: str = "Done",
    summary: str = "Fixed",
    resolution_code: str | None = "IC_DONE",
) -> None:
    service.resolve(
        ResolveCommand(
            complaint_id=complaint_id,
            action="PROPOSE",
            comment=comment,
            resolution_code=resolution_code,
            summary=summary,
            actor_id=actor_id,
            actor_unit_id=unit,
        )
    )


def _to_resolved(
    service: InternalComplaintApplicationService,
    complaint_id: str,
    *,
    actor_id: str = "handler-sv",
    unit: str = "PUSAT",
    owner_id: str = "owner-sv",
) -> None:
    current = service.get(complaint_id)
    owner_unit = current.owner_unit_id
    _to_in_progress(service, complaint_id, actor_id=actor_id, unit=unit)
    _propose_resolution(
        service, complaint_id, actor_id=actor_id, unit=unit
    )
    service.resolve(
        ResolveCommand(
            complaint_id=complaint_id,
            action="ACCEPT",
            comment="Usulan diterima",
            summary="Fixed",
            actor_id=owner_id,
            actor_unit_id=owner_unit,
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


def test_transfer_to_pusat_subunit_collapses_to_pusat(
    service: InternalComplaintApplicationService,
):
    cid = _create(service, owner_unit_id="UPPPD-GAMBIR")
    dto = service.transfer(
        TransferCommand(
            complaint_id=cid,
            destination_unit_id="PUSAT-CRO",
            actor_id="sv-1",
            actor_unit_id="UPPPD-GAMBIR",
            reason="to HQ CRO",
        )
    )
    assert dto.handling_unit_id == "PUSAT"


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


def test_branch_actor_cannot_redirect_from_pusat_to_another_branch(
    service: InternalComplaintApplicationService,
):
    cid = _create(service, owner_unit_id="UPPPD-GAMBIR")
    service.transfer(
        TransferCommand(
            complaint_id=cid,
            destination_unit_id="PUSAT",
            actor_id="sv-gambir",
            actor_unit_id="UPPPD-GAMBIR",
            reason="to hq",
        )
    )
    with pytest.raises(Exception) as exc:
        service.transfer(
            TransferCommand(
                complaint_id=cid,
                destination_unit_id="UPPPD-MENTENG",
                actor_id="sv-gambir",
                actor_unit_id="UPPPD-GAMBIR",
                reason="peer branch",
            )
        )
    blob = f"{getattr(exc.value, 'code', '')} {exc.value}"
    assert "TRANSFER_DIRECTION_NOT_ALLOWED" in blob


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


def test_resolve_omitted_code_persists_ic_done(
    service: InternalComplaintApplicationService,
):
    cid = _create(service)
    service.start_handling(
        StartHandlingCommand(
            complaint_id=cid, actor_id="a", actor_unit_id="UPPPD-GAMBIR"
        )
    )
    dto = service.resolve(
        ResolveCommand(
            complaint_id=cid,
            action="PROPOSE",
            comment="Done",
            summary="Tindakan diambil",
            actor_id="a",
            actor_unit_id="UPPPD-GAMBIR",
        )
    )
    assert dto.status == "IN_PROGRESS"
    accepted = service.resolve(
        ResolveCommand(
            complaint_id=cid,
            action="ACCEPT",
            comment="Usulan diterima",
            actor_id="owner-sv",
            actor_unit_id="UPPPD-GAMBIR",
        )
    )
    assert accepted.status == "RESOLVED"
    assert accepted.resolution is not None
    assert accepted.resolution.resolution_code == "IC_DONE"
    assert accepted.resolution.summary == "Tindakan diambil"


def test_resolve_explicit_legacy_code_still_accepted(
    service: InternalComplaintApplicationService,
):
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
            comment="Done",
            resolution_code="IC-OK",
            summary="Legacy",
            actor_id="a",
            actor_unit_id="UPPPD-GAMBIR",
        )
    )
    dto = service.resolve(
        ResolveCommand(
            complaint_id=cid,
            action="ACCEPT",
            comment="Usulan diterima",
            actor_id="owner-sv",
            actor_unit_id="UPPPD-GAMBIR",
        )
    )
    assert dto.resolution is not None
    assert dto.resolution.resolution_code == "IC-OK"


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


def test_accept_without_proposal_rejected(
    service: InternalComplaintApplicationService,
):
    cid = _create(service)
    service.start_handling(
        StartHandlingCommand(
            complaint_id=cid, actor_id="a", actor_unit_id="UPPPD-GAMBIR"
        )
    )
    with pytest.raises(ApiError) as exc:
        service.resolve(
            ResolveCommand(
                complaint_id=cid,
                action="ACCEPT",
                comment="shortcut",
                summary="Fixed",
                actor_id="owner-sv",
                actor_unit_id="UPPPD-GAMBIR",
            )
        )
    assert exc.value.code == "RESOLUTION_PROPOSAL_REQUIRED"


def test_proposer_cannot_accept_own_proposal(
    service: InternalComplaintApplicationService,
):
    cid = _create(service)
    _to_in_progress(service, cid, actor_id="handler-sv", unit="PUSAT")
    _propose_resolution(service, cid, actor_id="handler-sv", unit="PUSAT")
    with pytest.raises(ApiError) as exc:
        service.resolve(
            ResolveCommand(
                complaint_id=cid,
                action="ACCEPT",
                comment="self",
                actor_id="handler-sv",
                actor_unit_id="UPPPD-GAMBIR",
            )
        )
    assert exc.value.code == "RESOLUTION_SELF_DECISION_NOT_ALLOWED"


def test_handling_unit_cannot_accept_transferred_proposal(
    service: InternalComplaintApplicationService,
):
    cid = _create(service)
    _to_in_progress(service, cid, actor_id="handler-sv", unit="PUSAT")
    _propose_resolution(service, cid, actor_id="handler-sv", unit="PUSAT")
    with pytest.raises(ApiError) as exc:
        service.resolve(
            ResolveCommand(
                complaint_id=cid,
                action="ACCEPT",
                comment="same unit",
                actor_id="other-pusat",
                actor_unit_id="PUSAT",
            )
        )
    assert exc.value.code == "RESOLUTION_OWNER_UNIT_REQUIRED"


def test_owner_accepts_pending_proposal(
    service: InternalComplaintApplicationService,
):
    cid = _create(service)
    _to_in_progress(service, cid, actor_id="handler-sv", unit="PUSAT")
    _propose_resolution(
        service, cid, actor_id="handler-sv", unit="PUSAT", summary="Selesai di Pusat"
    )
    dto = service.resolve(
        ResolveCommand(
            complaint_id=cid,
            action="ACCEPT",
            comment="",
            actor_id="owner-sv",
            actor_unit_id="UPPPD-GAMBIR",
        )
    )
    assert dto.status == "RESOLVED"
    assert dto.resolution is not None
    assert dto.resolution.status == "ACCEPTED"
    assert dto.resolution.summary == "Selesai di Pusat"
    assert dto.handling_unit_acceptance is not None
    assert dto.handling_unit_acceptance.actor_id == "handler-sv"
    assert dto.owner_acceptance is None


def test_owner_rejects_pending_proposal(
    service: InternalComplaintApplicationService,
):
    cid = _create(service)
    _to_in_progress(service, cid, actor_id="handler-sv", unit="PUSAT")
    _propose_resolution(service, cid, actor_id="handler-sv", unit="PUSAT")
    dto = service.resolve(
        ResolveCommand(
            complaint_id=cid,
            action="REJECT",
            comment="Belum lengkap",
            rejection_reason="Belum lengkap",
            actor_id="owner-sv",
            actor_unit_id="UPPPD-GAMBIR",
        )
    )
    assert dto.status == "IN_PROGRESS"
    assert dto.resolution is not None
    assert dto.resolution.status == "REJECTED"


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
    _propose_resolution(
        service,
        cid,
        actor_id="handler-sv",
        unit="PUSAT",
        comment="Done2",
        summary="Fixed2",
        resolution_code="IC-OK2",
    )
    service.resolve(
        ResolveCommand(
            complaint_id=cid,
            action="ACCEPT",
            comment="Usulan diterima",
            actor_id="owner-sv",
            actor_unit_id="UPPPD-GAMBIR",
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


def test_agent_may_final_acceptance_on_own_unit():
    """Mode A: Agent may OWNER-accept on their own unit (DEC-021 Tutup path)."""
    agent = _principal(roles=("AGENT",), org_unit_id="UPPPD-GAMBIR")
    assert_case_acceptance_authorized(
        agent,
        party="OWNER",
        owner_unit_id="UPPPD-GAMBIR",
        handling_unit_id="PUSAT",
        actor_unit_id="UPPPD-GAMBIR",
        complaint_creator_id="someone-else",
    )


def test_agent_cannot_final_acceptance_cross_unit():
    agent = _principal(roles=("AGENT",), org_unit_id="UPPPD-GAMBIR")
    with pytest.raises(PermissionDeniedError):
        assert_case_acceptance_authorized(
            agent,
            party="OWNER",
            owner_unit_id="PUSAT",
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


def test_creator_may_be_sole_approver_on_own_unit():
    """2026-08-19: Supervisor/Manager closing their own-unit case they
    authored no longer needs a second Supervisor/Manager."""
    creator_id = uuid.uuid4()
    sv = _principal(
        user_id=creator_id, roles=("SUPERVISOR",), org_unit_id="UPPPD-GAMBIR"
    )
    assert_case_acceptance_authorized(
        sv,
        party="OWNER",
        owner_unit_id="UPPPD-GAMBIR",
        handling_unit_id="PUSAT",
        actor_unit_id="UPPPD-GAMBIR",
        complaint_creator_id=str(creator_id),
    )


def test_creator_cannot_be_sole_approver_cross_unit():
    creator_id = uuid.uuid4()
    sv = _principal(
        user_id=creator_id, roles=("SUPERVISOR",), org_unit_id="PUSAT"
    )
    with pytest.raises(PermissionDeniedError):
        assert_case_acceptance_authorized(
            sv,
            party="OWNER",
            owner_unit_id="UPPPD-GAMBIR",
            handling_unit_id="PUSAT",
            actor_unit_id="PUSAT",
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


# --- Transfer request gate (domain, via service) ----------------------------


def test_request_transfer_branch_to_branch_rejected(
    service: InternalComplaintApplicationService,
):
    cid = _create(service, owner_unit_id="UPPPD-GAMBIR")
    with pytest.raises(Exception):
        service.request_transfer(
            RequestTransferCommand(
                complaint_id=cid,
                destination_unit_id="UPPPD-TANAH-ABANG",
                reason="cross-branch not allowed",
                actor_id="agent-1",
                actor_unit_id="UPPPD-GAMBIR",
            )
        )


def test_request_transfer_requires_reason(
    service: InternalComplaintApplicationService,
):
    cid = _create(service, owner_unit_id="UPPPD-GAMBIR")
    with pytest.raises(Exception):
        service.request_transfer(
            RequestTransferCommand(
                complaint_id=cid,
                destination_unit_id="PUSAT",
                reason="   ",
                actor_id="agent-1",
                actor_unit_id="UPPPD-GAMBIR",
            )
        )


def test_request_transfer_then_reject_then_reapply(
    service: InternalComplaintApplicationService,
):
    cid = _create(service, owner_unit_id="UPPPD-GAMBIR")
    dto = service.request_transfer(
        RequestTransferCommand(
            complaint_id=cid,
            destination_unit_id="PUSAT",
            reason="need HQ decision",
            actor_id="agent-1",
            actor_unit_id="UPPPD-GAMBIR",
        )
    )
    assert dto.transfer_request_status == "PENDING"

    dto = service.decide_transfer_request(
        DecideTransferRequestCommand(
            complaint_id=cid,
            decision="REJECT",
            actor_id="sv-1",
            actor_unit_id="UPPPD-GAMBIR",
            reason="not enough detail",
        )
    )
    assert dto.status == "CREATED"
    assert dto.handling_unit_id == "UPPPD-GAMBIR"
    assert dto.transfer_request_status == "REJECTED"

    # Boleh ajukan ulang.
    dto = service.request_transfer(
        RequestTransferCommand(
            complaint_id=cid,
            destination_unit_id="PUSAT",
            reason="added detail",
            actor_id="agent-1",
            actor_unit_id="UPPPD-GAMBIR",
        )
    )
    assert dto.transfer_request_status == "PENDING"

    dto = service.decide_transfer_request(
        DecideTransferRequestCommand(
            complaint_id=cid,
            decision="APPROVE",
            actor_id="sv-1",
            actor_unit_id="UPPPD-GAMBIR",
        )
    )
    assert dto.status == "ASSIGNED"
    assert dto.handling_unit_id == "PUSAT"
    event_types = [e.event_type for e in dto.history]
    assert "TRANSFER_REQUESTED" in event_types
    assert "TRANSFER_REQUEST_REJECTED" in event_types
    assert "TRANSFER_REQUEST_APPROVED" in event_types
    assert "TRANSFER" in event_types


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


_DECIDE_PERMS = frozenset({*_PERMS, "internal:escalate-decide"})


def _dev_settings() -> Settings:
    return Settings(
        environment="development",
        ecmp_auth_mode="dev",
        ecmp_env="local",
        jwt_secret_key="test-secret-key-for-internal-complaints-mode-a",
        jwt_algorithm="HS256",
    )


def _app_client(
    db_session: Session,
    service: InternalComplaintApplicationService,
    principal: Principal,
    *,
    settings_factory: Callable[[], Settings] = _jwt_settings,
) -> TestClient:
    app = create_app()
    app.dependency_overrides[get_current_principal] = lambda: principal
    app.dependency_overrides[get_db_session] = lambda: db_session
    app.dependency_overrides[get_internal_complaint_service] = lambda: service
    app.dependency_overrides[get_settings] = settings_factory
    return TestClient(app)


def test_http_branch_agent_create_assigns_to_pusat(
    db_session: Session, service: InternalComplaintApplicationService
):
    """Cabang create — Handling langsung Pusat (ASSIGNED), tanpa transfer-request."""
    agent_perms = frozenset(p for p in _PERMS if p != "complaints:assign")
    agent = Principal(
        user_id=uuid.uuid4(),
        roles=("AGENT",),
        org_unit_id="UPPPD-GAMBIR",
        permissions=agent_perms,
    )
    with _app_client(db_session, service, agent) as client:
        created = client.post(
            "/api/v1/internal/complaints",
            json={
                "subject": "No dest",
                "description": "create only",
                "category": "OPERATIONAL",
            },
        )
        assert created.status_code == 201, created.text
        data = created.json()["data"]
        assert data["status"] == "ASSIGNED"
        assert data["ownerUnitId"] == "UPPPD-GAMBIR"
        assert data["handlingUnitId"] == "PUSAT"
        assert data["transferRequestStatus"] is None
        cid = data["complaintId"]

        tr = client.post(
            f"/api/v1/internal/complaints/{cid}/transfer",
            json={"destinationUnitId": "PUSAT"},
        )
        assert tr.status_code == 403


def test_http_pusat_agent_create_with_dest_requires_reason(
    db_session: Session, service: InternalComplaintApplicationService
):
    agent_perms = frozenset(p for p in _PERMS if p != "complaints:assign")
    agent = Principal(
        user_id=uuid.uuid4(),
        roles=("AGENT",),
        org_unit_id="PUSAT",
        permissions=agent_perms,
    )
    with _app_client(db_session, service, agent) as client:
        resp = client.post(
            "/api/v1/internal/complaints",
            json={
                "subject": "Escalate on create",
                "description": "to branch",
                "category": "OPERATIONAL",
                "handlingUnitId": "UPPPD-GAMBIR",
            },
        )
        assert resp.status_code == 400, resp.text


def test_http_branch_agent_create_with_dest_assigns_to_pusat(
    db_session: Session, service: InternalComplaintApplicationService
):
    """Checklist: Agent cabang create — ASSIGNED di Pusat, nomor PI-TAB-…-001."""
    agent_perms = frozenset(p for p in _PERMS if p != "complaints:assign")
    agent = Principal(
        user_id=uuid.uuid4(),
        roles=("AGENT",),
        org_unit_id="UPPPD-TANAH-ABANG",
        permissions=agent_perms,
    )
    with _app_client(db_session, service, agent) as client:
        resp = client.post(
            "/api/v1/internal/complaints",
            json={
                "subject": "Escalate on create",
                "description": "to pusat",
                "category": "OPERATIONAL",
                "handlingUnitId": "PUSAT",
            },
        )
        assert resp.status_code == 201, resp.text
        data = resp.json()["data"]
        assert data["status"] == "ASSIGNED"
        assert data["ownerUnitId"] == "UPPPD-TANAH-ABANG"
        assert data["handlingUnitId"] == "PUSAT"
        assert data["transferRequestStatus"] is None
        assert data["complaintNumber"].startswith("PI-TAB-")
        assert data["complaintNumber"].endswith("-001")


def test_http_branch_create_pusat_cro_collapses_to_pusat(
    db_session: Session, service: InternalComplaintApplicationService
):
    agent = Principal(
        user_id=uuid.uuid4(),
        roles=("AGENT",),
        org_unit_id="UPPPD-TANAH-ABANG",
        permissions=_PERMS,
    )
    with _app_client(db_session, service, agent) as client:
        resp = client.post(
            "/api/v1/internal/complaints",
            json={
                "subject": "CRO dest",
                "description": "should land on PUSAT",
                "category": "OPERATIONAL",
                "handlingUnitId": "PUSAT-CRO",
            },
        )
        assert resp.status_code == 201, resp.text
        assert resp.json()["data"]["handlingUnitId"] == "PUSAT"


def test_http_pusat_family_can_receive_and_cabang_cannot(
    db_session: Session, service: InternalComplaintApplicationService
):
    cabang = Principal(
        user_id=uuid.uuid4(),
        roles=("AGENT",),
        org_unit_id="UPPPD-GAMBIR",
        permissions=_PERMS,
    )
    pusat = Principal(
        user_id=uuid.uuid4(),
        roles=("AGENT",),
        org_unit_id="PUSAT",
        permissions=_PERMS,
    )
    admin = Principal(
        user_id=uuid.uuid4(),
        roles=("ADMIN",),
        org_unit_id=None,
        permissions=frozenset({"complaints:read", "complaints:update", "*"}),
    )
    with _app_client(db_session, service, cabang) as client:
        created = client.post(
            "/api/v1/internal/complaints",
            json={
                "subject": "Antrian Pusat",
                "description": "d",
                "category": "OPERATIONAL",
            },
        )
        assert created.status_code == 201, created.text
        cid = created.json()["data"]["complaintId"]
        denied = client.post(f"/api/v1/internal/complaints/{cid}/receive", json={})
        assert denied.status_code == 403, denied.text

    row = db_session.get(InternalComplaintORM, uuid.UUID(cid))
    assert row is not None
    row.handling_unit_id = "PUSAT-CRO"
    db_session.commit()

    with _app_client(db_session, service, pusat) as client:
        received = client.post(
            f"/api/v1/internal/complaints/{cid}/receive", json={}
        )
        assert received.status_code == 200, received.text
        assert received.json()["data"]["status"] == "IN_PROGRESS"

    cid2_holder: dict[str, str] = {}
    with _app_client(db_session, service, cabang) as client:
        created2 = client.post(
            "/api/v1/internal/complaints",
            json={
                "subject": "Admin Terima",
                "description": "d",
                "category": "OPERATIONAL",
            },
        )
        assert created2.status_code == 201, created2.text
        cid2_holder["id"] = created2.json()["data"]["complaintId"]

    with _app_client(db_session, service, admin) as client:
        admin_recv = client.post(
            f"/api/v1/internal/complaints/{cid2_holder['id']}/receive", json={}
        )
        assert admin_recv.status_code == 200, admin_recv.text


def test_http_manager_create_with_dest_transfers_directly(
    db_session: Session, service: InternalComplaintApplicationService
):
    """Checklist: SPV/Manager create + tujuan -> langsung ASSIGNED/transfer."""
    manager = Principal(
        user_id=uuid.uuid4(),
        roles=("MANAGER",),
        org_unit_id="UPPPD-GAMBIR",
        permissions=_PERMS,
    )
    with _app_client(db_session, service, manager) as client:
        resp = client.post(
            "/api/v1/internal/complaints",
            json={
                "subject": "Manager escalates",
                "description": "direct",
                "category": "OPERATIONAL",
                "handlingUnitId": "PUSAT",
            },
        )
        assert resp.status_code == 201, resp.text
        data = resp.json()["data"]
        assert data["status"] == "ASSIGNED"
        assert data["handlingUnitId"] == "PUSAT"
        assert data["transferRequestStatus"] is None


def test_http_admin_create_forbidden(
    db_session: Session, service: InternalComplaintApplicationService
):
    """Admin never creates internal complaints (matches 0074 WP behavior)."""
    admin = Principal(
        user_id=uuid.uuid4(),
        roles=("ADMIN",),
        org_unit_id="PUSAT",
        permissions=frozenset({"complaints:read", "complaints:update", "*"}),
    )
    with _app_client(db_session, service, admin) as client:
        resp = client.post(
            "/api/v1/internal/complaints",
            json={"subject": "x", "description": "y", "category": "OPERATIONAL"},
        )
        assert resp.status_code == 403


def test_http_decide_transfer_request_without_permission_denied(
    db_session: Session, service: InternalComplaintApplicationService
):
    agent_perms = frozenset(p for p in _PERMS if p != "complaints:assign")
    agent = Principal(
        user_id=uuid.uuid4(),
        roles=("AGENT",),
        org_unit_id="PUSAT",
        permissions=agent_perms,
    )
    with _app_client(db_session, service, agent) as client:
        created = client.post(
            "/api/v1/internal/complaints",
            json={
                "subject": "Escalate",
                "description": "d",
                "category": "OPERATIONAL",
                "handlingUnitId": "UPPPD-GAMBIR",
                "requestReason": "Perlu keputusan cabang",
            },
        )
        cid = created.json()["data"]["complaintId"]
        decide = client.post(
            f"/api/v1/internal/complaints/{cid}/transfer-request/decision",
            json={"decision": "APPROVE"},
        )
        assert decide.status_code == 403


def test_http_supervisor_approves_transfer_request_moves_handling(
    db_session: Session, service: InternalComplaintApplicationService
):
    agent_perms = frozenset(p for p in _PERMS if p != "complaints:assign")
    agent = Principal(
        user_id=uuid.uuid4(),
        roles=("AGENT",),
        org_unit_id="PUSAT",
        permissions=agent_perms,
    )
    supervisor = Principal(
        user_id=uuid.uuid4(),
        roles=("SUPERVISOR",),
        org_unit_id="PUSAT",
        permissions=_DECIDE_PERMS,
    )
    with _app_client(db_session, service, agent) as client:
        created = client.post(
            "/api/v1/internal/complaints",
            json={
                "subject": "Escalate",
                "description": "d",
                "category": "OPERATIONAL",
                "handlingUnitId": "UPPPD-GAMBIR",
                "requestReason": "Perlu keputusan cabang",
            },
        )
        cid = created.json()["data"]["complaintId"]

    with _app_client(db_session, service, supervisor) as client:
        decide = client.post(
            f"/api/v1/internal/complaints/{cid}/transfer-request/decision",
            json={"decision": "APPROVE", "reason": "Disetujui"},
        )
        assert decide.status_code == 200, decide.text
        data = decide.json()["data"]
        assert data["status"] == "ASSIGNED"
        assert data["handlingUnitId"] == "UPPPD-GAMBIR"
        assert data["transferRequestStatus"] == "APPROVED"
        event_types = [e["eventType"] for e in data["history"]]
        assert "TRANSFER_REQUESTED" in event_types
        assert "TRANSFER_REQUEST_APPROVED" in event_types
        assert "TRANSFER" in event_types


def test_http_manager_rejects_transfer_request_requires_reason_and_stays_local(
    db_session: Session, service: InternalComplaintApplicationService
):
    agent_perms = frozenset(p for p in _PERMS if p != "complaints:assign")
    agent = Principal(
        user_id=uuid.uuid4(),
        roles=("AGENT",),
        org_unit_id="PUSAT",
        permissions=agent_perms,
    )
    manager = Principal(
        user_id=uuid.uuid4(),
        roles=("MANAGER",),
        org_unit_id="PUSAT",
        permissions=_DECIDE_PERMS,
    )
    with _app_client(db_session, service, agent) as client:
        created = client.post(
            "/api/v1/internal/complaints",
            json={
                "subject": "Escalate",
                "description": "d",
                "category": "OPERATIONAL",
                "handlingUnitId": "UPPPD-GAMBIR",
                "requestReason": "Perlu keputusan cabang",
            },
        )
        cid = created.json()["data"]["complaintId"]

    with _app_client(db_session, service, manager) as client:
        missing_reason = client.post(
            f"/api/v1/internal/complaints/{cid}/transfer-request/decision",
            json={"decision": "REJECT"},
        )
        assert missing_reason.status_code == 400

        rejected = client.post(
            f"/api/v1/internal/complaints/{cid}/transfer-request/decision",
            json={"decision": "REJECT", "reason": "Belum lengkap datanya"},
        )
        assert rejected.status_code == 200, rejected.text
        data = rejected.json()["data"]
        assert data["status"] == "CREATED"
        assert data["handlingUnitId"] == "PUSAT"
        assert data["transferRequestStatus"] == "REJECTED"
        event_types = [e["eventType"] for e in data["history"]]
        assert "TRANSFER_REQUEST_REJECTED" in event_types

    with _app_client(db_session, service, agent) as client:
        reapplied = client.post(
            f"/api/v1/internal/complaints/{cid}/transfer-request",
            json={"destinationUnitId": "UPPPD-GAMBIR", "reason": "Data sudah dilengkapi"},
        )
        assert reapplied.status_code == 200, reapplied.text
        data = reapplied.json()["data"]
        assert data["transferRequestStatus"] == "PENDING"


def test_http_admin_decides_transfer_request_any_unit(
    db_session: Session, service: InternalComplaintApplicationService
):
    """Admin decides regardless of org-unit membership (org-scope bypass)."""
    agent_perms = frozenset(p for p in _PERMS if p != "complaints:assign")
    agent = Principal(
        user_id=uuid.uuid4(),
        roles=("AGENT",),
        org_unit_id="PUSAT",
        permissions=agent_perms,
    )
    admin = Principal(
        user_id=uuid.uuid4(),
        roles=("ADMIN",),
        org_unit_id="PUSAT",
        permissions=frozenset({*_DECIDE_PERMS, "*"} - {"complaints:create"}),
    )
    with _app_client(db_session, service, agent) as client:
        created = client.post(
            "/api/v1/internal/complaints",
            json={
                "subject": "Escalate",
                "description": "d",
                "category": "OPERATIONAL",
                "handlingUnitId": "UPPPD-GAMBIR",
                "requestReason": "Perlu keputusan cabang",
            },
        )
        cid = created.json()["data"]["complaintId"]

    with _app_client(db_session, service, admin) as client:
        decide = client.post(
            f"/api/v1/internal/complaints/{cid}/transfer-request/decision",
            json={"decision": "APPROVE"},
        )
        assert decide.status_code == 200, decide.text
        assert decide.json()["data"]["status"] == "ASSIGNED"


def test_number_sequence_widens_past_999(db_session: Session):
    """Checklist: Agent create seq 1000 — empat digit."""
    repo = SqlAlchemyInternalComplaintRepository(db_session)
    last = ""
    for _ in range(1000):
        last = repo.next_number(owner_unit_id="UPPPD-TANAH-ABANG")
    assert last.startswith("PI-TAB-")
    assert last.endswith("-1000")


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
    assert create.json()["data"]["handlingUnitId"] == "PUSAT"

    # Cabang create already sent Handling to Pusat — skip redundant /transfer.

    # Complete resolve/accept via service with units (HTTP org-scope in jwt
    # mode uses principal.org_unit_id; receive as handling unit requires
    # switching principal — do domain steps via service for dual-unit flow).
    service.start_handling(
        StartHandlingCommand(
            complaint_id=cid, actor_id="pusat-sv", actor_unit_id="PUSAT"
        )
    )
    _propose_resolution(
        service,
        cid,
        actor_id="pusat-sv",
        unit="PUSAT",
        comment="ok",
        summary="done",
        resolution_code="IC-1",
    )
    service.resolve(
        ResolveCommand(
            complaint_id=cid,
            action="ACCEPT",
            comment="Usulan diterima",
            actor_id="owner-sv",
            actor_unit_id="UPPPD-GAMBIR",
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
    assert body["closedBy"] == "other-owner-sv"
    assert "closedByName" in body
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


def test_resolve_related_by_number_case_insensitive(db_session: Session):
    principal = _principal(roles=("SUPERVISOR",))
    _seed_aggregate(db_session, created_by="someone-else")
    ref = resolve_related_aggregate(
        db_session,
        related_complaint_id="cm-rel-001",
        principal=principal,
        actor_unit_id="UPPPD-GAMBIR",
    )
    assert ref is not None
    assert ref.complaint_number == "CM-REL-001"


def test_resolve_related_missing_uses_user_message(db_session: Session):
    principal = _principal(roles=("SUPERVISOR",))
    with pytest.raises(Exception) as exc:
        resolve_related_aggregate(
            db_session,
            related_complaint_id="bukan-nomor",
            principal=principal,
            actor_unit_id="UPPPD-GAMBIR",
        )
    err = exc.value
    assert getattr(err, "code", "") == "RELATED_COMPLAINT_NOT_FOUND"
    assert "Aggregate" not in str(err)
    assert "tidak ditemukan" in str(err).lower()


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
    assert "Aggregate" not in resp.json()["message"]


def test_http_create_related_missing_not_found(
    http_client: tuple[TestClient, Principal],
):
    client, _ = http_client
    resp = client.post(
        "/api/v1/internal/complaints",
        json={
            "subject": "Missing related",
            "description": "should fail",
            "category": "OPERATIONAL",
            "relatedComplaintId": "bukan-nomor",
        },
    )
    assert resp.status_code == 404, resp.text
    body = resp.json()
    assert body["code"] == "RELATED_COMPLAINT_NOT_FOUND"
    assert "Aggregate" not in body["message"]
    assert "tidak ditemukan" in body["message"].lower()


def test_withdraw_before_receive_blocks_start_handling(
    service: InternalComplaintApplicationService,
):
    cid = _create(service, owner_unit_id="UPPPD-GAMBIR")
    service.transfer(
        TransferCommand(
            complaint_id=cid,
            destination_unit_id="PUSAT",
            actor_id="sv-1",
            actor_unit_id="UPPPD-GAMBIR",
            reason="to pusat",
        )
    )
    dto = service.withdraw(
        WithdrawCommand(
            complaint_id=cid,
            actor_id="creator-1",
            reason="Salah buat",
            actor_unit_id="UPPPD-GAMBIR",
        )
    )
    assert dto.status == "WITHDRAWN"
    assert dto.withdraw_reason == "Salah buat"
    with pytest.raises(Exception):
        service.start_handling(
            StartHandlingCommand(
                complaint_id=cid, actor_id="pusat-sv", actor_unit_id="PUSAT"
            )
        )


def test_unilateral_withdraw_hidden_from_pusat_list(
    service: InternalComplaintApplicationService,
):
    cid = _create(service, owner_unit_id="UPPPD-GAMBIR")
    service.transfer(
        TransferCommand(
            complaint_id=cid,
            destination_unit_id="PUSAT",
            actor_id="sv-1",
            actor_unit_id="UPPPD-GAMBIR",
            reason="to pusat",
        )
    )
    service.withdraw(
        WithdrawCommand(
            complaint_id=cid,
            actor_id="creator-1",
            reason="Salah buat",
            actor_unit_id="UPPPD-GAMBIR",
        )
    )
    branch = _principal(roles=("AGENT",), org_unit_id="UPPPD-GAMBIR")
    pusat = _principal(roles=("SUPERVISOR",), org_unit_id="PUSAT")
    items_b, _ = service.list_complaints(branch, org_unit_id="UPPPD-GAMBIR")
    assert any(i.complaint_id == cid for i in items_b)
    items_p, _ = service.list_complaints(pusat, org_unit_id="PUSAT")
    assert not any(i.complaint_id == cid for i in items_p)
    # Lab JWT Mode A often omits orgUnitId; membership still resolves to PUSAT.
    pusat_agent = _principal(roles=("AGENT",), org_unit_id=None)
    items_lab, _ = service.list_complaints(pusat_agent, org_unit_id="PUSAT")
    assert not any(i.complaint_id == cid for i in items_lab)


def test_approved_withdraw_remains_visible_to_pusat(
    service: InternalComplaintApplicationService,
):
    cid = _create(service, owner_unit_id="UPPPD-GAMBIR")
    service.transfer(
        TransferCommand(
            complaint_id=cid,
            destination_unit_id="PUSAT",
            actor_id="sv-1",
            actor_unit_id="UPPPD-GAMBIR",
            reason="to pusat",
        )
    )
    service.start_handling(
        StartHandlingCommand(
            complaint_id=cid, actor_id="pusat-sv", actor_unit_id="PUSAT"
        )
    )
    service.request_withdraw(
        RequestWithdrawCommand(
            complaint_id=cid,
            actor_id="creator-1",
            reason="Sudah selesai di cabang",
            actor_unit_id="UPPPD-GAMBIR",
        )
    )
    service.decide_withdraw_request(
        DecideWithdrawRequestCommand(
            complaint_id=cid,
            decision="APPROVE",
            actor_id="pusat-sv",
            actor_unit_id="PUSAT",
        )
    )
    pusat = _principal(roles=("SUPERVISOR",), org_unit_id="PUSAT")
    items_p, _ = service.list_complaints(pusat, org_unit_id="PUSAT")
    assert any(i.complaint_id == cid for i in items_p)


def test_withdraw_after_return_for_completion_visible_to_pusat(
    service: InternalComplaintApplicationService,
):
    cid = _create(service, owner_unit_id="UPPPD-GAMBIR")
    service.transfer(
        TransferCommand(
            complaint_id=cid,
            destination_unit_id="PUSAT",
            actor_id="sv-1",
            actor_unit_id="UPPPD-GAMBIR",
            reason="to pusat",
        )
    )
    service.return_for_completion(
        ReturnForCompletionCommand(
            complaint_id=cid,
            actor_id="pusat-sv",
            actor_unit_id="PUSAT",
            reason="Scan tidak terbaca",
        )
    )
    service.withdraw(
        WithdrawCommand(
            complaint_id=cid,
            actor_id="creator-1",
            reason="Cabang batal setelah diminta kelengkapan",
            actor_unit_id="UPPPD-GAMBIR",
        )
    )
    dto = service.get(cid)
    assert dto.status == "WITHDRAWN"
    assert dto.pusat_handled_at is not None
    pusat = _principal(roles=("SUPERVISOR",), org_unit_id="PUSAT")
    items_p, _ = service.list_complaints(pusat, org_unit_id="PUSAT")
    assert any(i.complaint_id == cid for i in items_p)


def test_request_withdraw_approve_and_reject(
    service: InternalComplaintApplicationService,
):
    cid = _create(service, owner_unit_id="UPPPD-GAMBIR")
    service.transfer(
        TransferCommand(
            complaint_id=cid,
            destination_unit_id="PUSAT",
            actor_id="sv-1",
            actor_unit_id="UPPPD-GAMBIR",
            reason="to pusat",
        )
    )
    service.start_handling(
        StartHandlingCommand(
            complaint_id=cid, actor_id="pusat-sv", actor_unit_id="PUSAT"
        )
    )
    with pytest.raises(Exception):
        service.withdraw(
            WithdrawCommand(
                complaint_id=cid,
                actor_id="creator-1",
                reason="terlambat",
                actor_unit_id="UPPPD-GAMBIR",
            )
        )
    dto = service.request_withdraw(
        RequestWithdrawCommand(
            complaint_id=cid,
            actor_id="creator-1",
            reason="Sudah selesai di cabang",
            actor_unit_id="UPPPD-GAMBIR",
        )
    )
    assert dto.status == "IN_PROGRESS"
    assert dto.withdraw_request_status == "PENDING"

    dto = service.decide_withdraw_request(
        DecideWithdrawRequestCommand(
            complaint_id=cid,
            decision="REJECT",
            actor_id="pusat-sv",
            actor_unit_id="PUSAT",
            reason="Masih perlu dikerjakan",
        )
    )
    assert dto.status == "IN_PROGRESS"
    assert dto.withdraw_request_status == "REJECTED"

    dto = service.request_withdraw(
        RequestWithdrawCommand(
            complaint_id=cid,
            actor_id="creator-1",
            reason="Data sudah lengkap, mohon dibatalkan",
            actor_unit_id="UPPPD-GAMBIR",
        )
    )
    dto = service.decide_withdraw_request(
        DecideWithdrawRequestCommand(
            complaint_id=cid,
            decision="APPROVE",
            actor_id="pusat-sv",
            actor_unit_id="PUSAT",
        )
    )
    assert dto.status == "WITHDRAWN"
    assert dto.withdraw_request_status == "APPROVED"


def test_http_branch_withdraw_before_receive(
    db_session: Session, service: InternalComplaintApplicationService
):
    agent_perms = frozenset(p for p in _PERMS if p != "complaints:assign")
    agent = Principal(
        user_id=uuid.uuid4(),
        roles=("AGENT",),
        org_unit_id="UPPPD-GAMBIR",
        permissions=agent_perms,
    )
    pusat = Principal(
        user_id=uuid.uuid4(),
        roles=("SUPERVISOR",),
        org_unit_id="PUSAT",
        permissions=_PERMS,
    )
    with _app_client(db_session, service, agent) as client:
        created = client.post(
            "/api/v1/internal/complaints",
            json={
                "subject": "Batal",
                "description": "salah buat",
                "category": "OPERATIONAL",
            },
        )
        cid = created.json()["data"]["complaintId"]
        withdrawn = client.post(
            f"/api/v1/internal/complaints/{cid}/withdraw",
            json={"reason": "Salah kirim"},
        )
        assert withdrawn.status_code == 200, withdrawn.text
        data = withdrawn.json()["data"]
        assert data["status"] == "WITHDRAWN"
        listed = client.get(
            "/api/v1/internal/complaints?status=ASSIGNED"
        )
        ids = [row["complaintId"] for row in listed.json()["data"]]
        assert cid not in ids

    with _app_client(db_session, service, pusat) as client:
        receive = client.post(
            f"/api/v1/internal/complaints/{cid}/receive", json={}
        )
        assert receive.status_code in (400, 409, 404)
        listed = client.get("/api/v1/internal/complaints")
        ids = [row["complaintId"] for row in listed.json()["data"]]
        assert cid not in ids
        hidden = client.get(f"/api/v1/internal/complaints/{cid}")
        assert hidden.status_code == 404


def test_http_withdraw_request_then_pusat_decides(
    db_session: Session, service: InternalComplaintApplicationService
):
    agent_perms = frozenset(p for p in _PERMS if p != "complaints:assign")
    agent = Principal(
        user_id=uuid.uuid4(),
        roles=("AGENT",),
        org_unit_id="UPPPD-GAMBIR",
        permissions=agent_perms,
    )
    pusat = Principal(
        user_id=uuid.uuid4(),
        roles=("SUPERVISOR",),
        org_unit_id="PUSAT",
        permissions=_PERMS,
    )
    with _app_client(db_session, service, agent) as client:
        created = client.post(
            "/api/v1/internal/complaints",
            json={
                "subject": "Minta batal",
                "description": "d",
                "category": "OPERATIONAL",
            },
        )
        cid = created.json()["data"]["complaintId"]

    with _app_client(db_session, service, pusat) as client:
        receive = client.post(
            f"/api/v1/internal/complaints/{cid}/receive", json={}
        )
        assert receive.status_code == 200, receive.text
        assert receive.json()["data"]["status"] == "IN_PROGRESS"

    with _app_client(db_session, service, agent) as client:
        too_late = client.post(
            f"/api/v1/internal/complaints/{cid}/withdraw",
            json={"reason": "terlambat"},
        )
        assert too_late.status_code in (400, 409)
        requested = client.post(
            f"/api/v1/internal/complaints/{cid}/withdraw-request",
            json={"reason": "Sudah selesai di cabang"},
        )
        assert requested.status_code == 200, requested.text
        assert requested.json()["data"]["withdrawRequestStatus"] == "PENDING"
        assert requested.json()["data"]["status"] == "IN_PROGRESS"

    with _app_client(db_session, service, pusat) as client:
        count = client.get(
            "/api/v1/internal/complaints/withdraw-requests/pending-count"
        )
        assert count.status_code == 200
        assert count.json()["data"] >= 1
        decided = client.post(
            f"/api/v1/internal/complaints/{cid}/withdraw-request/decision",
            json={"decision": "APPROVE"},
        )
        assert decided.status_code == 200, decided.text
        assert decided.json()["data"]["status"] == "WITHDRAWN"


def test_return_for_completion_before_and_after_receive(
    service: InternalComplaintApplicationService,
):
    cid = _create(service, owner_unit_id="UPPPD-TANAH-ABANG")
    service.transfer(
        TransferCommand(
            complaint_id=cid,
            destination_unit_id="PUSAT",
            actor_id="sv-tab",
            actor_unit_id="UPPPD-TANAH-ABANG",
            reason="to pusat",
        )
    )
    returned = service.return_for_completion(
        ReturnForCompletionCommand(
            complaint_id=cid,
            actor_id="pusat-agent",
            actor_unit_id="PUSAT",
            reason="Lampiran KTP belum ada",
        )
    )
    assert returned.status == "ASSIGNED"
    assert returned.handling_unit_id == "UPPPD-TANAH-ABANG"
    assert returned.completion_request_status == "PENDING"
    with pytest.raises(Exception):
        service.start_handling(
            StartHandlingCommand(
                complaint_id=cid, actor_id="pusat-sv", actor_unit_id="PUSAT"
            )
        )
    resent = service.resend_to_pusat(
        ResendToPusatCommand(
            complaint_id=cid,
            actor_id="sv-tab",
            actor_unit_id="UPPPD-TANAH-ABANG",
            note="KTP sudah dilampirkan",
        )
    )
    assert resent.handling_unit_id == "PUSAT"
    assert resent.completion_request_status is None
    assert resent.completion_return_reason == "Lampiran KTP belum ada"
    notes = [e.note for e in resent.history if e.event_type == "RESENT_TO_PUSAT"]
    assert "KTP sudah dilampirkan" in notes
    received = service.start_handling(
        StartHandlingCommand(
            complaint_id=cid, actor_id="pusat-sv", actor_unit_id="PUSAT"
        )
    )
    assert received.status == "IN_PROGRESS"
    again = service.return_for_completion(
        ReturnForCompletionCommand(
            complaint_id=cid,
            actor_id="pusat-sv",
            actor_unit_id="PUSAT",
            reason="Formulir halaman 2 kosong",
        )
    )
    assert again.status == "ASSIGNED"
    assert again.handling_unit_id == "UPPPD-TANAH-ABANG"
    assert again.completion_request_status == "PENDING"
    types = {e.event_type for e in again.history}
    assert "RETURNED_FOR_COMPLETION" in types
    assert "RESENT_TO_PUSAT" in types


def test_http_pusat_returns_and_branch_resends(
    db_session: Session, service: InternalComplaintApplicationService
):
    branch = Principal(
        user_id=uuid.uuid4(),
        roles=("AGENT",),
        org_unit_id="UPPPD-GAMBIR",
        permissions=frozenset(p for p in _PERMS if p != "complaints:assign"),
    )
    pusat = Principal(
        user_id=uuid.uuid4(),
        roles=("AGENT",),
        org_unit_id="PUSAT",
        permissions=_PERMS,
    )
    with _app_client(db_session, service, branch) as client:
        created = client.post(
            "/api/v1/internal/complaints",
            json={
                "subject": "Berkas kurang",
                "description": "uji kelengkapan",
                "category": "OPERATIONAL",
            },
        )
        assert created.status_code == 201, created.text
        cid = created.json()["data"]["complaintId"]
        denied = client.post(
            f"/api/v1/internal/complaints/{cid}/return-for-completion",
            json={"reason": "cabang tidak boleh"},
        )
        assert denied.status_code == 403

    with _app_client(db_session, service, pusat) as client:
        returned = client.post(
            f"/api/v1/internal/complaints/{cid}/return-for-completion",
            json={"reason": "Scan bukti bayar tidak terbaca"},
        )
        assert returned.status_code == 200, returned.text
        data = returned.json()["data"]
        assert data["status"] == "ASSIGNED"
        assert data["handlingUnitId"] == "UPPPD-GAMBIR"
        assert data["completionRequestStatus"] == "PENDING"

    with _app_client(db_session, service, branch) as client:
        empty = client.post(
            f"/api/v1/internal/complaints/{cid}/resend-to-pusat",
            json={"note": "  "},
        )
        # RequestValidationError di app ini dipetakan ke 400, bukan 422.
        assert empty.status_code == 400, empty.text
        resent = client.post(
            f"/api/v1/internal/complaints/{cid}/resend-to-pusat",
            json={"note": "Sudah diunggah ulang"},
        )
        assert resent.status_code == 200, resent.text
        data = resent.json()["data"]
        assert data["handlingUnitId"] == "PUSAT"
        assert data["completionRequestStatus"] is None
        assert data["status"] == "ASSIGNED"


def test_mode_a_cross_unit_internal_mutations_denied_404(
    db_session: Session, service: InternalComplaintApplicationService
) -> None:
    """SEC-CMP-005 — Mode A org-scope is a no-op; domain floor must 404.

    Branch B knowing Branch A's complaint id must not GET, transfer, receive,
    close, or request-transfer that ticket.
    """
    from app.core.authorization.org_unit_guard import org_scope_enforcement_enabled

    assert org_scope_enforcement_enabled(_dev_settings()) is False
    cid = _create(service, owner_unit_id="UPPPD-GAMBIR")
    attacker = Principal(
        user_id=uuid.uuid4(),
        roles=("SUPERVISOR",),
        org_unit_id="UPPPD-TANAH-ABANG",
        permissions=_PERMS,
    )
    with _app_client(
        db_session, service, attacker, settings_factory=_dev_settings
    ) as client:
        assert client.get(f"/api/v1/internal/complaints/{cid}").status_code == 404
        export = client.get(f"/api/v1/internal/complaints/{cid}/export")
        assert export.status_code == 404
        transfer = client.post(
            f"/api/v1/internal/complaints/{cid}/transfer",
            json={"destinationUnitId": "PUSAT"},
        )
        assert transfer.status_code == 404
        receive = client.post(
            f"/api/v1/internal/complaints/{cid}/receive", json={}
        )
        assert receive.status_code == 404
        close = client.post(
            f"/api/v1/internal/complaints/{cid}/close", json={}
        )
        assert close.status_code == 404
        request_tr = client.post(
            f"/api/v1/internal/complaints/{cid}/transfer-request",
            json={"destinationUnitId": "PUSAT", "reason": "cross-unit"},
        )
        assert request_tr.status_code == 404
        status = client.patch(
            f"/api/v1/internal/complaints/{cid}/status",
            json={"toStatus": "IN_PROGRESS"},
        )
        assert status.status_code == 404
    still = service.get(cid)
    assert still.owner_unit_id == "UPPPD-GAMBIR"
    assert still.handling_unit_id == "UPPPD-GAMBIR"
    assert still.status == "CREATED"


def test_mode_a_same_unit_internal_transfer_allowed(
    db_session: Session, service: InternalComplaintApplicationService
) -> None:
    """Owning-unit Supervisor may still transfer their own ticket in Mode A."""
    cid = _create(service, owner_unit_id="UPPPD-GAMBIR")
    owner = Principal(
        user_id=uuid.uuid4(),
        roles=("SUPERVISOR",),
        org_unit_id="UPPPD-GAMBIR",
        permissions=_PERMS,
    )
    with _app_client(
        db_session, service, owner, settings_factory=_dev_settings
    ) as client:
        got = client.get(f"/api/v1/internal/complaints/{cid}")
        assert got.status_code == 200, got.text
        transfer = client.post(
            f"/api/v1/internal/complaints/{cid}/transfer",
            json={"destinationUnitId": "PUSAT"},
        )
        assert transfer.status_code == 200, transfer.text
        assert transfer.json()["data"]["handlingUnitId"] == "PUSAT"


def test_http_export_pdf_same_visibility_as_get(
    db_session: Session, service: InternalComplaintApplicationService
) -> None:
    """Cabang pemilik dan Pusat handling boleh unduh; cabang lain 404."""
    cid = _create(service, owner_unit_id="UPPPD-GAMBIR", subject="PDF ticket")
    owner = Principal(
        user_id=uuid.uuid4(),
        roles=("SUPERVISOR",),
        org_unit_id="UPPPD-GAMBIR",
        permissions=_PERMS,
    )
    with _app_client(
        db_session, service, owner, settings_factory=_dev_settings
    ) as client:
        resp = client.get(f"/api/v1/internal/complaints/{cid}/export")
        assert resp.status_code == 200, resp.text
        assert resp.headers["content-type"].startswith("application/pdf")
        assert resp.content.startswith(b"%PDF")
        assert "attachment;" in resp.headers.get("content-disposition", "")
        assert b"PDF ticket" in resp.content
        assert b"Pelanggan" not in resp.content

    service.transfer(
        TransferCommand(
            complaint_id=cid,
            destination_unit_id="PUSAT",
            actor_id="creator-1",
            reason="Kirim ke Pusat",
            actor_unit_id="UPPPD-GAMBIR",
        )
    )
    pusat = Principal(
        user_id=uuid.uuid4(),
        roles=("AGENT",),
        org_unit_id="PUSAT",
        permissions=_PERMS,
    )
    with _app_client(
        db_session, service, pusat, settings_factory=_dev_settings
    ) as client:
        pusat_pdf = client.get(f"/api/v1/internal/complaints/{cid}/export")
        assert pusat_pdf.status_code == 200, pusat_pdf.text
        assert pusat_pdf.content.startswith(b"%PDF")

    outsider = Principal(
        user_id=uuid.uuid4(),
        roles=("SUPERVISOR",),
        org_unit_id="UPPPD-TANAH-ABANG",
        permissions=_PERMS,
    )
    with _app_client(
        db_session, service, outsider, settings_factory=_dev_settings
    ) as client:
        hidden = client.get(f"/api/v1/internal/complaints/{cid}/export")
        assert hidden.status_code == 404
        still = client.get(f"/api/v1/internal/complaints/{cid}")
        assert still.status_code == 404


def test_http_inbox_pending_count_cabang_create_lands_on_pusat(
    db_session: Session, service: InternalComplaintApplicationService
):
    """Cabang create → badge Pusat; Cabang pengirim tidak dihitung."""
    cabang = Principal(
        user_id=uuid.uuid4(),
        roles=("AGENT",),
        org_unit_id="UPPPD-GAMBIR",
        permissions=_PERMS,
    )
    other_cabang = Principal(
        user_id=uuid.uuid4(),
        roles=("AGENT",),
        org_unit_id="UPPPD-TANAH-ABANG",
        permissions=_PERMS,
    )
    pusat = Principal(
        user_id=uuid.uuid4(),
        roles=("SUPERVISOR",),
        org_unit_id="PUSAT",
        permissions=_PERMS,
    )
    with _app_client(db_session, service, cabang) as client:
        created = client.post(
            "/api/v1/internal/complaints",
            json={
                "subject": "Masuk Pusat",
                "description": "d",
                "category": "OPERATIONAL",
            },
        )
        assert created.status_code == 201, created.text
        cid = created.json()["data"]["complaintId"]
        own = client.get("/api/v1/internal/complaints/inbox/pending-count")
        assert own.status_code == 200
        assert own.json()["data"] == 0

    with _app_client(db_session, service, other_cabang) as client:
        other = client.get("/api/v1/internal/complaints/inbox/pending-count")
        assert other.status_code == 200
        assert other.json()["data"] == 0

    inbox, inbox_total = service.list_complaints(
        pusat, page=1, page_size=20, org_unit_id="PUSAT", needs_receive=True
    )
    assert inbox_total == 1
    assert inbox[0].complaint_id == cid

    with _app_client(db_session, service, pusat) as client:
        count = client.get("/api/v1/internal/complaints/inbox/pending-count")
        assert count.status_code == 200
        assert count.json()["data"] == 1
        receive = client.post(f"/api/v1/internal/complaints/{cid}/receive", json={})
        assert receive.status_code == 200, receive.text
        after = client.get("/api/v1/internal/complaints/inbox/pending-count")
        assert after.json()["data"] == 0
    remaining, remaining_total = service.list_complaints(
        pusat, page=1, page_size=20, org_unit_id="PUSAT", needs_receive=True
    )
    assert remaining_total == 0
    assert cid not in [row.complaint_id for row in remaining]


def test_http_inbox_pending_count_return_for_completion_lands_on_cabang(
    db_session: Session, service: InternalComplaintApplicationService
):
    """Pusat kembalikan berkas → badge Cabang pemilik; Pusat tidak dihitung."""
    cabang = Principal(
        user_id=uuid.uuid4(),
        roles=("SUPERVISOR",),
        org_unit_id="UPPPD-GAMBIR",
        permissions=_PERMS,
    )
    pusat = Principal(
        user_id=uuid.uuid4(),
        roles=("SUPERVISOR",),
        org_unit_id="PUSAT",
        permissions=_PERMS,
    )
    with _app_client(db_session, service, cabang) as client:
        created = client.post(
            "/api/v1/internal/complaints",
            json={
                "subject": "Berkas kurang",
                "description": "d",
                "category": "OPERATIONAL",
            },
        )
        cid = created.json()["data"]["complaintId"]

    with _app_client(db_session, service, pusat) as client:
        returned = client.post(
            f"/api/v1/internal/complaints/{cid}/return-for-completion",
            json={"reason": "Lengkapi lampiran pendukung"},
        )
        assert returned.status_code == 200, returned.text
        assert returned.json()["data"]["status"] == "ASSIGNED"
        assert returned.json()["data"]["handlingUnitId"] == "UPPPD-GAMBIR"
        pusat_count = client.get("/api/v1/internal/complaints/inbox/pending-count")
        assert pusat_count.json()["data"] == 0

    with _app_client(db_session, service, cabang) as client:
        cabang_count = client.get("/api/v1/internal/complaints/inbox/pending-count")
        assert cabang_count.status_code == 200
        assert cabang_count.json()["data"] == 1
    items, total = service.list_complaints(
        cabang, page=1, page_size=20, org_unit_id="UPPPD-GAMBIR", needs_receive=True
    )
    assert total == 1
    assert items[0].complaint_id == cid

