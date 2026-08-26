"""API-537 Case history projection — this Case plus parent HQ-path events."""

from __future__ import annotations

import uuid
from collections.abc import Generator
from datetime import UTC, datetime
from typing import Any

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.ext.compiler import compiles
from sqlalchemy.orm import Session, sessionmaker
from sqlalchemy.pool import StaticPool

from app.core.authorization.authentication import get_current_principal
from app.core.authorization.principal import Principal
from app.core.config import Settings, get_settings
from app.db.base import Base
from app.db.session import get_db_session
from app.main import create_app
from app.modules.cm_batch1.models import CmBatch1ComplaintORM
from app.modules.cm_case.api.router import _history_list_response, get_case_service
from app.modules.cm_case.api.schemas import CaseHistoryEntry
from app.modules.cm_case.application.dto import CaseDTO
from app.modules.cm_case.application.history import (
    _MAX_PAGES,
    _PAGE_SIZE,
    CaseHistoryService,
    _ids_equal,
    belongs_to_case,
    case_event_code,
)
from app.modules.cm_case.application.services import (
    AuditTimelineSideEffects,
    CaseApplicationService,
)
from app.modules.cm_case.infrastructure.orm import (
    CmCaseAcceptanceORM,
    CmCaseInboxReceiptORM,
    CmCaseNumberCounterORM,
    CmCaseORM,
    CmCaseResolutionORM,
)
from app.modules.cm_case.infrastructure.repository import SqlAlchemyCaseRepository
from app.modules.timeline.domain.entity import TimelineEntry
from app.modules.timeline.models import TimelineEntryORM
from app.modules.timeline.repository import TimelineRepository

CASE_ID = "c02969f2-3c3b-47cd-808c-c7d0d4527940"
SIBLING_ID = "aaaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaaaa"
COMPLAINT_ID = "11111111-1111-1111-1111-111111111111"


def _entry(
    event_type: str,
    meta: dict | None = None,
    *,
    actor_id: str | None = None,
    actor_name: str | None = None,
) -> TimelineEntry:
    return TimelineEntry.create(
        aggregate_type="Complaint",
        aggregate_id=uuid.UUID(COMPLAINT_ID),
        event_type=event_type,
        title=event_type,
        metadata=meta or {},
        created_at=datetime(2026, 8, 18, 3, 0, tzinfo=UTC),
        actor_id=actor_id,
        actor_name=actor_name,
    )


def test_belongs_to_case_keeps_tagged_row() -> None:
    row = _entry("CaseCreated", {"caseId": CASE_ID, "caseNumber": "CASE-2026-000001"})
    assert belongs_to_case(row, case_id=CASE_ID, case_number="CASE-2026-000001") is True


def test_belongs_to_case_drops_sibling_and_intake() -> None:
    sibling = _entry("CaseCreated", {"caseId": SIBLING_ID})
    registered = _entry("ComplaintRegistered", {"complaintId": COMPLAINT_ID})
    assert belongs_to_case(sibling, case_id=CASE_ID, case_number="CASE-1") is False
    assert belongs_to_case(registered, case_id=CASE_ID, case_number="CASE-1") is False


def test_belongs_to_case_includes_parent_hq_schedule() -> None:
    scheduled = _entry(
        "HqArrivalScheduled",
        {
            "arrivalDate": "2026-08-20",
            "arrivalTime": "09:30",
            "note": "Bawa dokumen asli",
        },
    )
    accepted = _entry("HqAccepted", {"note": "Diterima Pusat"})
    assert belongs_to_case(scheduled, case_id=CASE_ID, case_number="CASE-1") is True
    assert belongs_to_case(accepted, case_id=CASE_ID, case_number="CASE-1") is True


def test_belongs_to_case_includes_parent_hq_completion() -> None:
    """A Case closed via the HQ path never gets a cm_case_resolutions row —
    the completion note is the only record of the outcome, so it must reach
    the Case's own Catatan/Riwayat like the other parent HQ-path events."""
    completed = _entry(
        "HqCompleted",
        {"note": "Wp sudah kami arahkan ke bidang peraturan"},
    )
    assert belongs_to_case(completed, case_id=CASE_ID, case_number="CASE-1") is True
    assert case_event_code(completed) == "HQ_COMPLETED"


