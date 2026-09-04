"""API-553 Pengaduan Internal list report PDF — filters, renderer, endpoint."""

from __future__ import annotations

import uuid
from collections.abc import Generator
from datetime import UTC, datetime

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine, event
from sqlalchemy.orm import Session, sessionmaker
from sqlalchemy.pool import StaticPool

from app.core.authorization.authentication import get_current_principal
from app.core.authorization.principal import Principal
from app.core.config import Settings, get_settings
from app.db.base import Base
from app.db.session import get_db_session
from app.main import create_app
from app.modules.cm_batch1.models import CmBatch1ComplaintORM
from app.modules.internal_complaint.api.router import get_internal_complaint_service
from app.modules.internal_complaint.application.dto import (
    CreateInternalComplaintCommand,
    InternalComplaintSummaryDTO,
)
from app.modules.internal_complaint.application.report_pdf import (
    InternalReportFilters,
    InternalReportSnapshot,
    internal_report_pdf_filename,
    render_internal_report_pdf,
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


def _principal(org_unit_id: str | None = "UPPPD-GAMBIR") -> Principal:
    return Principal(
        user_id=uuid.uuid4(),
        roles=("SUPERVISOR",),
        org_unit_id=org_unit_id,
        permissions=_PERMS,
    )


def _create(
    service: InternalComplaintApplicationService,
    *,
    subject: str = "Antrian panjang",
    category: str = "OPERATIONAL",
    priority: str = "MEDIUM",
    owner_unit_id: str = "UPPPD-GAMBIR",
) -> str:
    dto = service.create(
        CreateInternalComplaintCommand(
            subject=subject,
            description="Deskripsi",
            category=category,
            priority=priority,
            actor_id="creator-1",
            owner_unit_id=owner_unit_id,
            actor_unit_id=owner_unit_id,
        )
    )
    return dto.complaint_id


def _set_created_at(session: Session, complaint_id: str, when: datetime) -> None:
    row = session.get(InternalComplaintORM, uuid.UUID(complaint_id))
    assert row is not None
    row.created_at = when
    session.flush()


def _summary(**overrides: object) -> InternalComplaintSummaryDTO:
    base = InternalComplaintSummaryDTO(
        complaint_id="11111111-1111-4111-8111-111111111111",
        complaint_number="PI-GAM-2609-001",
        status="IN_PROGRESS",
        subject="Antrian cabang panjang",
        category="OPERATIONAL",
        priority="HIGH",
        owner_unit_id="UPPPD-GAMBIR",
        handling_unit_id="PUSAT",
        created_at=datetime(2026, 9, 1, 2, 0, tzinfo=UTC),
        created_by="creator-1",
    )
    for key, value in overrides.items():
        setattr(base, key, value)
    return base


# --------------------------------------------------------------------------
# Renderer
# --------------------------------------------------------------------------


def test_report_filename_uses_the_jakarta_calendar_day():
    assert (
        internal_report_pdf_filename(datetime(2026, 9, 2, 17, 0, tzinfo=UTC))
        == "laporan-pengaduan-internal_20260903.pdf"
    )


def test_report_pdf_carries_criteria_breakdown_and_rows():
    pdf = render_internal_report_pdf(
        InternalReportSnapshot(
            rows=[_summary(), _summary(status="CLOSED", complaint_number="PI-GAM-2609-002")],
            total_matched=2,
            filters=InternalReportFilters(
                status=None,
                category="OPERATIONAL",
                priority=None,
                date_from="2026-09-01",
                date_to="2026-09-30",
                query=None,
            ),
            exported_by="Supervisor Gambir",
            exported_at=datetime(2026, 9, 2, 3, 0, tzinfo=UTC),
        )
    )
    assert pdf.startswith(b"%PDF-1.4")
    assert b"Laporan Pengaduan Internal" in pdf
    assert b"2026-09-01 s.d. 2026-09-30" in pdf
    assert b"Operasional" in pdf
    assert b"Distribusi Status" in pdf
    assert b"PI-GAM-2609-001" in pdf
    assert b"PI-GAM-2609-002" in pdf
    assert b"Supervisor Gambir" in pdf


def test_report_pdf_says_out_loud_when_the_cap_trimmed_the_tail():
    pdf = render_internal_report_pdf(
        InternalReportSnapshot(
            rows=[_summary()],
            total_matched=900,
            exported_by="Operator",
            exported_at=datetime(2026, 9, 2, 3, 0, tzinfo=UTC),
        )
    )
    assert b"900" in pdf
    assert b"Persempit filter" in pdf


def test_report_pdf_renders_an_empty_result_without_a_table():
    pdf = render_internal_report_pdf(
        InternalReportSnapshot(
            rows=[],
            total_matched=0,
            exported_at=datetime(2026, 9, 2, 3, 0, tzinfo=UTC),
        )
    )
    assert pdf.startswith(b"%PDF-1.4")
    assert b"Tidak ada pengaduan internal yang sesuai kriteria." in pdf


# --------------------------------------------------------------------------
# Service / repository filters
# --------------------------------------------------------------------------


def test_export_summaries_filters_by_category_and_priority(
    service: InternalComplaintApplicationService,
):
    _create(service, category="OPERATIONAL", priority="LOW")
    _create(service, category="SYSTEM", priority="HIGH")
    principal = _principal()

    rows, total = service.export_summaries(
        principal, org_unit_id="UPPPD-GAMBIR", category="SYSTEM"
    )
    assert [r.category for r in rows] == ["SYSTEM"]
    assert total == 1

    rows, _ = service.export_summaries(
        principal, org_unit_id="UPPPD-GAMBIR", priority="LOW"
    )
    assert [r.priority for r in rows] == ["LOW"]


def test_export_summaries_filters_by_period_and_search(
    service: InternalComplaintApplicationService, db_session: Session
):
    old_id = _create(service, subject="Keluhan lama")
    new_id = _create(service, subject="Keluhan baru")
    _set_created_at(db_session, old_id, datetime(2026, 1, 15, 3, 0, tzinfo=UTC))
    _set_created_at(db_session, new_id, datetime(2026, 3, 15, 3, 0, tzinfo=UTC))
    principal = _principal()

    rows, _ = service.export_summaries(
        principal,
        org_unit_id="UPPPD-GAMBIR",
        date_from=datetime(2026, 3, 1, tzinfo=UTC),
    )
    assert [r.subject for r in rows] == ["Keluhan baru"]

    rows, _ = service.export_summaries(
        principal,
        org_unit_id="UPPPD-GAMBIR",
        date_to=datetime(2026, 2, 1, tzinfo=UTC),
    )
    assert [r.subject for r in rows] == ["Keluhan lama"]

    rows, _ = service.export_summaries(
        principal, org_unit_id="UPPPD-GAMBIR", query="lama"
    )
    assert [r.subject for r in rows] == ["Keluhan lama"]


def test_export_summaries_keeps_the_caller_visibility(
    service: InternalComplaintApplicationService,
):
    _create(service, owner_unit_id="UPPPD-GAMBIR")
    _create(service, owner_unit_id="UPPPD-TANAH-ABANG")

    rows, total = service.export_summaries(
        _principal("UPPPD-GAMBIR"), org_unit_id="UPPPD-GAMBIR"
    )
    assert {r.owner_unit_id for r in rows} == {"UPPPD-GAMBIR"}
    assert total == 1


# --------------------------------------------------------------------------
# Endpoint
# --------------------------------------------------------------------------


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
) -> Generator[TestClient, None, None]:
    app = create_app()
    principal = _principal()

    app.dependency_overrides[get_current_principal] = lambda: principal
    app.dependency_overrides[get_db_session] = lambda: db_session
    app.dependency_overrides[get_internal_complaint_service] = lambda: service
    app.dependency_overrides[get_settings] = _jwt_settings

    with TestClient(app) as client:
        yield client

    app.dependency_overrides.clear()


