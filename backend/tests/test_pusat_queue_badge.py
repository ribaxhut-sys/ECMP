"""Pusat sidebar badge = unopened rows of the needsPusatHandling list.

The badge is a per-user notification: it counts the queue rows this Pusat
user has not opened yet, and lights up again when the branch moves the
complaint after they read it.
"""

from __future__ import annotations

import uuid
from collections.abc import Generator
from datetime import UTC, datetime, timedelta

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker

from app.db.base import Base
from app.modules.cm_batch1.models import (
    CmBatch1ComplaintORM,
    CmBatch1PusatQueueSeenORM,
)
from app.modules.cm_batch1.repository import CmBatch1Repository
from app.modules.cm_case.application.services import (
    CaseApplicationService,
    NoOpSideEffects,
)
from app.modules.cm_case.infrastructure.orm import (
    CmCaseAcceptanceORM,
    CmCaseInboxReceiptORM,
    CmCaseORM,
    CmCaseResolutionORM,
)
from app.modules.cm_case.infrastructure.repository import SqlAlchemyCaseRepository

PUSAT_A = "11111111-1111-1111-1111-111111111111"
PUSAT_B = "22222222-2222-2222-2222-222222222222"


@pytest.fixture()
def db_session() -> Generator[Session, None, None]:
    engine = create_engine("sqlite:///:memory:", future=True)
    Base.metadata.create_all(
        engine,
        tables=[
            CmBatch1ComplaintORM.__table__,
            CmBatch1PusatQueueSeenORM.__table__,
            CmCaseORM.__table__,
            CmCaseResolutionORM.__table__,
            CmCaseAcceptanceORM.__table__,
            CmCaseInboxReceiptORM.__table__,
        ],
    )
    factory = sessionmaker(bind=engine, autoflush=False, autocommit=False, future=True)
    session = factory()
    try:
        yield session
    finally:
        session.close()
        engine.dispose()


def _complaint(
    session: Session,
    *,
    number: str,
    intake_disposition: str | None,
    status: str = "IN_PROGRESS",
    at: datetime | None = None,
    hq_accepted_at: datetime | None = None,
) -> str:
    now = at or datetime.now(UTC)
    row = CmBatch1ComplaintORM(
        id=uuid.uuid4(),
        complaint_number=number,
        status=status,
        customer_id="CUST-1",
        category="GENERAL",
        channel="BRANCH",
        subject=number,
        description="Uraian",
        priority="MEDIUM",
        owning_unit_id="JKT01",
        intake_disposition=intake_disposition,
        hq_accepted_at=hq_accepted_at,
        case_created=False,
        created_by="agent-branch",
        created_at=now,
        updated_at=now,
    )
    session.add(row)
    session.commit()
    return str(row.id)


def _case(
    session: Session,
    *,
    complaint_id: str,
    number: str,
    escalated: bool = True,
    claimed_by: str | None = None,
    status: str = "IN_PROGRESS",
    at: datetime | None = None,
) -> str:
    now = at or datetime.now(UTC)
    row = CmCaseORM(
        id=uuid.uuid4(),
        complaint_id=complaint_id,
        case_number=number,
        customer_id="CUST-1",
        status=status,
        subject=number,
        description="Uraian",
        priority="MEDIUM",
        case_type="GENERAL",
        owning_unit_id="JKT01",
        owner_unit_id="JKT01",
        escalated_to_pusat=escalated,
        handling_claimed_by=claimed_by,
        created_by="agent-branch",
        created_at=now,
        updated_at=now,
    )
    session.add(row)
    session.commit()
    return str(row.id)


def _queue_total(session: Session) -> int:
    _, total = CmBatch1Repository(session).list_complaints(
        page=1, page_size=50, visibility="PUSAT", needs_pusat_handling=True
    )
    return total


def test_badge_never_exceeds_the_list_behind_it(db_session: Session) -> None:
    """Regression: the badge counted Cases the Pusat list would not show."""
    waiting = _complaint(
        db_session, number="CM-0001", intake_disposition="ESCALATE_APPROVED"
    )
    returned = _complaint(
        db_session, number="CM-0002", intake_disposition="RETURNED_TO_BRANCH"
    )
    _case(db_session, complaint_id=returned, number="TAB-2608-0002")
    # Claimed work is somebody's job already — not queue, not badge.
    claimed = _complaint(
        db_session, number="CM-0003", intake_disposition="ESCALATE_APPROVED"
    )
    _case(db_session, complaint_id=claimed, number="TAB-2608-0003", claimed_by="pusat-1")

    repo = CmBatch1Repository(db_session)
    assert repo.count_pusat_queue_unread(PUSAT_A) == _queue_total(db_session)
    assert waiting  # keeps the fixture explicit about what is queued


