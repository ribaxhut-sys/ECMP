"""HqScheduleRepository — SQL path: proposal only surfaces for a live escalation."""

from __future__ import annotations

import uuid
from collections.abc import Generator
from datetime import UTC, date, datetime, timedelta

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker

from app.db.base import Base
from app.integrations.customer import StubCustomerProvider
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
from app.modules.cm_batch1.schemas import (
    CreateComplaintBatch1Request,
    HqAcceptAndScheduleRequest,
    HqCompleteRequest,
    HqReturnRequest,
    IntakeEscalationDecisionRequest,
)
from app.modules.cm_batch1.service import CmBatch1Service
from app.modules.cm_case.infrastructure.orm import CmCaseORM
from app.modules.hq_schedule.models import CmHqHolidayORM
from app.modules.hq_schedule.repository import HqScheduleRepository
from cm_batch1_helpers import confirmed_create

_BATCH1_TABLES = [
    CmBatch1ComplaintORM.__table__,
    CmBatch1IdempotencyORM.__table__,
    CmBatch1ChannelMessageORM.__table__,
    CmBatch1CustomerLockORM.__table__,
    CmBatch1NumberCounterORM.__table__,
    CmBatch1DuplicateDecisionORM.__table__,
    CmBatch1LaterReviewItemORM.__table__,
    CmHqHolidayORM.__table__,
    CmCaseORM.__table__,
]

_TOMORROW = date.today() + timedelta(days=1)


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
def service(db_session: Session) -> CmBatch1Service:
    return CmBatch1Service(
        customer_provider=StubCustomerProvider(),
        guard=EnumerationGuard(max_failures=3, window_seconds=60, block_seconds=30),
        store=CmBatch1Repository(db_session),
    )


def _escalate_body(**overrides: object) -> CreateComplaintBatch1Request:
    fields = {
        "customerId": "CUST-10001",
        "category": "Layanan",
        "channel": "WALK_IN",
        "subject": "Subjek",
        "description": "Cerita\n\n---\nAlasan eskalasi:\nPerlu ditinjau Pusat.",
        "intakeDisposition": "ESCALATE_PENDING_APPROVAL",
    }
    fields.update(overrides)
    return CreateComplaintBatch1Request.model_validate(fields)


def test_returned_to_branch_proposal_not_listed(
    service: CmBatch1Service, db_session: Session
) -> None:
    resp = confirmed_create(
        service,
        _escalate_body(
            proposedArrivalDate=_TOMORROW.isoformat(), proposedArrivalTime="09:00"
        ),
        request_id="hq-repo-req-1",
    )
    service.decide_intake_escalation(
        resp.complaint_id,
        IntakeEscalationDecisionRequest(
            decision="APPROVE",
            note="Disetujui supervisor cabang untuk eskalasi ke Pusat.",
            priority="MEDIUM",
        ),
        actor_id="supervisor-1",
    )
    service.return_from_hq(
        resp.complaint_id,
        HqReturnRequest(
            reasonCode="INCOMPLETE_CHRONOLOGY",
            note="Data pendukung belum lengkap, mohon dilengkapi.",
        ),
        actor_id="hq-scheduler-1",
    )

    # return_from_hq already clears proposed_* in the DB (bug fix above), so
    # the returned complaint drops out of the range query entirely — nothing
    # left to mistake for a pending proposal.
    hq_repo = HqScheduleRepository(db_session)
    rows = hq_repo.list_arrivals_in_range(date_from=_TOMORROW, date_to=_TOMORROW)
    assert rows == []


def test_stale_proposed_columns_ignored_for_non_live_disposition(
    service: CmBatch1Service, db_session: Session
) -> None:
    """Defensive filter: even if proposed_* survives (legacy row, race), a
    non-live disposition must never surface it as a pending proposal."""
    resp = confirmed_create(
        service,
        _escalate_body(
            proposedArrivalDate=_TOMORROW.isoformat(), proposedArrivalTime="09:00"
        ),
        request_id="hq-repo-req-3",
    )
    row = db_session.get(CmBatch1ComplaintORM, uuid.UUID(resp.complaint_id))
    assert row is not None
    row.intake_disposition = "ESCALATE_REJECTED"
    db_session.flush()

    hq_repo = HqScheduleRepository(db_session)
    rows = hq_repo.list_arrivals_in_range(date_from=_TOMORROW, date_to=_TOMORROW)
    assert len(rows) == 1
    assert rows[0].proposed_arrival_date is None
    assert rows[0].proposed_arrival_time is None


