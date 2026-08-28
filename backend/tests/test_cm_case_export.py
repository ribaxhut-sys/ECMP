"""API-539 internal Case snapshot PDF — FR-003 AC-09."""

from __future__ import annotations

import re
import uuid
from collections.abc import Generator
from datetime import UTC, datetime
from unittest.mock import MagicMock

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
from app.modules.cm_case.api.router import get_case_service
from app.modules.cm_case.api.schemas import CaseHistoryEntry
from app.modules.cm_case.application.case_pdf import (
    CASE_PDF_AGENCY,
    CasePdfAttachment,
    CasePdfSnapshot,
    case_pdf_filename,
    case_pdf_masthead,
    format_operator_dt,
    render_case_snapshot_pdf,
    strip_up3d_unit_prefix,
)
from app.modules.cm_case.application.dto import CaseDTO
from app.modules.cm_case.application.pdf_dates import (
    format_pdf_date_and_time,
    rewrite_iso_dates_in_text,
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
from app.modules.timeline.models import TimelineEntryORM
from app.modules.timeline.repository import TimelineRepository


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


def _export_app(
    db_session: Session,
    *,
    principal: Principal | None = None,
    jwt_org_scope: bool = False,
) -> tuple[TestClient, dict[str, Principal]]:
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
            jwt_secret_key="test-secret-key-for-cm-case-export",
            jwt_algorithm="HS256",
        )
    return TestClient(app), state


def _create_case(client: TestClient, complaint_id: str) -> dict:
    resp = client.post(
        "/api/v1/cm/cases",
        json={
            "complaintId": complaint_id,
            "caseType": "BILLING",
            "subject": "Export case",
            "description": "Isi deskripsi untuk PDF",
            "priority": "HIGH",
            "destinationUnitId": "UNIT-API",
        },
    )
    assert resp.status_code == 201, resp.text
    return resp.json()["data"]


def _snapshot_case(**overrides: object) -> CaseDTO:
    payload = dict(
        case_id="c02969f2-3c3b-47cd-808c-c7d0d4527940",
        case_number="UNI-2608-0001",
        complaint_id="11111111-1111-1111-1111-111111111111",
        customer_id="CUST-1",
        status="IN_PROGRESS",
        case_type="SERVICE",
        subject="Antrian panjang",
        description="WP menunggu terlalu lama di loket.",
        priority="HIGH",
        created_at=datetime(2026, 8, 1, 3, 0, tzinfo=UTC),
        created_by="officer-dewi",
    )
    payload.update(overrides)
    return CaseDTO(**payload)  # type: ignore[arg-type]


def test_case_pdf_filename_uses_jakarta_date() -> None:
    when = datetime(2026, 8, 27, 17, 30, tzinfo=UTC)  # 28 Aug 2026 WIB
    assert case_pdf_filename("UNI-2608-0001", when) == "UNI-2608-0001_20260828.pdf"


def test_pdf_dates_are_dmy_with_comma_before_time() -> None:
    assert format_pdf_date_and_time("2026-08-27", "11:00") == "27-08-2026, 11:00"
    assert format_pdf_date_and_time("2026-08-27", None) == "27-08-2026"
    assert (
        rewrite_iso_dates_in_text("Catatan: 2026-08-27 11:00")
        == "Catatan: 27-08-2026, 11:00"
    )
    when = datetime(2026, 8, 27, 4, 0, tzinfo=UTC)  # 11:00 WIB
    assert format_operator_dt(when) == "27-08-2026, 11:00"


def test_case_pdf_masthead_is_created_unit_and_number() -> None:
    assert strip_up3d_unit_prefix("UPPPD Gambir") == "Gambir"
    assert strip_up3d_unit_prefix("UP3D Tanah Abang") == "Tanah Abang"
    assert (
        case_pdf_masthead(unit_name="UPPPD Gambir", case_number="UNI-2608-0001")
        == "Gambir - UNI-2608-0001"
    )
    assert (
        case_pdf_masthead(
            unit_name="UPPPD Gambir",
            case_number="UNI-2608-0001",
            customer_name="Budi Santoso",
        )
        == "Gambir - UNI-2608-0001 ( Budi Santoso )"
    )
    assert case_pdf_masthead(
        unit_name="UPPPD Gambir",
        case_number="UNI-2608-0001",
        customer_name="9e79e188-f126-44ce-9f3a-b08c789e8e33",
    ) == "Gambir - UNI-2608-0001"


