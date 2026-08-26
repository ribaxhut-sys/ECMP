"""Cover CmBatch1Repository.list_complaints + work_stats_for_user (SQL path)."""

from __future__ import annotations

import uuid
from collections.abc import Generator

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker

from app.core.authorization.principal import Principal
from app.db.base import Base
from app.integrations.customer import StubCustomerProvider
from app.models import Customer
from app.modules.cm_batch1.enumeration import EnumerationGuard
from app.modules.cm_batch1.models import (
    CmBatch1ChannelMessageORM,
    CmBatch1ComplaintORM,
    CmBatch1CustomerLockORM,
    CmBatch1DuplicateDecisionORM,
    CmBatch1IdempotencyORM,
    CmBatch1LaterReviewItemORM,
    CmBatch1NumberCounterORM,
    CmBatch1PusatQueueSeenORM,
)
from app.modules.cm_batch1.repository import CmBatch1Repository
from app.modules.cm_batch1.schemas import (
    CreateComplaintBatch1Request,
    IntakeEscalationDecisionRequest,
)
from app.modules.cm_batch1.service import CmBatch1Service
from app.modules.cm_case.infrastructure.orm import CmCaseORM
from cm_batch1_helpers import confirmed_create

_BATCH1_TABLES = [
    CmBatch1ComplaintORM.__table__,
    CmBatch1IdempotencyORM.__table__,
    CmBatch1ChannelMessageORM.__table__,
    CmBatch1CustomerLockORM.__table__,
    CmBatch1NumberCounterORM.__table__,
    CmBatch1DuplicateDecisionORM.__table__,
    CmBatch1LaterReviewItemORM.__table__,
    CmBatch1PusatQueueSeenORM.__table__,
    # Pusat visibility + the Case embed both read cm_cases.
    CmCaseORM.__table__,
    Customer.__table__,
]


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