class _FakeTimeline:
    def __init__(self, entries: list[TimelineEntry]) -> None:
        self.entries = entries

    def list_by_aggregate(self, **kwargs):  # noqa: ANN003
        return self.entries, len(self.entries)


def test_list_for_case_exposes_hq_arrival_slot() -> None:
    case = CaseDTO(
        case_id=CASE_ID,
        case_number="CASE-2026-000001",
        complaint_id=COMPLAINT_ID,
        customer_id="cust-1",
        status="IN_PROGRESS",
        case_type="SERVICE",
        subject="Antrian",
        description="Panjang",
        priority="MEDIUM",
        created_at=datetime(2026, 8, 1, tzinfo=UTC),
        created_by="officer-1",
    )
    created = _entry(
        "CaseCreated",
        {"caseId": CASE_ID, "caseNumber": "CASE-2026-000001"},
    )
    scheduled = _entry(
        "HqArrivalScheduled",
        {
            "arrivalDate": "2026-08-20",
            "arrivalTime": "09:30",
            "note": "Bawa dokumen asli",
        },
    )
    service = CaseHistoryService(_FakeTimeline([created, scheduled]))
    items = service.list_for_case(case)
    codes = [row.event_code for row in items]
    assert codes == ["CASE_CREATED", "HQ_ARRIVAL_SCHEDULED"]
    hq = items[1]
    assert hq.arrival_date == "2026-08-20"
    assert hq.arrival_time == "09:30"
    assert hq.note == "Bawa dokumen asli"


def _case(**overrides: object) -> CaseDTO:
    payload: dict[str, object] = {
        "case_id": CASE_ID,
        "case_number": "CASE-2026-000001",
        "complaint_id": COMPLAINT_ID,
        "customer_id": "cust-1",
        "status": "IN_PROGRESS",
        "case_type": "SERVICE",
        "subject": "Antrian",
        "description": "Panjang",
        "priority": "MEDIUM",
        "created_at": datetime(2026, 8, 1, tzinfo=UTC),
        "created_by": "officer-1",
    }
    payload.update(overrides)
    return CaseDTO(**payload)  # type: ignore[arg-type]


def test_belongs_to_case_matches_uuid_and_case_number() -> None:
    compact = CASE_ID.replace("-", "").upper()
    tagged = _entry("CaseCreated", {"caseId": compact})
    assert belongs_to_case(tagged, case_id=CASE_ID, case_number="CASE-1") is True
    by_number = _entry("CaseCreated", {"caseNumber": "CASE-2026-000001"})
    assert belongs_to_case(
        by_number, case_id=CASE_ID, case_number="CASE-2026-000001"
    ) is True
    odd = _entry("CaseCreated", {"caseId": "Not-A-UUID"})
    assert belongs_to_case(odd, case_id="not-a-uuid", case_number="CASE-1") is True
    assert _ids_equal(None, CASE_ID) is False
    assert _ids_equal("  ", CASE_ID) is False


def test_case_event_code_uses_extra_map() -> None:
    row = _entry("CaseHandlingUnitAccepted", {"caseId": CASE_ID})
    assert case_event_code(row) == "CASE_HANDLING_UNIT_ACCEPTED"


def test_list_for_case_invalid_complaint_id_is_empty() -> None:
    service = CaseHistoryService(_FakeTimeline([]))
    assert service.list_for_case(_case(complaint_id="not-a-uuid")) == []


class _PagedTimeline:
    def __init__(self, entries: list[TimelineEntry]) -> None:
        self.entries = entries

    def list_by_aggregate(self, **kwargs):  # noqa: ANN003
        page = int(kwargs["page"])
        size = int(kwargs["page_size"])
        start = (page - 1) * size
        return self.entries[start : start + size], len(self.entries)


def test_list_for_case_walks_additional_timeline_pages() -> None:
    tagged = [
        _entry("CaseCreated", {"caseId": CASE_ID, "caseNumber": "CASE-2026-000001"})
        for _ in range(101)
    ]
    items = CaseHistoryService(_PagedTimeline(tagged)).list_for_case(_case())
    assert len(items) == 101