def test_opening_the_complaint_clears_only_that_users_badge(
    db_session: Session,
) -> None:
    complaint_id = _complaint(
        db_session, number="CM-0010", intake_disposition="ESCALATE_APPROVED"
    )
    repo = CmBatch1Repository(db_session)
    assert repo.count_pusat_queue_unread(PUSAT_A) == 1
    assert repo.count_pusat_queue_unread(PUSAT_B) == 1

    repo.mark_pusat_queue_seen(complaint_id, PUSAT_A)
    db_session.commit()

    assert repo.count_pusat_queue_unread(PUSAT_A) == 0
    assert repo.count_pusat_queue_unread(PUSAT_B) == 1
    # The row itself is still queue work for whoever picks it up.
    assert _queue_total(db_session) == 1


def test_opening_a_case_style_receipt_survives_until_the_branch_moves(
    db_session: Session,
) -> None:
    earlier = datetime.now(UTC) - timedelta(hours=1)
    complaint_id = _complaint(
        db_session,
        number="CM-0020",
        intake_disposition="ESCALATE_APPROVED",
        at=earlier,
    )
    repo = CmBatch1Repository(db_session)
    repo.mark_pusat_queue_seen(complaint_id, PUSAT_A)
    db_session.commit()
    assert repo.count_pusat_queue_unread(PUSAT_A) == 0

    # Branch escalates another Case under the same parent afterwards.
    _case(db_session, complaint_id=complaint_id, number="TAB-2608-0020")

    assert repo.count_pusat_queue_unread(PUSAT_A) == 1
    assert repo.count_pusat_queue_unread(PUSAT_B) == 1


def test_reading_again_after_the_movement_settles_the_badge(
    db_session: Session,
) -> None:
    complaint_id = _complaint(
        db_session,
        number="CM-0030",
        intake_disposition="ESCALATE_APPROVED",
        at=datetime.now(UTC) - timedelta(hours=2),
    )
    _case(
        db_session,
        complaint_id=complaint_id,
        number="TAB-2608-0030",
        at=datetime.now(UTC) - timedelta(hours=1),
    )
    repo = CmBatch1Repository(db_session)
    assert repo.count_pusat_queue_unread(PUSAT_A) == 1

    repo.mark_pusat_queue_seen(complaint_id, PUSAT_A)
    db_session.commit()
    assert repo.count_pusat_queue_unread(PUSAT_A) == 0


def test_hq_return_releases_the_cases_pusat_was_holding(
    db_session: Session,
) -> None:
    """Parent went back to the branch — no Case may stay flagged at Pusat."""
    complaint_id = _complaint(
        db_session, number="CM-0040", intake_disposition="RETURNED_TO_BRANCH"
    )
    case_id = _case(db_session, complaint_id=complaint_id, number="TAB-2608-0040")
    claimed_case = _case(
        db_session,
        complaint_id=complaint_id,
        number="TAB-2608-0041",
        claimed_by="pusat-1",
    )

    service = CaseApplicationService(
        SqlAlchemyCaseRepository(db_session), side_effects=NoOpSideEffects()
    )
    released = service.return_escalations_for_complaint(
        complaint_id=complaint_id,
        return_note="Dikembalikan ke cabang untuk dilengkapi.",
        actor_id=PUSAT_A,
    )

    assert released == 1
    unclaimed = db_session.get(CmCaseORM, uuid.UUID(case_id))
    assert unclaimed is not None
    assert unclaimed.escalated_to_pusat is False
    # Handling goes back to the Case creator, not to nobody.
    assert unclaimed.handling_claimed_by == "agent-branch"
    # Work Pusat already took stays with Pusat (ended via API-521 instead).
    still_pusat = db_session.get(CmCaseORM, uuid.UUID(claimed_case))
    assert still_pusat is not None
    assert still_pusat.escalated_to_pusat is True

    assert CmBatch1Repository(db_session).count_pusat_queue_unread(PUSAT_A) == 0