def test_repository_list_visibility_and_filters(service: CmBatch1Service) -> None:
    agent_a = uuid.uuid4()
    agent_b = uuid.uuid4()

    own_a = confirmed_create(
        service,
        CreateComplaintBatch1Request(
            customerId="CUST-10001",
            category="BILLING",
            channel="BRANCH",
            subject="Own A billing",
            description="Keluhan cabang A tanpa eskalasi.",
            recordingUnitId="UPPPD-A",
        ),
        request_id="repo-vis-own-a",
        actor_id=str(agent_a),
    )
    pending = confirmed_create(
        service,
        CreateComplaintBatch1Request(
            customerId="CUST-10001",
            category="BILLING",
            channel="BRANCH",
            subject="Pending esc A",
            description="Keluhan\n\n---\nAlasan eskalasi:\nButuh pusat segera",
            intakeDisposition="ESCALATE_PENDING_APPROVAL",
            recordingUnitId="UPPPD-A",
            duplicateOverrideJustification=(
                "Uji repository visibility — override duplikat untuk seed kedua."
            ),
        ),
        request_id="repo-vis-pending",
        actor_id=str(agent_a),
    )
    approved = confirmed_create(
        service,
        CreateComplaintBatch1Request(
            customerId="CUST-10002",
            category="SERVICE",
            channel="BRANCH",
            subject="Approved esc B",
            description="Keluhan lain\n\n---\nAlasan eskalasi:\nButuh pusat segera",
            intakeDisposition="ESCALATE_PENDING_APPROVAL",
            recordingUnitId="UPPPD-B",
            duplicateOverrideJustification=(
                "Uji repository visibility — override duplikat untuk seed ketiga."
            ),
        ),
        request_id="repo-vis-approved",
        actor_id=str(agent_b),
    )
    service.decide_intake_escalation(
        approved.complaint_id,
        IntakeEscalationDecisionRequest(
            decision="APPROVE",
            note="Catatan supervisor cukup panjang untuk HQ review path.",
            priority="HIGH",
        ),
        actor_id="supervisor-b",
    )

    self_items, self_total = service.list_complaints(
        principal=Principal(
            user_id=agent_a,
            roles=("AGENT",),
            permissions=frozenset({"complaints:read"}),
        ),
    )
    assert self_total == 2
    assert {i.complaint_id for i in self_items} == {
        own_a.complaint_id,
        pending.complaint_id,
    }

    unit_items, unit_total = service.list_complaints(
        principal=Principal(
            user_id=uuid.uuid4(),
            roles=("SUPERVISOR",),
            permissions=frozenset({"complaints:read"}),
            org_unit_id="UPPPD-A",
        ),
        org_unit_id="UPPPD-A",
    )
    assert unit_total == 2
    assert all(i.owning_unit_id == "UPPPD-A" for i in unit_items)

    pusat_items, _ = service.list_complaints(
        principal=Principal(
            user_id=uuid.uuid4(),
            roles=("HO_SCHEDULER",),
            permissions=frozenset({"complaints:read", "escalations:review"}),
        ),
    )
    pusat_ids = {i.complaint_id for i in pusat_items}
    assert approved.complaint_id in pusat_ids
    assert pending.complaint_id not in pusat_ids

    by_creator, creator_total = service.list_complaints(
        principal=Principal(
            user_id=uuid.uuid4(),
            roles=("ADMIN",),
            permissions=frozenset({"*"}),
        ),
        created_by=str(agent_a),
    )
    assert creator_total == 2
    assert all(i.created_by == str(agent_a) for i in by_creator)

    by_kw, kw_total = service.list_complaints(
        principal=Principal(
            user_id=uuid.uuid4(),
            roles=("ADMIN",),
            permissions=frozenset({"*"}),
        ),
        keyword="billing",
    )
    assert kw_total >= 1
    assert any("billing" in (i.subject or "").lower() for i in by_kw)

    by_status, st_total = service.list_complaints(
        principal=Principal(
            user_id=uuid.uuid4(),
            roles=("ADMIN",),
            permissions=frozenset({"*"}),
        ),
        status="REGISTERED",
    )
    assert st_total >= 3
    assert all(i.status == "REGISTERED" for i in by_status)

    by_disp, disp_total = service.list_complaints(
        principal=Principal(
            user_id=uuid.uuid4(),
            roles=("ADMIN",),
            permissions=frozenset({"*"}),
        ),
        intake_disposition="ESCALATED",
    )
    assert disp_total >= 2

    by_unescalated, unescalated_total = service.list_complaints(
        principal=Principal(
            user_id=uuid.uuid4(),
            roles=("ADMIN",),
            permissions=frozenset({"*"}),
        ),
        intake_disposition="UNESCALATED",
        status="REGISTERED",
    )
    assert unescalated_total >= 1
    escalate_family = {
        "ESCALATE_PENDING_APPROVAL",
        "ESCALATE_APPROVED",
        "ESCALATE_REJECTED",
        "ESCALATE_CANCELLED",
        "RETURNED_TO_BRANCH",
        "HQ_SCHEDULED",
    }
    assert all(i.status == "REGISTERED" for i in by_unescalated)
    assert all(
        (i.intake_disposition or "").upper() not in escalate_family
        for i in by_unescalated
    )

    store = service._store
    assert isinstance(store, CmBatch1Repository)
    progressed = store._session.get(
        CmBatch1ComplaintORM, uuid.UUID(own_a.complaint_id)
    )
    assert progressed is not None
    progressed.status = "IN_PROGRESS"
    progressed.case_created = True
    store._session.commit()

    by_open, open_total = service.list_complaints(
        principal=Principal(
            user_id=uuid.uuid4(),
            roles=("ADMIN",),
            permissions=frozenset({"*"}),
        ),
        status="OPEN",
    )
    assert open_total >= 3
    assert all(i.status in {"REGISTERED", "IN_PROGRESS"} for i in by_open)

    by_progress, progress_total = service.list_complaints(
        principal=Principal(
            user_id=uuid.uuid4(),
            roles=("ADMIN",),
            permissions=frozenset({"*"}),
        ),
        status="IN_PROGRESS",
    )
    assert progress_total >= 1
    assert all(i.status == "IN_PROGRESS" for i in by_progress)
    assert any(i.case_created for i in by_progress)

    by_pri, pri_total = service.list_complaints(
        principal=Principal(
            user_id=uuid.uuid4(),
            roles=("ADMIN",),
            permissions=frozenset({"*"}),
        ),
        priority="HIGH",
    )
    assert pri_total >= 1

    by_cat, cat_total = service.list_complaints(
        principal=Principal(
            user_id=uuid.uuid4(),
            roles=("ADMIN",),
            permissions=frozenset({"*"}),
        ),
        category="billing",
    )
    assert cat_total >= 1

    by_decided, decided_total = service.list_complaints(
        principal=Principal(
            user_id=uuid.uuid4(),
            roles=("ADMIN",),
            permissions=frozenset({"*"}),
        ),
        decided_by="supervisor-b",
    )
    assert decided_total >= 1

    empty_self, empty_total = service.list_complaints(
        principal=Principal(
            user_id=uuid.uuid4(),
            roles=("AGENT",),
            permissions=frozenset({"complaints:read"}),
        ),
    )
    assert empty_total == 0
    assert empty_self == []

    # Direct store edge paths (empty actor / unit / unknown visibility / exact disp).
    repo = service._store  # noqa: SLF001 — intentional SQL-path coverage
    assert isinstance(repo, CmBatch1Repository)
    assert repo.list_complaints(visibility="SELF", actor_id="")[1] == 0
    assert repo.list_complaints(visibility="UNIT", org_unit_id="")[1] == 0
    assert repo.list_complaints(visibility="NOPE")[1] == 0
    exact_disp, exact_total = repo.list_complaints(
        visibility="ALL",
        intake_disposition="ESCALATE_APPROVED",
    )
    assert exact_total >= 1
    assert all(r.intake_disposition == "ESCALATE_APPROVED" for r in exact_disp)