class _CappedPages:
    """Always returns a full page so the loop hits ``_MAX_PAGES`` then stops."""

    def list_by_aggregate(self, **kwargs):  # noqa: ANN003
        size = int(kwargs["page_size"])
        row = _entry("CaseCreated", {"caseId": CASE_ID})
        return [row] * size, 10_000


def test_list_for_case_stops_at_max_pages() -> None:
    items = CaseHistoryService(_CappedPages()).list_for_case(_case())
    assert len(items) == _MAX_PAGES * _PAGE_SIZE


def test_list_for_case_resolves_actor_name_and_survives_directory_errors() -> None:
    actor_id = str(uuid.uuid4())
    named = _entry("CaseCreated", {"caseId": CASE_ID}, actor_id=actor_id, actor_name="Ayu")
    looked = _entry(
        "CaseWorkStarted",
        {"caseId": CASE_ID},
        actor_id=actor_id,
        actor_name=actor_id,
    )

    class _Dir:
        def display_names(self, wanted: set[str]) -> dict[str, str]:
            return {actor_id: "Budi Santoso"}

    items = CaseHistoryService(
        _FakeTimeline([named, looked]), user_directory=_Dir()
    ).list_for_case(_case())
    assert items[0].actor_name == "Ayu"
    assert items[1].actor_name == "Budi Santoso"

    class _Boom:
        def display_names(self, wanted: set[str]) -> dict[str, str]:
            raise RuntimeError("directory down")

    boom = CaseHistoryService(
        _FakeTimeline([looked]), user_directory=_Boom()
    ).list_for_case(_case())
    assert boom[0].actor_name is None


def test_history_list_response_caps_page_size_at_100() -> None:
    rows = [
        CaseHistoryEntry(
            entryId=str(uuid.uuid4()),
            eventCode="CASE_CREATED",
            eventType="CaseCreated",
            occurredAt=datetime(2026, 8, 18, tzinfo=UTC),
        )
        for _ in range(101)
    ]
    envelope = _history_list_response(rows)
    assert len(envelope.data) == 100
    assert envelope.meta.page == 1
    assert envelope.meta.page_size == 100
    assert envelope.meta.total_items == 101
    empty = _history_list_response([])
    assert empty.data == []
    assert empty.meta.page_size == 1
    assert empty.meta.total_items == 0


# --- API-537 HTTP (AC-07 / AC-08) -------------------------------------------


@compiles(JSONB, "sqlite")
def _compile_jsonb_sqlite(_type, _compiler, **_kw):  # type: ignore[no-untyped-def]
    return "JSON"


_HTTP_TABLES = [
    CmBatch1ComplaintORM.__table__,
    CmCaseORM.__table__,
    CmCaseResolutionORM.__table__,
    CmCaseAcceptanceORM.__table__,
    CmCaseNumberCounterORM.__table__,
    TimelineEntryORM.__table__,
    CmCaseInboxReceiptORM.__table__,
]


@pytest.fixture()
def db_session() -> Generator[Session, None, None]:
    engine = create_engine(
        "sqlite://",
        future=True,
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    Base.metadata.create_all(engine, tables=_HTTP_TABLES)
    factory = sessionmaker(bind=engine, autoflush=False, autocommit=False, future=True)
    session = factory()
    try:
        yield session
    finally:
        session.close()
        engine.dispose()


def _seed_complaint(session: Session, *, owning_unit_id: str | None = "UNIT-API") -> str:
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
        created_by="seed",
        owning_unit_id=owning_unit_id,
    )
    session.add(row)
    session.commit()
    return str(row.id)