def test_pending_approval_proposal_is_listed(
    service: CmBatch1Service, db_session: Session
) -> None:
    resp = confirmed_create(
        service,
        _escalate_body(
            proposedArrivalDate=_TOMORROW.isoformat(), proposedArrivalTime="09:00"
        ),
        request_id="hq-repo-req-2",
    )

    hq_repo = HqScheduleRepository(db_session)
    rows = hq_repo.list_arrivals_in_range(date_from=_TOMORROW, date_to=_TOMORROW)
    assert len(rows) == 1
    row = rows[0]
    assert row.complaint_id == resp.complaint_id
    assert row.proposed_arrival_date == _TOMORROW
    assert row.proposed_arrival_time == "09:00"


def test_case_numbers_joined_by_complaint_id(
    service: CmBatch1Service, db_session: Session
) -> None:
    """CmCaseORM.complaint_id is a plain string column, not an FK — the join
    is manual (HqScheduleRepository._case_numbers_by_complaint). A complaint
    can carry more than one case."""
    resp = confirmed_create(
        service,
        _escalate_body(
            proposedArrivalDate=_TOMORROW.isoformat(), proposedArrivalTime="09:00"
        ),
        request_id="hq-repo-req-4",
    )
    now = datetime.now(UTC)
    db_session.add_all(
        [
            CmCaseORM(
                id=uuid.uuid4(),
                case_number="CASE-2026-000001",
                complaint_id=resp.complaint_id,
                customer_id="cust-1",
                status="OPEN",
                case_type="ESCALATION",
                subject="Eskalasi ke Pusat",
                description="Perlu ditinjau Pusat.",
                priority="MEDIUM",
                owning_unit_id="PUSAT",
                owner_unit_id="UPPPD-A",
                created_by="agent-1",
                created_at=now,
            ),
            CmCaseORM(
                id=uuid.uuid4(),
                case_number="CASE-2026-000002",
                complaint_id=resp.complaint_id,
                customer_id="cust-1",
                status="OPEN",
                case_type="ESCALATION",
                subject="Eskalasi ke Pusat — lanjutan",
                description="Case kedua untuk complaint yang sama.",
                priority="MEDIUM",
                owning_unit_id="PUSAT",
                owner_unit_id="UPPPD-A",
                created_by="agent-1",
                created_at=now,
            ),
        ]
    )
    db_session.flush()

    hq_repo = HqScheduleRepository(db_session)
    rows = hq_repo.list_arrivals_in_range(date_from=_TOMORROW, date_to=_TOMORROW)
    assert len(rows) == 1
    assert rows[0].case_numbers == ("CASE-2026-000001", "CASE-2026-000002")


def test_holiday_crud_round_trip(db_session: Session) -> None:
    repo = HqScheduleRepository(db_session)
    assert repo.get_holiday(_TOMORROW) is None
    assert repo.delete_holiday(_TOMORROW) is False

    created = repo.create_holiday(
        holiday_date=_TOMORROW, label="Cuti bersama", created_by="hq-1"
    )
    assert created.label == "Cuti bersama"
    assert repo.get_holiday(_TOMORROW) is not None
    listed = repo.list_holidays(date_from=_TOMORROW, date_to=_TOMORROW)
    assert [row.label for row in listed] == ["Cuti bersama"]

    assert repo.delete_holiday(_TOMORROW) is True
    assert repo.get_holiday(_TOMORROW) is None
    repo.commit()


def test_completed_hq_visit_stays_listed_on_schedule(
    service: CmBatch1Service, db_session: Session
) -> None:
    resp = confirmed_create(
        service,
        _escalate_body(),
        request_id="hq-repo-complete-1",
    )
    service.decide_intake_escalation(
        resp.complaint_id,
        IntakeEscalationDecisionRequest(
            decision="APPROVE",
            note="Disetujui supervisor cabang untuk eskalasi ke Pusat.",
            priority="MEDIUM",
        ),
        actor_id="supervisor-1",
    )
    service.accept_and_schedule_at_hq(
        resp.complaint_id,
        HqAcceptAndScheduleRequest(
            arrivalDate=_TOMORROW,
            arrivalTime="09:00",
            note="Bawa KTP asli dan dokumen pendukung.",
        ),
        actor_id="hq-scheduler-1",
    )
    hq_repo = HqScheduleRepository(db_session)
    before = hq_repo.list_arrivals_in_range(date_from=_TOMORROW, date_to=_TOMORROW)
    assert len(before) == 1
    assert before[0].hq_arrival_date == _TOMORROW

    completed = service.complete_at_hq(
        resp.complaint_id,
        HqCompleteRequest(
            note="Wajib pajak datang dan pengaduan diselesaikan di Pusat."
        ),
        actor_id="hq-scheduler-1",
    )
    assert completed.status == "CLOSED"
    assert completed.intake_disposition == "HQ_CLOSED"

    after = hq_repo.list_arrivals_in_range(date_from=_TOMORROW, date_to=_TOMORROW)
    assert len(after) == 1
    assert after[0].completed is True
    assert after[0].hq_arrival_date == _TOMORROW
    assert after[0].hq_arrival_time == "09:00"