def test_repository_work_stats_for_user(service: CmBatch1Service) -> None:
    approved = confirmed_create(
        service,
        CreateComplaintBatch1Request(
            customerId="CUST-10001",
            category="BILLING",
            channel="BRANCH",
            subject="Escalate to be approved repo",
            description="Keluhan\n\n---\nAlasan eskalasi:\nButuh pusat",
            intakeDisposition="ESCALATE_PENDING_APPROVAL",
            recordingUnitId="UPPPD-A",
        ),
        request_id="repo-stats-approved",
        actor_id="agent-repo-1",
    )
    rejected = confirmed_create(
        service,
        CreateComplaintBatch1Request(
            customerId="CUST-10002",
            category="BILLING",
            channel="BRANCH",
            subject="Escalate to be rejected repo",
            description="Keluhan\n\n---\nAlasan eskalasi:\nButuh pusat",
            intakeDisposition="ESCALATE_PENDING_APPROVAL",
            recordingUnitId="UPPPD-A",
            duplicateOverrideJustification=(
                "Uji work_stats repository — seed kedua pelanggan berbeda."
            ),
        ),
        request_id="repo-stats-rejected",
        actor_id="agent-repo-1",
    )
    service.decide_intake_escalation(
        approved.complaint_id,
        IntakeEscalationDecisionRequest(
            decision="APPROVE",
            note="Disetujui: lanjut ke Pusat untuk konfigurasi parameter terminal.",
            priority="HIGH",
        ),
        actor_id="supervisor-repo-1",
    )
    service.decide_intake_escalation(
        rejected.complaint_id,
        IntakeEscalationDecisionRequest(
            decision="REJECT",
            note="Ditolak: kurang bukti pendukung untuk diteruskan ke Pusat.",
        ),
        actor_id="supervisor-repo-1",
    )

    agent_stats = service.work_stats_for_user("agent-repo-1")
    assert agent_stats.created_count == 2
    assert agent_stats.escalation_requested_count == 2

    supervisor_stats = service.work_stats_for_user("supervisor-repo-1")
    assert supervisor_stats.escalation_approved_count == 1
    assert supervisor_stats.escalation_rejected_count == 1

    assert service.work_stats_for_user("").created_count == 0
    assert service.work_stats_for_user("nobody").created_count == 0


