"""Internal Case snapshot PDF (API-539 / FR-003 companion).

Stdlib-only PDF 1.4 (Helvetica). Not customer-safe. Not reporting.
Attachment bytes are never embedded — callers pass a filename manifest.
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from datetime import date, datetime
from zoneinfo import ZoneInfo

from app.core.operator_pdf import (
    OPERATOR_PDF_AGENCY,
    OperatorPdfDoc,
    dash,
    format_bytes,
)
from app.modules.cm_case.api.schemas import CaseHistoryEntry
from app.modules.cm_case.application.case_work_card import (
    HandlingNote,
    case_description_narrative,
    collect_handling_notes,
    event_label,
    format_schedule_body,
    group_handling_notes,
    resolution_card_text,
)
from app.modules.cm_case.application.dto import CaseDTO
from app.modules.cm_case.application.pdf_dates import (
    format_pdf_datetime,
    rewrite_iso_dates_in_text,
)

_OPERATOR_TZ = ZoneInfo("Asia/Jakarta")
_SAFE_FILENAME = re.compile(r"[^A-Za-z0-9._-]+")
_UNIT_PREFIX = re.compile(r"^(?:UPPPD|UP3D)[\s.\-]+", re.IGNORECASE)
_UUID = re.compile(
    r"^[0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{12}$"
)
CASE_PDF_AGENCY = OPERATOR_PDF_AGENCY
#: Note/body inset (spaces were stripped by wrapping, so this is a real x-shift).
_NOTE_BODY_INDENT = 24
_NESTED_HEAD_INDENT = 12
_PdfDoc = OperatorPdfDoc
_dash = dash
_format_bytes = format_bytes


@dataclass(frozen=True)
class CasePdfAttachment:
    original_name: str
    mime_type: str
    size_bytes: int
    checksum_sha256: str
    status: str
    classification: str
    case_id: str | None = None


@dataclass
class CasePdfSnapshot:
    case: CaseDTO
    complaint_number: str | None = None
    customer_label: str | None = None
    created_by_name: str | None = None
    handler_name: str | None = None
    assigned_name: str | None = None
    hq_arrival_date: date | None = None
    hq_arrival_time: str | None = None
    hq_destination_unit_id: str | None = None
    history: list[CaseHistoryEntry] = field(default_factory=list)
    attachments: list[CasePdfAttachment] = field(default_factory=list)
    parent_intake_note: str | None = None
    created_unit_name: str | None = None
    exported_by: str = ""
    exported_at: datetime | None = None


def strip_up3d_unit_prefix(name: str | None) -> str:
    """Drop the shared UPPPD / UP3D prefix so the letterhead can spell it out."""
    raw = (name or "").strip()
    if not raw:
        return ""
    stripped = _UNIT_PREFIX.sub("", raw).strip()
    return stripped or raw


def operator_visible_name(value: str | None) -> str | None:
    """Operator-facing label — never an internal UUID."""
    text = (value or "").strip()
    if not text or _UUID.match(text):
        return None
    return text


def case_pdf_masthead(
    *,
    unit_name: str | None,
    case_number: str | None,
    customer_name: str | None = None,
) -> str:
    """Second letterhead line: unit (no UPPPD/UP3D) - Case number ( WP name )."""
    unit = strip_up3d_unit_prefix(unit_name)
    number = (case_number or "").strip()
    if unit and number:
        head = f"{unit} - {number}"
    else:
        head = number or unit or "Case"
    wp = operator_visible_name(customer_name)
    if wp:
        return f"{head} ( {wp} )"
    return head


def case_pdf_filename(case_number: str, when: datetime | None = None) -> str:
    stamp = (when or datetime.now(_OPERATOR_TZ)).astimezone(_OPERATOR_TZ).strftime(
        "%Y%m%d"
    )
    raw = (case_number or "").strip() or "case"
    safe = _SAFE_FILENAME.sub("-", raw).strip("-") or "case"
    return f"{safe}_{stamp}.pdf"


def format_operator_dt(value: datetime | None) -> str:
    return format_pdf_datetime(value)


def format_catatan_dt(value: datetime | None) -> str | None:
    if value is None:
        return None
    return format_pdf_datetime(value)


def render_case_snapshot_pdf(snapshot: CasePdfSnapshot) -> bytes:
    """Render an internal snapshot. Does not mutate Case state."""
    exported_at = snapshot.exported_at or datetime.now(_OPERATOR_TZ)
    footer = (
        f"INTERNAL  |  {snapshot.case.case_number}  |  "
        f"diunduh {format_operator_dt(exported_at)}  |  "
        f"{snapshot.exported_by or '-'}"
    )
    doc = _PdfDoc(footer=footer)
    _write_snapshot(doc, snapshot, exported_at)
    return doc.build()


def _write_snapshot(doc: _PdfDoc, snapshot: CasePdfSnapshot, exported_at: datetime) -> None:
    case = snapshot.case
    notes = collect_handling_notes(
        case.description,
        snapshot.history,
        parent_intake_note=snapshot.parent_intake_note,
        resolution_texts=[
            case.resolution.summary if case.resolution else None,
            case.resolution.comment if case.resolution else None,
            case.resolution.detail if case.resolution else None,
        ],
    )
    narrative = case_description_narrative(case.description)
    resolusi_lead, resolusi_lines = resolution_card_text(case, notes)

    doc.letterhead_centered(
        CASE_PDF_AGENCY,
        case_pdf_masthead(
            unit_name=snapshot.created_unit_name,
            case_number=case.case_number,
            customer_name=snapshot.customer_label,
        ),
        subject=case.subject,
    )
    doc.blank()

    doc.heading("Identitas")
    identity: list[tuple[str, str | None]] = [
        ("Nomor case", case.case_number),
        ("Status", case.status),
        ("Prioritas", case.priority),
        ("Jenis", case.case_type),
    ]
    if case.category:
        identity.append(("Kategori", case.category))
    identity.extend(
        [
            ("No. pengaduan", snapshot.complaint_number),
            ("Unit pemilik", case.owner_unit_id or case.owning_unit_id),
            ("Unit penanganan", case.owning_unit_id),
            ("Pelanggan", operator_visible_name(snapshot.customer_label)),
            ("Petugas", snapshot.handler_name or case.handling_claimed_by),
        ]
    )
    if snapshot.assigned_name or case.assigned_user_id:
        identity.append(
            ("Ditugaskan ke", snapshot.assigned_name or case.assigned_user_id)
        )
    identity.append(("Dibuat oleh", snapshot.created_by_name or case.created_by))
    identity.append(("Dibuat pada", format_operator_dt(case.created_at)))
    if case.updated_at:
        identity.append(("Diubah pada", format_operator_dt(case.updated_at)))
    if case.closed_at:
        identity.append(("Ditutup pada", format_operator_dt(case.closed_at)))
    if case.cancel_reason:
        identity.append(("Alasan batal", case.cancel_reason))
    identity.append(
        ("Eskalasi ke Pusat", "Ya" if case.escalated_to_pusat else "Tidak")
    )
    doc.kv_block(identity)
    doc.blank()
    doc.rule()

    doc.heading("Deskripsi")
    if narrative:
        doc.pre(narrative)
    else:
        doc.muted("Tidak ada deskripsi.")
    doc.blank()

    doc.heading("Catatan")
    groups = group_handling_notes(notes)
    if not groups:
        doc.muted("Belum ada catatan penanganan.")
    else:
        for group in groups:
            _write_handling_note(
                doc,
                group.parent,
                destination_unit_id=snapshot.hq_destination_unit_id,
            )
            for child in group.children:
                _write_handling_note(
                    doc,
                    child,
                    nested=True,
                    destination_unit_id=snapshot.hq_destination_unit_id,
                )
    doc.blank()

    doc.heading("Resolusi")
    doc.para(resolusi_lead)
    for line in resolusi_lines:
        doc.pre(line)
    doc.blank()
    doc.rule()

    doc.heading("Lampiran")
    if not snapshot.attachments:
        doc.muted("Tidak ada lampiran dalam lingkup Case ini.")
    else:
        doc.muted("Hanya daftar (nama, tipe, ukuran, hash). File tidak tertanam.")
        for item in snapshot.attachments:
            pin = "Case ini" if (item.case_id or "").strip() else "Pengaduan (bersama)"
            size = _format_bytes(item.size_bytes)
            checksum = (item.checksum_sha256 or "").strip()
            checksum_short = checksum[:16] + ("..." if len(checksum) > 16 else "")
            doc.para(
                f"* {_dash(item.original_name)}  |  {size}  |  "
                f"{_dash(item.mime_type)}  |  {_dash(item.classification)}  |  "
                f"{_dash(item.status)}  |  {pin}  |  {checksum_short or '-'}"
            )
    doc.blank()

    doc.heading("Riwayat Case")
    if not snapshot.history:
        doc.muted("Belum ada kejadian tercatat untuk Case ini.")
    else:
        prior: list[str] = []
        for entry in snapshot.history:
            when = format_operator_dt(entry.occurred_at)
            actor = _dash(entry.actor_name or entry.actor_id)
            label = event_label(entry.event_code, prior)
            doc.para(f"{when}  |  {label}  |  {actor}")
            if entry.note:
                doc.para(
                    rewrite_iso_dates_in_text(entry.note),
                    indent=_NOTE_BODY_INDENT,
                )
            prior.append(entry.event_code)
    doc.blank()
    doc.muted(f"Dibuat {format_operator_dt(exported_at)} (Asia/Jakarta).")


def _write_handling_note(
    doc: _PdfDoc,
    note: HandlingNote,
    *,
    nested: bool = False,
    destination_unit_id: str | None = None,
) -> None:
    meta_parts = [p for p in (note.actor_name, format_catatan_dt(note.occurred_at)) if p]
    head_indent = _NESTED_HEAD_INDENT if nested else 0
    head = note.label
    if meta_parts:
        head = f"{head}  |  {' | '.join(meta_parts)}"
    doc.para(head, indent=head_indent)
    body = format_schedule_body(note, destination_unit_id=destination_unit_id)
    if body:
        for line in rewrite_iso_dates_in_text(body).split("\n"):
            text = line.strip()
            if not text:
                continue
            doc.para(text, indent=head_indent + _NOTE_BODY_INDENT)

