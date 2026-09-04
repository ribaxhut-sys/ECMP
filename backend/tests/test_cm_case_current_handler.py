"""Case handler column — who the Case sits with, across the HQ handover.

Escalating to Pusat clears ``handling_claimed_by`` (Pusat must claim), which
left the Tindak lanjut "CRO" column empty for every Case on the HQ path.
``resolve_current_handler`` fills it from the actor columns already stamped on
the parent Complaint. These tests pin the precedence and prove the Case list
carries it end to end.
"""

from __future__ import annotations

import uuid
from collections.abc import Generator

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker
from sqlalchemy.pool import StaticPool

from app.core.authorization.principal import Principal
from app.db.base import Base
from app.modules.cm_batch1.models import CmBatch1ComplaintORM
from app.modules.cm_case.application.current_handler import (
    BRANCH,
    PUSAT,
    ParentHandoff,
    resolve_current_handler,
)
from app.modules.cm_case.application.dto import CreateCaseCommand
from app.modules.cm_case.application.services import (
    CaseApplicationService,
    NoOpSideEffects,
)
from app.modules.cm_case.infrastructure.orm import (
    CmCaseAcceptanceORM,
    CmCaseInboxReceiptORM,
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
    CmCaseInboxReceiptORM.__table__,
]

BRANCH_OFFICER = "branch-cro-1"
PUSAT_OFFICER = "pusat-cro-9"


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


# --- precedence rules -------------------------------------------------------


def test_active_claim_wins_over_the_hq_actors() -> None:
    handler = resolve_current_handler(
        handling_claimed_by=PUSAT_OFFICER,
        created_by=BRANCH_OFFICER,
        escalated_to_pusat=True,
        parent=ParentHandoff(
            intake_disposition="HQ_SCHEDULED",
            hq_destination_set_by="pusat-someone-else",
        ),
    )
    assert (handler.actor_id, handler.scope) == (PUSAT_OFFICER, PUSAT)


def test_branch_claim_stays_branch_scope() -> None:
    handler = resolve_current_handler(
        handling_claimed_by=BRANCH_OFFICER,
        created_by=BRANCH_OFFICER,
        escalated_to_pusat=False,
    )
    assert (handler.actor_id, handler.scope) == (BRANCH_OFFICER, BRANCH)


def test_escalated_without_claim_uses_the_pusat_scheduler() -> None:
    handler = resolve_current_handler(
        handling_claimed_by=None,
        created_by=BRANCH_OFFICER,
        escalated_to_pusat=True,
        parent=ParentHandoff(
            intake_disposition="HQ_SCHEDULED",
            hq_accepted_by="pusat-accepter",
            hq_destination_set_by=PUSAT_OFFICER,
        ),
    )
    assert (handler.actor_id, handler.scope) == (PUSAT_OFFICER, PUSAT)


def test_accepted_without_a_schedule_uses_the_accepting_officer() -> None:
    handler = resolve_current_handler(
        handling_claimed_by=None,
        created_by=BRANCH_OFFICER,
        escalated_to_pusat=True,
        parent=ParentHandoff(
            intake_disposition="ESCALATE_APPROVED",
            hq_accepted_by=PUSAT_OFFICER,
        ),
    )
    assert (handler.actor_id, handler.scope) == (PUSAT_OFFICER, PUSAT)


def test_awaiting_branch_approval_shows_the_proposing_officer() -> None:
    handler = resolve_current_handler(
        handling_claimed_by=None,
        created_by="case-creator",
        escalated_to_pusat=False,
        parent=ParentHandoff(
            intake_disposition="ESCALATE_PENDING_APPROVAL",
            proposed_by=BRANCH_OFFICER,
        ),
    )
    assert (handler.actor_id, handler.scope) == (BRANCH_OFFICER, BRANCH)


def test_returned_to_branch_never_shows_the_pusat_officer() -> None:
    handler = resolve_current_handler(
        handling_claimed_by=None,
        created_by=BRANCH_OFFICER,
        escalated_to_pusat=False,
        parent=ParentHandoff(
            intake_disposition="RETURNED_TO_BRANCH",
            hq_accepted_by=PUSAT_OFFICER,
            hq_destination_set_by=PUSAT_OFFICER,
        ),
    )
    assert (handler.actor_id, handler.scope) == (BRANCH_OFFICER, BRANCH)


def test_falls_back_to_the_case_creator() -> None:
    handler = resolve_current_handler(
        handling_claimed_by=None,
        created_by=BRANCH_OFFICER,
        escalated_to_pusat=False,
    )
    assert (handler.actor_id, handler.scope) == (BRANCH_OFFICER, BRANCH)


def test_no_actor_at_all_stays_empty() -> None:
    handler = resolve_current_handler(
        handling_claimed_by=None,
        created_by=None,
        escalated_to_pusat=True,
        parent=ParentHandoff(intake_disposition="ESCALATE_APPROVED"),
    )
    assert handler.actor_id is None


# --- list path --------------------------------------------------------------


def _seed_complaint(session: Session, **columns: object) -> str:
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
        created_by=BRANCH_OFFICER,
        owning_unit_id="UPPPD-GAMBIR",
        **columns,
    )
    session.add(row)
    session.commit()
    return str(row.id)


def _service(session: Session) -> CaseApplicationService:
    return CaseApplicationService(
        SqlAlchemyCaseRepository(session),
        side_effects=NoOpSideEffects(),
    )


def _admin() -> Principal:
    return Principal(
        user_id=uuid.uuid4(),
        roles=("ADMIN",),
        org_unit_id=None,
        permissions=frozenset({"complaints:create", "complaints:read", "complaints:update"}),
    )


def test_case_list_shows_the_pusat_officer_once_escalated(db_session: Session) -> None:
    complaint_id = _seed_complaint(
        db_session,
        intake_disposition="HQ_SCHEDULED",
        hq_destination_set_by=PUSAT_OFFICER,
    )
    service = _service(db_session)
    created = service.create_case(
        CreateCaseCommand(
            complaint_id=complaint_id,
            case_type="COMPLAINT",
            subject="Case subject",
            description="desc",
            priority="MEDIUM",
            destination_unit_id="UPPPD-GAMBIR",
            actor_id=BRANCH_OFFICER,
        )
    )
    # Escalation clears the claim — exactly the state that emptied the column.
    row = db_session.get(CmCaseORM, uuid.UUID(created.case_id))
    row.escalated_to_pusat = True
    row.handling_claimed_by = None
    db_session.commit()

    items, _ = service.list_cases(_admin(), complaint_id=complaint_id)

    assert len(items) == 1
    assert items[0].handling_claimed_by is None
    assert items[0].current_handler_id == PUSAT_OFFICER
    assert items[0].current_handler_scope == PUSAT


def test_case_list_keeps_the_branch_claimer_when_not_escalated(
    db_session: Session,
) -> None:
    complaint_id = _seed_complaint(db_session)
    service = _service(db_session)
    service.create_case(
        CreateCaseCommand(
            complaint_id=complaint_id,
            case_type="COMPLAINT",
            subject="Case subject",
            description="desc",
            priority="MEDIUM",
            destination_unit_id="UPPPD-GAMBIR",
            actor_id=BRANCH_OFFICER,
        )
    )

    items, _ = service.list_cases(_admin(), complaint_id=complaint_id)

    assert len(items) == 1
    assert items[0].current_handler_id == BRANCH_OFFICER
    assert items[0].current_handler_scope == BRANCH