def test_repository_later_review_aging_and_hq_mutations(
    service: CmBatch1Service, db_session: Session
) -> None:
    from datetime import UTC, date, datetime, timedelta

    created = confirmed_create(
        service,
        CreateComplaintBatch1Request(
            customerId="CUST-10001",
            category="BILLING",
            channel="BRANCH",
            subject="HQ mutation seed",
            description=(
                "Keluhan untuk jalur repository HQ/aging.\n\n"
                "---\nAlasan eskalasi:\nButuh pusat segera"
            ),
            recordingUnitId="UPPPD-A",
            intakeDisposition="ESCALATE_PENDING_APPROVAL",
        ),
        request_id="repo-hq-seed",
        actor_id="agent-hq",
    )
    repo = CmBatch1Repository(db_session)

    lr_id = repo.create_later_review_work_item(
        customer_id="CUST-10001",
        reason="attachment_bind_failed",
        complaint_id=created.complaint_id,
    )
    assert lr_id.startswith("LR-")
    open_items = repo.list_later_review_items(status="OPEN")
    assert any(i.work_item_id == lr_id for i in open_items)
    assert repo.list_later_review_items(status="ALL")
    assert repo.close_later_review_items(complaint_id="") == 0
    assert (
        repo.close_later_review_items(
            complaint_id=created.complaint_id, reason="attachment_bind_failed"
        )
        == 1
    )

    aged = repo.list_aging_without_case(
        older_than=datetime.now(UTC) + timedelta(days=1), limit=10
    )
    assert any(c.complaint_id == created.complaint_id for c in aged)

    assert repo.update_intake_disposition("not-a-uuid", intake_disposition="X") is None
    assert (
        repo.update_intake_disposition(str(uuid.uuid4()), intake_disposition="X")
        is None
    )
    updated = repo.update_intake_disposition(
        created.complaint_id,
        intake_disposition="ESCALATE_APPROVED",
        description="Updated narrative for HQ",
        priority="high",
        decided_by="supervisor-hq",
    )
    assert updated is not None
    assert updated.intake_disposition == "ESCALATE_APPROVED"
    assert updated.priority == "HIGH"
    assert updated.decided_by == "supervisor-hq"

    assert repo.accept_at_hq("bad", hq_accepted_at=datetime.now(UTC)) is None
    assert (
        repo.accept_at_hq(str(uuid.uuid4()), hq_accepted_at=datetime.now(UTC))
        is None
    )
    accepted = repo.accept_at_hq(
        created.complaint_id,
        hq_accepted_at=datetime.now(UTC),
        description="Accepted at HQ",
        intake_disposition="ESCALATE_APPROVED",
    )
    assert accepted is not None
    assert accepted.hq_accepted_at is not None

    assert (
        repo.schedule_hq_arrival(
            "bad", arrival_date=date(2026, 8, 10), arrival_time="09:00"
        )
        is None
    )
    assert (
        repo.schedule_hq_arrival(
            str(uuid.uuid4()),
            arrival_date=date(2026, 8, 10),
            arrival_time="09:00",
        )
        is None
    )
    scheduled = repo.schedule_hq_arrival(
        created.complaint_id,
        arrival_date=date(2026, 8, 10),
        arrival_time="09:00",
        description="Scheduled",
        intake_disposition="HQ_SCHEDULED",
    )
    assert scheduled is not None
    assert scheduled.hq_arrival_date == date(2026, 8, 10)
    assert scheduled.hq_arrival_time == "09:00"

    assert (
        repo.accept_and_schedule_at_hq(
            "bad",
            hq_accepted_at=datetime.now(UTC),
            arrival_date=date(2026, 8, 11),
            arrival_time="10:00",
            description="combo",
        )
        is None
    )
    assert (
        repo.accept_and_schedule_at_hq(
            str(uuid.uuid4()),
            hq_accepted_at=datetime.now(UTC),
            arrival_date=date(2026, 8, 11),
            arrival_time="10:00",
            description="combo",
        )
        is None
    )
    combo = repo.accept_and_schedule_at_hq(
        created.complaint_id,
        hq_accepted_at=datetime.now(UTC),
        arrival_date=date(2026, 8, 11),
        arrival_time="10:00",
        description="Accept and schedule narrative",
    )
    assert combo is not None
    assert combo.intake_disposition == "HQ_SCHEDULED"
    assert combo.hq_arrival_time == "10:00"
    repo.commit()


def test_list_complaints_keyword_matches_local_customer_name(
    service: CmBatch1Service, db_session: Session
) -> None:
    """API-514 keyword matches WP name via local cache (ADR-002), including CLOSED."""
    taxpayer = Customer(
        id=uuid.uuid4(),
        external_customer_id="CUST-10001",
        full_name="Siti Rahayu Unik",
    )
    db_session.add(taxpayer)
    db_session.commit()

    named = confirmed_create(
        service,
        CreateComplaintBatch1Request(
            customerId="CUST-10001",
            category="BILLING",
            channel="BRANCH",
            subject="Closed billing for named WP",
            description="Keluhan ditutup untuk uji cari nama.",
            recordingUnitId="UPPPD-A",
        ),
        request_id="repo-kw-name-siti",
        actor_id=str(uuid.uuid4()),
    )
    other = confirmed_create(
        service,
        CreateComplaintBatch1Request(
            customerId="CUST-10002",
            category="BILLING",
            channel="BRANCH",
            subject="Closed billing other WP",
            description="Keluhan ditutup milik WP lain.",
            recordingUnitId="UPPPD-A",
        ),
        request_id="repo-kw-name-other",
        actor_id=str(uuid.uuid4()),
    )
    for cid in (named.complaint_id, other.complaint_id):
        row = db_session.get(CmBatch1ComplaintORM, uuid.UUID(cid))
        assert row is not None
        row.status = "CLOSED"
    db_session.commit()

    admin = Principal(
        user_id=uuid.uuid4(),
        roles=("ADMIN",),
        permissions=frozenset({"*"}),
    )
    hits, total = service.list_complaints(
        principal=admin,
        keyword="Siti Rahayu",
        status="CLOSED",
    )
    assert total == 1
    assert hits[0].complaint_id == named.complaint_id

    miss, miss_total = service.list_complaints(
        principal=admin,
        keyword="zzznomatch999",
        status="CLOSED",
    )
    assert miss_total == 0
    assert miss == []
