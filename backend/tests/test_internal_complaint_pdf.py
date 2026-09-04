"""API-550 Pengaduan Internal snapshot PDF — renderer + filename."""

from __future__ import annotations

from datetime import UTC, datetime

from app.modules.internal_complaint.application.dto import (
    HistoryEventDTO,
    InternalComplaintDTO,
    ResolutionDTO,
)
from app.modules.internal_complaint.application.pdf import (
    InternalPdfAttachment,
    InternalPdfSnapshot,
    internal_pdf_filename,
    internal_pdf_masthead,
    render_internal_snapshot_pdf,
    strip_up3d_unit_prefix,
)


def _dto(**overrides: object) -> InternalComplaintDTO:
    base = InternalComplaintDTO(
        complaint_id="11111111-1111-4111-8111-111111111111",
        complaint_number="PI-TAB-2609-001",
        status="IN_PROGRESS",
        subject="Antrian cabang",
        description="Petugas cabang menunggu konfirmasi.",
        category="OPERATIONAL",
        priority="HIGH",
        owner_unit_id="UPPPD-TANAH-ABANG",
        handling_unit_id="PUSAT",
        created_by="creator-1",
        created_at=datetime(2026, 9, 1, 2, 0, tzinfo=UTC),
        chronology="Pukul 09.00 petugas menghubungi Pusat.",
        related_complaint_number="CMP-0001",
        history=[
            HistoryEventDTO(
                event_id="e1",
                event_type="CREATED",
                actor_id="creator-1",
                actor_unit_id="UPPPD-TANAH-ABANG",
                occurred_at=datetime(2026, 9, 1, 2, 0, tzinfo=UTC),
                note="Dibuat dari cabang",
            )
        ],
        resolution=ResolutionDTO(
            resolution_id="r1",
            resolution_code="IC_DONE",
            summary="Selesai koordinasi",
            status="PENDING_APPROVAL",
            comment="Sudah dikonfirmasi",
            proposed_by="handler-1",
            proposed_at=datetime(2026, 9, 1, 4, 0, tzinfo=UTC),
        ),
    )
    for key, value in overrides.items():
        setattr(base, key, value)
    return base


def test_internal_pdf_masthead_strips_upppd_and_omits_wp_name() -> None:
    assert strip_up3d_unit_prefix("UPPPD Tanah Abang") == "Tanah Abang"
    assert (
        internal_pdf_masthead(
            owner_unit_id="UPPPD-TANAH-ABANG",
            number="PI-TAB-2609-001",
        )
        == "TANAH-ABANG - PI-TAB-2609-001"
    )


def test_internal_pdf_filename_uses_jakarta_date() -> None:
    name = internal_pdf_filename(
        "PI-TAB-2609-001",
        datetime(2026, 9, 1, 17, 0, tzinfo=UTC),
    )
    assert name == "PI-TAB-2609-001_20260902.pdf"


def test_render_internal_snapshot_pdf_is_operator_ticket_not_wp_case() -> None:
    pdf = render_internal_snapshot_pdf(
        InternalPdfSnapshot(
            complaint=_dto(),
            created_by_name="Teguh",
            actor_names={"creator-1": "Teguh", "handler-1": "Dewi"},
            attachments=[
                InternalPdfAttachment(
                    original_name="bukti.zip",
                    mime_type="application/zip",
                    size_bytes=2048,
                    checksum_sha256="abc123def4567890ffff",
                    status="AVAILABLE",
                )
            ],
            exported_by="Teguh",
            exported_at=datetime(2026, 9, 2, 1, 0, tzinfo=UTC),
        )
    )
    assert pdf.startswith(b"%PDF-1.4")
    assert b"PI-TAB-2609-001" in pdf
    assert b"Antrian cabang" in pdf
    assert b"Dalam Penanganan" in pdf
    assert b"Pengaduan WP terkait" in pdf
    assert b"CMP-0001" in pdf
    assert b"bukti.zip" in pdf
    assert b"IC_DONE" not in pdf
    assert b"Selesai koordinasi" in pdf
    assert b"Pelanggan" not in pdf
    assert b"Nomor case" not in pdf
    assert b"File tidak tertanam" in pdf
    assert b"Dibuat dari cabang" in pdf