def test_render_case_snapshot_pdf_contains_identity_through_history() -> None:
    history = [
        CaseHistoryEntry(
            entryId="e1",
            eventCode="CASE_CREATED",
            eventType="CaseCreated",
            occurredAt=datetime(2026, 8, 1, 3, 0, tzinfo=UTC),
            actorName="Dewi",
            note="Catatan awal",
        )
    ]
    pdf = render_case_snapshot_pdf(
        CasePdfSnapshot(
            case=_snapshot_case(),
            complaint_number="CMP-0001",
            history=history,
            attachments=[
                CasePdfAttachment(
                    original_name="bukti.pdf",
                    mime_type="application/pdf",
                    size_bytes=2048,
                    checksum_sha256="abc123def456",
                    status="ACTIVE",
                    classification="customer_evidence",
                    case_id="c02969f2-3c3b-47cd-808c-c7d0d4527940",
                )
            ],
            exported_by="Dewi Hidayat",
            exported_at=datetime(2026, 8, 28, 1, 0, tzinfo=UTC),
            created_unit_name="UPPPD Gambir",
            customer_label="Budi Santoso",
        )
    )
    assert pdf.startswith(b"%PDF-1.4")
    assert CASE_PDF_AGENCY.encode("ascii") in pdf
    assert b"Gambir - UNI-2608-0001 \\( Budi Santoso \\)" in pdf
    assert b"UPPPD Gambir - UNI-2608-0001" not in pdf
    assert b"Snapshot Case" not in pdf
    agency_tf = re.search(
        rb"/F2 (\d+) Tf ([\d.]+) [\d.]+ Td \(Unit Pelayanan Pemungutan Pajak Daerah\)",
        pdf,
    )
    assert agency_tf is not None
    assert agency_tf.group(1) == b"16"
    assert float(agency_tf.group(2)) > 80
    unit_tf = re.search(
        rb"/F2 (\d+) Tf ([\d.]+) [\d.]+ Td \(Gambir - UNI-2608-0001 \\\( Budi Santoso \\\)\)",
        pdf,
    )
    assert unit_tf is not None
    assert unit_tf.group(1) == b"11"
    assert float(unit_tf.group(2)) > 80
    subject_tf = re.search(
        rb"/F1 (\d+) Tf ([\d.]+) [\d.]+ Td \(Antrian panjang\)",
        pdf,
    )
    assert subject_tf is not None
    assert subject_tf.group(1) == b"10"
    assert float(subject_tf.group(2)) > 80
    assert pdf.count(b"0.6 w") == 2
    assert pdf.find(b"Identitas") < pdf.find(b"0.6 w") < pdf.find(b"Deskripsi")
    assert pdf.find(b"Resolusi") < pdf.rfind(b"0.6 w") < pdf.find(b"Lampiran")
    assert b"UNI-2608-0001" in pdf
    assert b"CMP-0001" in pdf
    assert b"Antrian panjang" in pdf
    assert b"WP menunggu terlalu lama di loket." in pdf
    assert b"Case dibuat" in pdf
    assert b"Catatan awal" in pdf
    assert b"Dewi" in pdf
    assert b"CASE_CREATED" not in pdf
    assert b"bukti.pdf" in pdf
    assert b"INTERNAL" in pdf
    assert b"%%EOF" in pdf


def test_pdf_hides_internal_uuids_for_pelanggan_and_footer() -> None:
    customer_uuid = "9e79e188-f126-44ce-9f3a-b08c789e8e33"
    case_uuid = "05715ca3-bfb7-4db6-bfe4-532483967b2a"
    pdf = render_case_snapshot_pdf(
        CasePdfSnapshot(
            case=_snapshot_case(case_id=case_uuid, customer_id=customer_uuid),
            exported_by="Dewi Hidayat",
            exported_at=datetime(2026, 8, 28, 1, 0, tzinfo=UTC),
        )
    )
    assert customer_uuid.encode("ascii") not in pdf
    assert case_uuid.encode("ascii") not in pdf
    assert b"Pelanggan: -" in pdf
    assert b"UNI-2608-0001" in pdf