def test_export_endpoint_returns_a_pdf_attachment(
    http_client: TestClient, service: InternalComplaintApplicationService
):
    _create(service, subject="Antrian panjang")
    resp = http_client.get("/api/v1/internal/complaints/export")
    assert resp.status_code == 200, resp.text
    assert resp.headers["content-type"] == "application/pdf"
    assert "laporan-pengaduan-internal_" in resp.headers["content-disposition"]
    assert resp.headers["cache-control"] == "no-store"
    assert resp.content.startswith(b"%PDF-1.4")


def test_export_endpoint_is_not_shadowed_by_the_detail_route(
    http_client: TestClient, service: InternalComplaintApplicationService
):
    """`/export` must not be read as a complaint id by `/{complaint_id}`."""
    _create(service)
    resp = http_client.get("/api/v1/internal/complaints/export")
    assert resp.status_code == 200, resp.text
    assert resp.headers["content-type"] == "application/pdf"


def test_export_endpoint_honours_the_status_filter(
    http_client: TestClient, service: InternalComplaintApplicationService
):
    _create(service, subject="Masih dibuat")
    resp = http_client.get(
        "/api/v1/internal/complaints/export", params={"status": "CLOSED"}
    )
    assert resp.status_code == 200, resp.text
    assert b"Tidak ada pengaduan internal yang sesuai kriteria." in resp.content


def test_export_endpoint_rejects_a_malformed_or_inverted_period(
    http_client: TestClient,
):
    bad_format = http_client.get(
        "/api/v1/internal/complaints/export", params={"dateFrom": "01-09-2026"}
    )
    assert bad_format.status_code == 400, bad_format.text

    inverted = http_client.get(
        "/api/v1/internal/complaints/export",
        params={"dateFrom": "2026-09-30", "dateTo": "2026-09-01"},
    )
    assert inverted.status_code == 400, inverted.text