def _history_app(
    db_session: Session,
    *,
    principal: Principal | None = None,
    jwt_org_scope: bool = False,
) -> tuple[TestClient, dict[str, Principal]]:
    from unittest.mock import MagicMock

    app = create_app()
    actor = principal or Principal(
        user_id=uuid.uuid4(),
        roles=("SUPERVISOR",),
        org_unit_id="UNIT-API",
        permissions=frozenset(
            {"complaints:create", "complaints:read", "complaints:update"}
        ),
    )
    state: dict[str, Principal] = {"principal": actor}
    svc = CaseApplicationService(
        SqlAlchemyCaseRepository(db_session),
        side_effects=AuditTimelineSideEffects(
            db_session, audit=MagicMock(), timeline=TimelineRepository(db_session)
        ),
    )
    app.dependency_overrides[get_case_service] = lambda: svc
    app.dependency_overrides[get_current_principal] = lambda: state["principal"]
    app.dependency_overrides[get_db_session] = lambda: db_session
    if jwt_org_scope:
        app.dependency_overrides[get_settings] = lambda: Settings(
            environment="development",
            ecmp_auth_mode="jwt",
            ecmp_env="shared",
            oidc_issuer="http://localhost:8180/realms/ecmp",
            oidc_audience="ecmp-api",
            oidc_jwks_url="http://jwks.test/certs",
            jwt_secret_key="test-secret-key-for-cm-case-history",
            jwt_algorithm="HS256",
        )
    client = TestClient(app)
    return client, state


def _create_case(client: TestClient, complaint_id: str, subject: str = "History case") -> dict:
    resp = client.post(
        "/api/v1/cm/cases",
        json={
            "complaintId": complaint_id,
            "caseType": "BILLING",
            "subject": subject,
            "description": "via HTTP",
            "priority": "MEDIUM",
            "destinationUnitId": "UNIT-API",
        },
    )
    assert resp.status_code == 201, resp.text
    return resp.json()["data"]


def test_api_537_history_returns_401_without_auth(db_session: Session) -> None:
    app = create_app()
    app.dependency_overrides[get_db_session] = lambda: db_session
    client = TestClient(app)
    try:
        resp = client.get(f"/api/v1/cm/cases/{uuid.uuid4()}/history")
        assert resp.status_code == 401
        assert resp.json()["code"] == "UNAUTHENTICATED"
    finally:
        app.dependency_overrides.clear()


def test_api_537_history_returns_403_without_permission(db_session: Session) -> None:
    client, _state = _history_app(
        db_session,
        principal=Principal(
            user_id=uuid.uuid4(),
            permissions=frozenset({"complaints:create"}),
        ),
    )
    try:
        resp = client.get(f"/api/v1/cm/cases/{uuid.uuid4()}/history")
        assert resp.status_code == 403
        assert resp.json()["code"] == "FORBIDDEN"
    finally:
        client.app.dependency_overrides.clear()


def test_api_537_history_returns_404_for_unknown_case(db_session: Session) -> None:
    client, _state = _history_app(db_session)
    try:
        resp = client.get(f"/api/v1/cm/cases/{uuid.uuid4()}/history")
        assert resp.status_code == 404
        assert resp.json()["code"] == "NOT_FOUND"
    finally:
        client.app.dependency_overrides.clear()


def test_api_537_history_returns_409_on_membership_mismatch(db_session: Session) -> None:
    client, _state = _history_app(db_session)
    try:
        body = _create_case(client, _seed_complaint(db_session))
        resp = client.get(
            f"/api/v1/cm/cases/{body['caseId']}/history",
            params={"complaintId": str(uuid.uuid4())},
        )
        assert resp.status_code == 409, resp.text
        assert resp.json()["code"] == "CASE_COMPLAINT_MEMBERSHIP_MISMATCH"
    finally:
        client.app.dependency_overrides.clear()


def test_api_537_history_cross_unit_denied(db_session: Session) -> None:
    client, state = _history_app(db_session, jwt_org_scope=True)
    try:
        body = _create_case(client, _seed_complaint(db_session, owning_unit_id="UNIT-API"))
        case_id = body["caseId"]

        state["principal"] = Principal(
            user_id=uuid.uuid4(),
            permissions=frozenset({"complaints:read"}),
            org_unit_id="OU-B",
        )
        denied = client.get(f"/api/v1/cm/cases/{case_id}/history")
        assert denied.status_code == 403
        assert denied.json()["code"] == "ORG_SCOPE_DENIED"

        state["principal"] = Principal(
            user_id=uuid.uuid4(),
            permissions=frozenset({"complaints:read"}),
            org_unit_id="UNIT-API",
        )
        allowed = client.get(f"/api/v1/cm/cases/{case_id}/history")
        assert allowed.status_code == 200, allowed.text
    finally:
        client.app.dependency_overrides.clear()