def test_render_case_pdf_mirrors_work_card_deskripsi_catatan_resolusi() -> None:
    history = [
        CaseHistoryEntry(
            entryId="e1",
            eventCode="CASE_CREATED",
            eventType="CaseCreated",
            occurredAt=datetime(2026, 8, 1, 3, 0, tzinfo=UTC),
            actorName="Dewi",
            note="Catatan buat case",
        ),
        CaseHistoryEntry(
            entryId="e2",
            eventCode="HQ_ACCEPTED",
            eventType="HqAccepted",
            occurredAt=datetime(2026, 8, 1, 4, 0, tzinfo=UTC),
            actorName="Daffa",
            note="Diterima di Pusat",
        ),
        CaseHistoryEntry(
            entryId="e3",
            eventCode="HQ_COMPLETED",
            eventType="HqCompleted",
            occurredAt=datetime(2026, 8, 2, 5, 0, tzinfo=UTC),
            actorName="Daffa",
            note="WP hadir, selesai di Pusat",
        ),
    ]
    pdf = render_case_snapshot_pdf(
        CasePdfSnapshot(
            case=_snapshot_case(
                subject="BPHTB",
                status="CLOSED",
                description="Keluhan mesin\n\n---\nCatatan:\nSudah dijelaskan",
            ),
            parent_intake_note="Sudah dijelaskan",
            history=history,
            exported_by="Dewi Hidayat",
            exported_at=datetime(2026, 8, 28, 1, 0, tzinfo=UTC),
        )
    )
    assert b"BPHTB" in pdf
    assert b"Keluhan mesin" in pdf
    assert b"Sudah dijelaskan" in pdf
    assert b"Catatan buat case" in pdf
    assert b"Diterima Pusat" in pdf
    assert b"Selesai di Pusat" in pdf
    assert b"Case ini ditutup melalui penyelesaian di Pusat" in pdf
    assert b"bukan alur resolusi cabang" in pdf
    assert b"untuk hasilnya." in pdf
    assert b"Belum ada resolusi. Resolusi akan tampil" not in pdf
    narrative_idx = pdf.find(b"Keluhan mesin")
    catatan_idx = pdf.find(b"Sudah dijelaskan")
    assert 0 <= narrative_idx < catatan_idx


def test_api_539_export_returns_pdf(db_session: Session) -> None:
    client, _state = _export_app(db_session)
    try:
        body = _create_case(client, _seed_complaint(db_session))
        case_id = body["caseId"]
        status_before = body["status"]
        resp = client.get(f"/api/v1/cm/cases/{case_id}/export")
        assert resp.status_code == 200, resp.text
        assert resp.headers["content-type"].startswith("application/pdf")
        assert "attachment;" in resp.headers.get("content-disposition", "")
        assert body["caseNumber"] in resp.headers.get("content-disposition", "")
        assert resp.content.startswith(b"%PDF-1.4")
        assert body["caseNumber"].encode() in resp.content
        assert f"UNIT-API - {body['caseNumber']}".encode() in resp.content
        assert b"Unit Pelayanan Pemungutan Pajak Daerah" in resp.content
        assert b"Snapshot Case" not in resp.content
        viewed = client.get(f"/api/v1/cm/cases/{case_id}")
        assert viewed.status_code == 200
        assert viewed.json()["data"]["status"] == status_before
    finally:
        client.app.dependency_overrides.clear()


def test_api_539_export_returns_401_without_auth(db_session: Session) -> None:
    app = create_app()
    app.dependency_overrides[get_db_session] = lambda: db_session
    client = TestClient(app)
    try:
        resp = client.get(f"/api/v1/cm/cases/{uuid.uuid4()}/export")
        assert resp.status_code == 401
        assert resp.json()["code"] == "UNAUTHENTICATED"
    finally:
        app.dependency_overrides.clear()


def test_api_539_export_returns_403_without_permission(db_session: Session) -> None:
    client, _state = _export_app(
        db_session,
        principal=Principal(
            user_id=uuid.uuid4(),
            permissions=frozenset({"complaints:create"}),
        ),
    )
    try:
        resp = client.get(f"/api/v1/cm/cases/{uuid.uuid4()}/export")
        assert resp.status_code == 403
    finally:
        client.app.dependency_overrides.clear()


def test_api_539_export_returns_409_on_membership_mismatch(db_session: Session) -> None:
    client, _state = _export_app(db_session)
    try:
        body = _create_case(client, _seed_complaint(db_session))
        resp = client.get(
            f"/api/v1/cm/cases/{body['caseId']}/export",
            params={"complaintId": str(uuid.uuid4())},
        )
        assert resp.status_code == 409, resp.text
        assert resp.json()["code"] == "CASE_COMPLAINT_MEMBERSHIP_MISMATCH"
    finally:
        client.app.dependency_overrides.clear()


def test_api_539_export_cross_unit_denied(db_session: Session) -> None:
    client, state = _export_app(db_session, jwt_org_scope=True)
    try:
        body = _create_case(
            client, _seed_complaint(db_session, owning_unit_id="UNIT-API")
        )
        case_id = body["caseId"]

        state["principal"] = Principal(
            user_id=uuid.uuid4(),
            permissions=frozenset({"complaints:read"}),
            org_unit_id="OU-B",
        )
        denied = client.get(f"/api/v1/cm/cases/{case_id}/export")
        assert denied.status_code == 403
        assert denied.json()["code"] == "ORG_SCOPE_DENIED"

        state["principal"] = Principal(
            user_id=uuid.uuid4(),
            permissions=frozenset({"complaints:read"}),
            org_unit_id="UNIT-API",
        )
        allowed = client.get(f"/api/v1/cm/cases/{case_id}/export")
        assert allowed.status_code == 200, allowed.text
        assert allowed.content.startswith(b"%PDF-1.4")
    finally:
        client.app.dependency_overrides.clear()