# --------------------------------------------------------------------------
# Report breakdown (API-554)
# --------------------------------------------------------------------------


def test_summarize_counts_the_whole_visible_population(
    service: InternalComplaintApplicationService,
):
    _create(service, priority="HIGH")
    _create(service, priority="HIGH")
    _create(service, priority="LOW", category="SYSTEM")

    summary = service.summarize(_principal(), org_unit_id="UPPPD-GAMBIR")
    assert summary.total_items == 3
    assert dict((b.key, b.count) for b in summary.by_priority) == {
        "HIGH": 2,
        "LOW": 1,
    }
    assert dict((b.key, b.count) for b in summary.by_status) == {"CREATED": 3}
    assert [b.key for b in summary.by_handling_unit] == ["UPPPD-GAMBIR"]


def test_summarize_applies_the_same_filters_as_the_list(
    service: InternalComplaintApplicationService,
):
    _create(service, category="OPERATIONAL")
    _create(service, category="SYSTEM")

    summary = service.summarize(
        _principal(), org_unit_id="UPPPD-GAMBIR", category="SYSTEM"
    )
    assert summary.total_items == 1


def test_summarize_respects_visibility(
    service: InternalComplaintApplicationService,
):
    _create(service, owner_unit_id="UPPPD-GAMBIR")
    _create(service, owner_unit_id="UPPPD-TANAH-ABANG")

    summary = service.summarize(_principal("UPPPD-GAMBIR"), org_unit_id="UPPPD-GAMBIR")
    assert summary.total_items == 1


def test_summary_endpoint_returns_the_breakdown(
    http_client: TestClient, service: InternalComplaintApplicationService
):
    _create(service, priority="CRITICAL")
    resp = http_client.get("/api/v1/internal/complaints/summary")
    assert resp.status_code == 200, resp.text
    body = resp.json()["data"]
    assert body["totalItems"] == 1
    assert body["byPriority"] == [{"key": "CRITICAL", "count": 1}]
    assert body["byStatus"] == [{"key": "CREATED", "count": 1}]
    assert body["byHandlingUnit"] == [{"key": "UPPPD-GAMBIR", "count": 1}]


def test_summary_endpoint_rejects_a_malformed_period(http_client: TestClient):
    resp = http_client.get(
        "/api/v1/internal/complaints/summary", params={"dateTo": "31-12-2026"}
    )
    assert resp.status_code == 400, resp.text


# --------------------------------------------------------------------------
# Renderer edge cases
# --------------------------------------------------------------------------


@pytest.mark.parametrize(
    ("date_from", "date_to", "expected"),
    [
        ("2026-09-01", None, b"Sejak 2026-09-01"),
        (None, "2026-09-30", b"Sampai 2026-09-30"),
        (None, None, b"Semua periode"),
    ],
)
def test_report_pdf_names_a_half_open_period(
    date_from: str | None, date_to: str | None, expected: bytes
):
    pdf = render_internal_report_pdf(
        InternalReportSnapshot(
            rows=[_summary()],
            total_matched=1,
            filters=InternalReportFilters(date_from=date_from, date_to=date_to),
            exported_at=datetime(2026, 9, 2, 3, 0, tzinfo=UTC),
        )
    )
    assert expected in pdf


def test_report_pdf_still_counts_a_status_outside_the_known_order():
    pdf = render_internal_report_pdf(
        InternalReportSnapshot(
            rows=[_summary(status="ESCALATED")],
            total_matched=1,
            exported_at=datetime(2026, 9, 2, 3, 0, tzinfo=UTC),
        )
    )
    assert b"ESCALATED" in pdf


def test_report_pdf_falls_back_to_a_dash_for_a_blank_priority():
    pdf = render_internal_report_pdf(
        InternalReportSnapshot(
            rows=[_summary(priority="")],
            total_matched=1,
            exported_at=datetime(2026, 9, 2, 3, 0, tzinfo=UTC),
        )
    )
    assert pdf.startswith(b"%PDF-1.4")


def test_report_pdf_truncates_a_subject_too_wide_for_its_column():
    pdf = render_internal_report_pdf(
        InternalReportSnapshot(
            rows=[_summary(subject="A" * 300)],
            total_matched=1,
            exported_at=datetime(2026, 9, 2, 3, 0, tzinfo=UTC),
        )
    )
    assert b"..." in pdf
    assert b"A" * 300 not in pdf


def test_report_pdf_repeats_the_table_header_across_pages():
    rows = [
        _summary(complaint_number=f"PI-GAM-2609-{index:03d}")
        for index in range(1, 121)
    ]
    pdf = render_internal_report_pdf(
        InternalReportSnapshot(
            rows=rows,
            total_matched=len(rows),
            exported_at=datetime(2026, 9, 2, 3, 0, tzinfo=UTC),
        )
    )
    assert pdf.count(b"(Prioritas)") >= 2
    assert b"PI-GAM-2609-120" in pdf