def test_accepted_or_scheduled_work_is_not_intake_queue(db_session: Session) -> None:
    accepted = _complaint(
        db_session,
        number="CM-0050",
        intake_disposition="ESCALATE_APPROVED",
        hq_accepted_at=datetime.now(UTC),
    )
    _case(db_session, complaint_id=accepted, number="TAB-2608-0050")
    scheduled = _complaint(
        db_session, number="CM-0051", intake_disposition="HQ_SCHEDULED"
    )
    _case(db_session, complaint_id=scheduled, number="TAB-2608-0051")

    assert _queue_total(db_session) == 0
    assert CmBatch1Repository(db_session).count_pusat_queue_unread(PUSAT_A) == 0


def test_unclaimed_escalated_case_on_returned_parent_is_intake(
    db_session: Session,
) -> None:
    """Re-escalated Case after return still needs a Pusat handler."""
    returned = _complaint(
        db_session, number="CM-0060", intake_disposition="RETURNED_TO_BRANCH"
    )
    _case(db_session, complaint_id=returned, number="TAB-2608-0060")

    assert _queue_total(db_session) == 1
    assert CmBatch1Repository(db_session).count_pusat_queue_unread(PUSAT_A) == 1


def test_dec029_escalated_case_without_parent_disposition_is_intake(
    db_session: Session,
) -> None:
    parent = _complaint(db_session, number="CM-0070", intake_disposition=None)
    _case(db_session, complaint_id=parent, number="TAB-2608-0070")

    assert _queue_total(db_session) == 1
    assert CmBatch1Repository(db_session).count_pusat_queue_unread(PUSAT_A) == 1


def _follow_up_unread(session: Session, user_id: str = PUSAT_A) -> int:
    return CmBatch1Repository(session).count_pusat_follow_up_unread(user_id)


def test_intake_and_follow_up_badges_are_mutually_exclusive(
    db_session: Session,
) -> None:
    waiting = _complaint(
        db_session, number="CM-0080", intake_disposition="ESCALATE_APPROVED"
    )
    _case(db_session, complaint_id=waiting, number="TAB-2608-0080")
    assert _queue_total(db_session) == 1
    assert _follow_up_unread(db_session) == 0

    accepted = _complaint(
        db_session,
        number="CM-0081",
        intake_disposition="ESCALATE_APPROVED",
        hq_accepted_at=datetime.now(UTC),
    )
    _case(db_session, complaint_id=accepted, number="TAB-2608-0081")
    assert CmBatch1Repository(db_session).count_pusat_queue_unread(PUSAT_A) == 1
    assert _follow_up_unread(db_session) == 1

    CmBatch1Repository(db_session).mark_pusat_queue_seen(accepted, PUSAT_A)
    db_session.commit()
    assert _follow_up_unread(db_session) == 0
    assert _follow_up_unread(db_session, PUSAT_B) == 1


def test_scheduled_work_lights_follow_up_not_intake(db_session: Session) -> None:
    scheduled = _complaint(
        db_session,
        number="CM-0090",
        intake_disposition="HQ_SCHEDULED",
        hq_accepted_at=datetime.now(UTC),
    )
    _case(db_session, complaint_id=scheduled, number="TAB-2608-0090")
    assert _queue_total(db_session) == 0
    assert _follow_up_unread(db_session) == 1


def test_unread_parent_ids_matches_the_badge_receipt(db_session: Session) -> None:
    waiting = _complaint(
        db_session, number="CM-0100", intake_disposition="ESCALATE_APPROVED"
    )
    accepted = _complaint(
        db_session,
        number="CM-0101",
        intake_disposition="ESCALATE_APPROVED",
        hq_accepted_at=datetime.now(UTC),
    )
    _case(db_session, complaint_id=accepted, number="TAB-2608-0101")
    repo = CmBatch1Repository(db_session)
    ids = [waiting, accepted]
    assert repo.unread_parent_ids(PUSAT_A, ids) == {waiting, accepted}

    repo.mark_pusat_queue_seen(waiting, PUSAT_A)
    db_session.commit()
    assert repo.unread_parent_ids(PUSAT_A, ids) == {accepted}
    assert repo.unread_parent_ids(PUSAT_B, ids) == {waiting, accepted}

