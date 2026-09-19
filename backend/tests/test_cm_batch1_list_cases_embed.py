"""API-514 nested Cases: Pusat must not see branch-only siblings."""

from __future__ import annotations

import uuid
from collections.abc import Generator
from datetime import UTC, datetime

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker

from app.db.base import Base
from app.modules.cm_batch1.models import CmBatch1ComplaintORM
from app.modules.cm_batch1.repository import CmBatch1Repository
from app.modules.cm_case.infrastructure.orm import CmCaseORM


@pytest.fixture()
def db_session() -> Generator[Session, None, None]:
    engine = create_engine("sqlite:///:memory:", future=True)
    Base.metadata.create_all(
        engine, tables=[CmBatch1ComplaintORM.__table__, CmCaseORM.__table__]
    )
    factory = sessionmaker(bind=engine, autoflush=False, autocommit=False, future=True)
    session = factory()
    try:
        yield session
    finally:
        session.close()
        engine.dispose()


def test_list_cases_embed_hides_branch_closed_from_pusat(db_session: Session) -> None:
    complaint_id = str(uuid.uuid4())
    now = datetime.now(UTC)
    db_session.add(
        CmBatch1ComplaintORM(
            id=uuid.UUID(complaint_id),
            complaint_number="CMTAB-2608-0099",
            status="IN_PROGRESS",
            customer_id="CUST-1",
            category="GENERAL",
            channel="BRANCH",
            subject="Mixed close + escalate",
            description="Uraian",
            priority="MEDIUM",
            owning_unit_id="JKT01",
            intake_disposition="ESCALATE_APPROVED",
            created_at=now,
            updated_at=now,
        )
    )
    closed = CmCaseORM(
        id=uuid.uuid4(),
        complaint_id=complaint_id,
        case_number="TAB-2608-0001",
        customer_id="CUST-1",
        status="CLOSED",
        subject="Selesai di cabang",
        description="Ditutup cabang",
        priority="MEDIUM",
        case_type="GENERAL",
        owning_unit_id="JKT01",
        owner_unit_id="JKT01",
        escalated_to_pusat=False,
        created_by="agent-branch",
        created_at=now,
        updated_at=now,
    )
    escalated = CmCaseORM(
        id=uuid.uuid4(),
        complaint_id=complaint_id,
        case_number="TAB-2608-0002",
        customer_id="CUST-1",
        status="IN_PROGRESS",
        subject="Eskalasi ke Pusat",
        description="Perlu Pusat",
        priority="HIGH",
        case_type="GENERAL",
        owning_unit_id="JKT01",
        owner_unit_id="JKT01",
        escalated_to_pusat=True,
        created_by="agent-branch",
        created_at=now,
        updated_at=now,
    )
    db_session.add_all([closed, escalated])
    db_session.commit()

    repo = CmBatch1Repository(db_session)
    all_cases = repo.list_cases_for_complaint_ids([complaint_id])
    assert {c["caseNumber"] for c in all_cases[complaint_id]} == {
        "TAB-2608-0001",
        "TAB-2608-0002",
    }

    pusat_cases = repo.list_cases_for_complaint_ids(
        [complaint_id], visibility="PUSAT"
    )
    assert {c["caseNumber"] for c in pusat_cases[complaint_id]} == {
        "TAB-2608-0002",
    }
    assert pusat_cases[complaint_id][0]["escalatedToPusat"] is True


def test_pusat_list_hides_parent_with_only_branch_closed_case(
    db_session: Session,
) -> None:
    """ESCALATE_APPROVED + only a closed non-escalated Case must not appear
    as a Pusat row with a false empty Case column.
    """
    now = datetime.now(UTC)
    orphan_hq = str(uuid.uuid4())
    with_pusat_case = str(uuid.uuid4())
    db_session.add_all(
        [
            CmBatch1ComplaintORM(
                id=uuid.UUID(orphan_hq),
                complaint_number="CMTAB-2608-0100",
                status="CLOSED",
                customer_id="CUST-1",
                category="GENERAL",
                channel="BRANCH",
                subject="Hanya case cabang selesai",
                description="Uraian",
                priority="MEDIUM",
                owning_unit_id="JKT01",
                intake_disposition="ESCALATE_APPROVED",
                case_created=True,
                created_at=now,
                updated_at=now,
            ),
            CmBatch1ComplaintORM(
                id=uuid.UUID(with_pusat_case),
                complaint_number="CMTAB-2608-0101",
                status="IN_PROGRESS",
                customer_id="CUST-1",
                category="GENERAL",
                channel="BRANCH",
                subject="Ada case eskalasi",
                description="Uraian",
                priority="HIGH",
                owning_unit_id="JKT01",
                intake_disposition="ESCALATE_APPROVED",
                case_created=True,
                created_at=now,
                updated_at=now,
            ),
            CmCaseORM(
                id=uuid.uuid4(),
                complaint_id=orphan_hq,
                case_number="TAB-2608-0100",
                customer_id="CUST-1",
                status="CLOSED",
                subject="Selesai cabang",
                description="Ditutup",
                priority="MEDIUM",
                case_type="GENERAL",
                owning_unit_id="JKT01",
                owner_unit_id="JKT01",
                escalated_to_pusat=False,
                created_by="agent-branch",
                created_at=now,
                updated_at=now,
            ),
            CmCaseORM(
                id=uuid.uuid4(),
                complaint_id=with_pusat_case,
                case_number="TAB-2608-0101",
                customer_id="CUST-1",
                status="IN_PROGRESS",
                subject="Ke Pusat",
                description="Eskalasi",
                priority="HIGH",
                case_type="GENERAL",
                owning_unit_id="JKT01",
                owner_unit_id="JKT01",
                escalated_to_pusat=True,
                created_by="agent-branch",
                created_at=now,
                updated_at=now,
            ),
        ]
    )
    db_session.commit()

    repo = CmBatch1Repository(db_session)
    rows, total = repo.list_complaints(page=1, page_size=20, visibility="PUSAT")
    numbers = {r.complaint_number for r in rows}
    assert "CMTAB-2608-0100" not in numbers
    assert "CMTAB-2608-0101" in numbers
    assert total == 1
