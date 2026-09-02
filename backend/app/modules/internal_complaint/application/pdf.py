"""Pengaduan Internal snapshot PDF (API-550).

Operator-only. Same visibility as GET. Attachment bytes are never embedded.
Not reporting. Not a WP Case dump (that is API-539).
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from datetime import datetime
from zoneinfo import ZoneInfo

from app.core.operator_pdf import (
    OPERATOR_PDF_AGENCY,
    OperatorPdfDoc,
    dash,
    format_bytes,
)
from app.modules.cm_case.application.pdf_dates import (
    format_pdf_datetime,
    rewrite_iso_dates_in_text,
)
from app.modules.internal_complaint.application.dto import (
    AcceptanceDTO,
    HistoryEventDTO,
    InternalComplaintDTO,
    ResolutionDTO,
)
from app.modules.internal_complaint.domain.aggregate import (
    canonicalize_internal_handling_unit,
)

_OPERATOR_TZ = ZoneInfo("Asia/Jakarta")
_SAFE_FILENAME = re.compile(r"[^A-Za-z0-9._-]+")
_UNIT_PREFIX = re.compile(r"^(?:UPPPD|UP3D)[\s.\-]+", re.IGNORECASE)
_NOTE_INDENT = 24
_MACHINE_RESOLUTION = frozenset({"IC_DONE", "IC-OK"})

_STATUS_LABEL = {
    "CREATED": "Dibuat",
    "ASSIGNED": "Ditugaskan",
    "IN_PROGRESS": "Dalam Penanganan",
    "RESOLVED": "Terselesaikan",
    "CLOSED": "Ditutup",
    "WITHDRAWN": "Dibatalkan",
}
_CATEGORY_LABEL = {
    "PERFORMANCE": "Kinerja",
    "PROCESS_SOP": "Proses/SOP",
    "COORDINATION": "Koordinasi",
    "COMPLIANCE": "Kepatuhan",
    "SYSTEM": "Sistem",
    "OPERATIONAL": "Operasional",
    "OTHER": "Lainnya",
}
_PRIORITY_LABEL = {
    "LOW": "Rendah",
    "MEDIUM": "Sedang",
    "HIGH": "Tinggi",
    "CRITICAL": "Kritis",
}
_EVENT_LABEL = {
    "CREATED": "Pengaduan dibuat",
    "TRANSFER": "Unit penanganan dipindah",
    "TRANSFER_REQUESTED": "Permintaan pindah diajukan",
    "TRANSFER_REQUEST_APPROVED": "Permintaan pindah disetujui",
    "TRANSFER_REQUEST_REJECTED": "Permintaan pindah ditolak",
    "RECEIVED": "Pengaduan diterima",
    "REVIEW": "Tinjauan dimulai",
    "RESOLUTION": "Penyelesaian dicatat",
    "HANDLING_UNIT_ACCEPT": "Unit penanganan menyetujui",
    "HANDLING_UNIT_REJECT": "Dikembalikan ke pengerjaan",
    "OWNER_ACCEPT": "Unit pemilik menyetujui",
    "OWNER_REJECT": "Dikembalikan ke pengerjaan",
    "CLOSED": "Pengaduan ditutup",
    "WITHDRAWN": "Pengaduan dibatalkan",
    "WITHDRAW_REQUESTED": "Permintaan batal diajukan",
    "WITHDRAW_REQUEST_APPROVED": "Permintaan batal disetujui",
    "WITHDRAW_REQUEST_REJECTED": "Permintaan batal ditolak",
    "RETURNED_FOR_COMPLETION": "Dikembalikan ke cabang",
    "RESENT_TO_PUSAT": "Dikirim ulang ke Pusat",
}
_DECISION_LABEL = {
    "ACCEPT": "Setuju",
    "REJECT": "Tolak",
    "APPROVE": "Setujui",
}


@dataclass(frozen=True)
class InternalPdfAttachment:
    original_name: str
    mime_type: str
    size_bytes: int
    checksum_sha256: str
    status: str


@dataclass
class InternalPdfSnapshot:
    complaint: InternalComplaintDTO
    created_by_name: str | None = None
    closed_by_name: str | None = None
    withdrawn_by_name: str | None = None
    actor_names: dict[str, str] = field(default_factory=dict)
    attachments: list[InternalPdfAttachment] = field(default_factory=list)
    exported_by: str = ""
    exported_at: datetime | None = None


def strip_up3d_unit_prefix(name: str | None) -> str:
    raw = (name or "").strip()
    if not raw:
        return ""
    stripped = _UNIT_PREFIX.sub("", raw).strip()
    return stripped or raw


def internal_pdf_masthead(*, owner_unit_id: str | None, number: str | None) -> str:
    unit = strip_up3d_unit_prefix(owner_unit_id)
    num = (number or "").strip()
    if unit and num:
        return f"{unit} - {num}"
    return num or unit or "Pengaduan Internal"


def internal_pdf_filename(number: str, when: datetime | None = None) -> str:
    stamp = (when or datetime.now(_OPERATOR_TZ)).astimezone(_OPERATOR_TZ).strftime(
        "%Y%m%d"
    )
    raw = (number or "").strip() or "pengaduan-internal"
    safe = _SAFE_FILENAME.sub("-", raw).strip("-") or "pengaduan-internal"
    return f"{safe}_{stamp}.pdf"


def _label(table: dict[str, str], raw: str | None) -> str:
    key = (raw or "").strip()
    if not key:
        return "-"
    return table.get(key, key)


def _person(names: dict[str, str], user_id: str | None) -> str | None:
    if not user_id:
        return None
    return names.get(user_id) or user_id


def _hide_machine_code(code: str | None) -> str | None:
    raw = (code or "").strip()
    if not raw or raw.upper() in _MACHINE_RESOLUTION:
        return None
    return raw


def render_internal_snapshot_pdf(snapshot: InternalPdfSnapshot) -> bytes:
    exported_at = snapshot.exported_at or datetime.now(_OPERATOR_TZ)
    dto = snapshot.complaint
    footer = (
        f"INTERNAL  |  {dto.complaint_number}  |  "
        f"diunduh {format_pdf_datetime(exported_at)}  |  "
        f"{snapshot.exported_by or '-'}"
    )
    doc = OperatorPdfDoc(footer=footer)
    _write_snapshot(doc, snapshot, exported_at)
    return doc.build()


def _write_snapshot(
    doc: OperatorPdfDoc, snapshot: InternalPdfSnapshot, exported_at: datetime
) -> None:
    dto = snapshot.complaint
    names = snapshot.actor_names

    doc.letterhead_centered(
        OPERATOR_PDF_AGENCY,
        internal_pdf_masthead(
            owner_unit_id=dto.owner_unit_id,
            number=dto.complaint_number,
        ),
        subject=dto.subject,
    )
    doc.blank()

    doc.heading("Identitas")
    identity: list[tuple[str, str | None]] = [
        ("Nomor", dto.complaint_number),
        ("Status", _label(_STATUS_LABEL, dto.status)),
        ("Prioritas", _label(_PRIORITY_LABEL, dto.priority)),
        ("Kategori", _label(_CATEGORY_LABEL, dto.category)),
        ("Unit pemilik", canonicalize_internal_handling_unit(dto.owner_unit_id)),
        (
            "Unit penanganan",
            canonicalize_internal_handling_unit(dto.handling_unit_id),
        ),
        ("Pengaduan WP terkait", dto.related_complaint_number),
        ("Dibuat oleh", snapshot.created_by_name or dto.created_by),
        ("Dibuat pada", format_pdf_datetime(dto.created_at)),
    ]
    if dto.updated_at:
        identity.append(("Diubah pada", format_pdf_datetime(dto.updated_at)))
    if dto.closed_at:
        identity.append(
            ("Ditutup oleh", snapshot.closed_by_name or dto.closed_by)
        )
        identity.append(("Ditutup pada", format_pdf_datetime(dto.closed_at)))
    if dto.withdrawn_at:
        identity.append(
            ("Dibatalkan oleh", snapshot.withdrawn_by_name or dto.withdrawn_by)
        )
        identity.append(("Dibatalkan pada", format_pdf_datetime(dto.withdrawn_at)))
        if dto.withdraw_reason:
            identity.append(("Alasan batal", dto.withdraw_reason))
    if dto.transfer_request_status:
        identity.append(("Permintaan pindah", dto.transfer_request_status))
        if dto.transfer_request_destination_unit_id:
            identity.append(
                ("Tujuan permintaan pindah", dto.transfer_request_destination_unit_id)
            )
    if dto.withdraw_request_status:
        identity.append(("Permintaan batal", dto.withdraw_request_status))
    if dto.completion_request_status:
        identity.append(("Kelengkapan berkas", dto.completion_request_status))
        if dto.completion_return_reason:
            identity.append(("Alasan dikembalikan", dto.completion_return_reason))
    doc.kv_block(identity)
    doc.blank()
    doc.rule()

    doc.heading("Uraian")
    if (dto.description or "").strip():
        doc.pre(dto.description)
    else:
        doc.muted("Tidak ada deskripsi.")
    if (dto.chronology or "").strip():
        doc.blank()
        doc.heading("Kronologi")
        doc.pre(dto.chronology)
    if (dto.impact or "").strip():
        doc.blank()
        doc.heading("Dampak")
        doc.pre(dto.impact)
    doc.blank()

    doc.heading("Penyelesaian")
    _write_resolution(doc, dto.resolution, names)
    doc.blank()

    doc.heading("Persetujuan penutup")
    if not dto.handling_unit_acceptance and not dto.owner_acceptance:
        doc.muted("Belum ada cap persetujuan.")
    else:
        _write_acceptance(doc, "Unit penanganan", dto.handling_unit_acceptance, names)
        _write_acceptance(doc, "Unit pemilik", dto.owner_acceptance, names)
    doc.blank()
    doc.rule()

    doc.heading("Lampiran")
    if not snapshot.attachments:
        doc.muted("Tidak ada lampiran pada tiket ini.")
    else:
        doc.muted("Hanya daftar (nama, tipe, ukuran, hash). File tidak tertanam.")
        for item in snapshot.attachments:
            checksum = (item.checksum_sha256 or "").strip()
            checksum_short = checksum[:16] + ("..." if len(checksum) > 16 else "")
            doc.para(
                f"* {dash(item.original_name)}  |  {format_bytes(item.size_bytes)}  |  "
                f"{dash(item.mime_type)}  |  {dash(item.status)}  |  "
                f"{checksum_short or '-'}"
            )
    doc.blank()

    doc.heading("Riwayat")
    if not dto.history:
        doc.muted("Belum ada kejadian tercatat.")
    else:
        for entry in dto.history:
            _write_history_entry(doc, entry, names)
    doc.blank()
    doc.muted(f"Dibuat {format_pdf_datetime(exported_at)} (Asia/Jakarta).")


def _write_resolution(
    doc: OperatorPdfDoc, resolution: ResolutionDTO | None, names: dict[str, str]
) -> None:
    if resolution is None:
        doc.muted("Belum ada usulan penyelesaian.")
        return
    rows: list[tuple[str, str | None]] = [
        ("Status usulan", resolution.status),
        ("Ringkasan", resolution.summary),
        ("Komentar", resolution.comment),
        ("Diajukan oleh", _person(names, resolution.proposed_by)),
        ("Diajukan pada", format_pdf_datetime(resolution.proposed_at)),
    ]
    code = _hide_machine_code(resolution.resolution_code)
    if code:
        rows.insert(1, ("Kode", code))
    if resolution.detail:
        rows.append(("Detail", resolution.detail))
    if resolution.decided_by:
        rows.append(("Diputus oleh", _person(names, resolution.decided_by)))
        rows.append(("Diputus pada", format_pdf_datetime(resolution.decided_at)))
    if resolution.rejection_reason:
        rows.append(("Alasan tolak", resolution.rejection_reason))
    doc.kv_block(rows)


def _write_acceptance(
    doc: OperatorPdfDoc,
    heading: str,
    acceptance: AcceptanceDTO | None,
    names: dict[str, str],
) -> None:
    if acceptance is None:
        doc.para(f"{heading}: belum")
        return
    actor = _person(names, acceptance.actor_id)
    decision = _label(_DECISION_LABEL, acceptance.decision)
    when = format_pdf_datetime(acceptance.decided_at)
    doc.para(f"{heading}: {decision}  |  {dash(actor)}  |  {when}")
    if acceptance.note:
        doc.para(rewrite_iso_dates_in_text(acceptance.note), indent=_NOTE_INDENT)


def _write_history_entry(
    doc: OperatorPdfDoc, entry: HistoryEventDTO, names: dict[str, str]
) -> None:
    when = format_pdf_datetime(entry.occurred_at)
    actor = dash(_person(names, entry.actor_id) or entry.actor_id)
    label = _label(_EVENT_LABEL, entry.event_type)
    doc.para(f"{when}  |  {label}  |  {actor}")
    unit_move = ""
    source = canonicalize_internal_handling_unit(entry.source_unit_id) or (
        entry.source_unit_id or ""
    ).strip()
    target = canonicalize_internal_handling_unit(entry.target_unit_id) or (
        entry.target_unit_id or ""
    ).strip()
    if source and target and source != target:
        unit_move = f"{source} -> {target}"
    if unit_move:
        doc.para(unit_move, indent=_NOTE_INDENT)
    if entry.note:
        doc.para(rewrite_iso_dates_in_text(entry.note), indent=_NOTE_INDENT)