def test_api_537_history_after_write_is_chronological_and_case_scoped(
    db_session: Session,
) -> None:
    """AC-08: writes appear in time order; sibling Case rows stay out; HQ path in."""
    client, _state = _history_app(db_session)
    try:
        complaint_id = _seed_complaint(db_session)
        first = _create_case(client, complaint_id, subject="Case A")
        sibling = _create_case(client, complaint_id, subject="Case B")
        case_id = first["caseId"]

        started = client.patch(
            f"/api/v1/cm/cases/{case_id}/status",
            json={"toStatus": "IN_PROGRESS"},
        )
        assert started.status_code == 200, started.text

        TimelineRepository(db_session).add(
            TimelineEntry.create(
                aggregate_type="Complaint",
                aggregate_id=uuid.UUID(complaint_id),
                event_type="HqArrivalScheduled",
                title="HQ slot",
                metadata={
                    "arrivalDate": "2026-08-20",
                    "arrivalTime": "09:30",
                    "note": "Bawa dokumen asli",
                },
            )
        )
        db_session.commit()

        resp = client.get(
            f"/api/v1/cm/cases/{case_id}/history",
            params={"complaintId": complaint_id},
        )
        assert resp.status_code == 200, resp.text
        payload = resp.json()
        items: list[dict[str, Any]] = payload["data"]
        meta = payload["meta"]
        assert meta["page"] == 1
        assert meta["pageSize"] == max(1, len(items))
        assert meta["totalItems"] == len(items)
        assert meta["pageSize"] <= 100

        codes = [row["eventCode"] for row in items]
        assert "CASE_CREATED" in codes
        assert "CASE_WORK_STARTED" in codes
        assert "HQ_ARRIVAL_SCHEDULED" in codes
        occurred = [row["occurredAt"] for row in items]
        assert occurred == sorted(occurred)

        sibling_ids = {
            row.get("caseNumber")
            for row in items
            if row.get("caseNumber") and row["caseNumber"] == sibling["caseNumber"]
        }
        assert sibling_ids == set()

        created_idx = codes.index("CASE_CREATED")
        work_idx = codes.index("CASE_WORK_STARTED")
        assert created_idx < work_idx

        hq = next(row for row in items if row["eventCode"] == "HQ_ARRIVAL_SCHEDULED")
        assert hq["arrivalDate"] == "2026-08-20"
        assert hq["arrivalTime"] == "09:30"
        assert hq["note"] == "Bawa dokumen asli"
    finally:
        client.app.dependency_overrides.clear()


def test_get_case_repairs_stale_parent_after_pusat_return(db_session: Session) -> None:
    from app.modules.cm_case.application.services import NoOpSideEffects

    complaint_id = uuid.uuid4()
    case_id = uuid.uuid4()
    db_session.add(
        CmBatch1ComplaintORM(
            id=complaint_id,
            complaint_number="CMTAB-2608-0099",
            customer_id="CUST-10001",
            category="BILLING",
            channel="WALK_IN",
            subject="Seed",
            description="Seed",
            priority="MEDIUM",
            status="IN_PROGRESS",
            case_created=True,
            created_by="officer-1",
            owning_unit_id="TAB",
            intake_disposition="ESCALATE_APPROVED",
        )
    )
    db_session.add(
        CmCaseORM(
            id=case_id,
            case_number="TAB-2608-0099",
            complaint_id=str(complaint_id),
            customer_id="CUST-10001",
            status="IN_PROGRESS",
            case_type="BILLING",
            subject="Returned case",
            description="Need branch work again",
            priority="MEDIUM",
            created_by="officer-1",
            owning_unit_id="TAB",
            owner_unit_id="TAB",
            escalated_to_pusat=False,
        )
    )
    db_session.add(
        TimelineEntryORM(
            aggregate_type="Complaint",
            aggregate_id=complaint_id,
            event_type="CaseEscalationReturned",
            title="Case escalation returned to branch",
            metadata_json={"caseId": str(case_id)},
        )
    )
    db_session.commit()
    service = CaseApplicationService(
        SqlAlchemyCaseRepository(db_session),
        side_effects=NoOpSideEffects(),
    )
    service.get_case(str(case_id))
    parent = db_session.get(CmBatch1ComplaintORM, complaint_id)
    assert parent is not None
    assert parent.intake_disposition == "RETURNED_TO_BRANCH"
