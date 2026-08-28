"""Internal Case snapshot PDF (API-539 / FR-003 companion).

Stdlib-only PDF 1.4 (Helvetica). Not customer-safe. Not reporting.
Attachment bytes are never embedded — callers pass a filename manifest.
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from datetime import date, datetime
from zoneinfo import ZoneInfo

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

_OPERATOR_TZ = ZoneInfo("Asia/Jakarta")
_PAGE_W = 595
_PAGE_H = 842
_MARGIN_X = 50
_MARGIN_TOP = 800
_MARGIN_BOTTOM = 48
_BODY_SIZE = 10
_HEAD_SIZE = 13
_TITLE_SIZE = 16
_LINE = 13
_WRAP = 92

_MONTHS_ID = (
    "",
    "Januari",
    "Februari",
    "Maret",
    "April",
    "Mei",
    "Juni",
    "Juli",
    "Agustus",
    "September",
    "Oktober",
    "November",
    "Desember",
)
_UNICODE_ASCII = str.maketrans(
    {
        "\u2014": "-",
        "\u2013": "-",
        "\u2026": "...",
        "\u00a0": " ",
        "\u2018": "'",
        "\u2019": "'",
        "\u201c": '"',
        "\u201d": '"',
    }
)
_SAFE_FILENAME = re.compile(r"[^A-Za-z0-9._-]+")
_UNIT_PREFIX = re.compile(r"^(?:UPPPD|UP3D)[\s.\-]+", re.IGNORECASE)
_UUID = re.compile(
    r"^[0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{12}$"
)
CASE_PDF_AGENCY = "Unit Pelayanan Pemungutan Pajak Daerah"
_CONTENT_WIDTH = _PAGE_W - 2 * _MARGIN_X
# Adobe Helvetica-Bold AFM widths for ASCII 32-126 (units / 1000 em).
_HELVETICA_BOLD_ASCII = (
    278, 333, 474, 556, 556, 889, 722, 278, 333, 333, 389, 584, 278, 333, 278,
    278, 556, 556, 556, 556, 556, 556, 556, 556, 556, 556, 333, 333, 584, 584,
    584, 611, 975, 722, 667, 722, 722, 667, 611, 778, 722, 278, 556, 722, 611,
    833, 722, 778, 667, 778, 722, 667, 611, 722, 667, 944, 667, 667, 611, 333,
    278, 333, 584, 556, 278, 556, 611, 556, 611, 556, 333, 611, 611, 278, 278,
    556, 278, 889, 611, 611, 611, 611, 389, 556, 333, 611, 556, 778, 556, 556,
    500, 389, 280, 389, 584,
)


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
    if value is None:
        return "-"
    local = value.astimezone(_OPERATOR_TZ) if value.tzinfo else value
    return local.strftime("%d/%m/%Y %H:%M")


def format_catatan_dt(value: datetime | None) -> str | None:
    if value is None:
        return None
    local = value.astimezone(_OPERATOR_TZ) if value.tzinfo else value
    month = _MONTHS_ID[local.month] if 1 <= local.month <= 12 else ""
    return f"{local.day:02d} {month} {local.year}, {local.strftime('%H.%M')}"


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


def _dash(value: str | None) -> str:
    text = (value or "").strip()
    return text if text else "-"


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
    )
    if case.subject.strip():
        doc.muted(case.subject.strip())
    doc.blank()

    doc.heading("Identitas")
    doc.kv("Nomor case", case.case_number)
    doc.kv("Status", case.status)
    doc.kv("Prioritas", case.priority)
    doc.kv("Jenis", case.case_type)
    if case.category:
        doc.kv("Kategori", case.category)
    doc.kv("No. pengaduan", snapshot.complaint_number)
    doc.kv("Unit pemilik", case.owner_unit_id or case.owning_unit_id)
    doc.kv("Unit penanganan", case.owning_unit_id)
    doc.kv("Pelanggan", operator_visible_name(snapshot.customer_label))
    doc.kv("Petugas", snapshot.handler_name or case.handling_claimed_by)
    if snapshot.assigned_name or case.assigned_user_id:
        doc.kv("Ditugaskan ke", snapshot.assigned_name or case.assigned_user_id)
    doc.kv("Dibuat oleh", snapshot.created_by_name or case.created_by)
    doc.kv("Dibuat pada", format_operator_dt(case.created_at))
    if case.updated_at:
        doc.kv("Diubah pada", format_operator_dt(case.updated_at))
    if case.closed_at:
        doc.kv("Ditutup pada", format_operator_dt(case.closed_at))
    if case.cancel_reason:
        doc.kv("Alasan batal", case.cancel_reason)
    doc.kv("Eskalasi ke Pusat", "Ya" if case.escalated_to_pusat else "Tidak")
    doc.blank()

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
                doc.para(f"    {entry.note}")
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
    prefix = "    " if nested else ""
    head = note.label
    if meta_parts:
        head = f"{head}  |  {' | '.join(meta_parts)}"
    doc.para(f"{prefix}{head}")
    body = format_schedule_body(note, destination_unit_id=destination_unit_id)
    if body:
        for line in body.split("\n"):
            doc.para(f"{prefix}    {line}" if nested else f"    {line}")


def _format_bytes(size: int) -> str:
    if size < 1024:
        return f"{size} B"
    if size < 1024 * 1024:
        return f"{size / 1024:.1f} KB"
    return f"{size / (1024 * 1024):.1f} MB"


class _PdfDoc:
    def __init__(self, *, footer: str) -> None:
        self._footer = footer
        self._pages: list[list[str]] = [[]]
        self._y = _MARGIN_TOP

    def title(self, text: str) -> None:
        self._ensure(28)
        self._text(text, size=_TITLE_SIZE, bold=True)
        self._y -= 20

    def letterhead_centered(self, agency: str, unit_line: str) -> None:
        self._ensure(52)
        for line in _wrap_to_width(agency, max_pt=_CONTENT_WIDTH, size=_HEAD_SIZE):
            self._text(line, size=_HEAD_SIZE, bold=True, align="center")
            self._y -= 16
        self._y -= 2
        for line in _wrap_to_width(unit_line, max_pt=_CONTENT_WIDTH, size=_TITLE_SIZE):
            self._text(line, size=_TITLE_SIZE, bold=True, align="center")
            self._y -= 20

    def heading(self, text: str) -> None:
        self._ensure(24)
        self._y -= 4
        self._text(text, size=_HEAD_SIZE, bold=True)
        self._y -= 16

    def muted(self, text: str) -> None:
        for line in _wrap(text, _WRAP):
            self._ensure(_LINE)
            self._text(line, size=9, italic=True)
            self._y -= _LINE

    def kv(self, label: str, value: str | None) -> None:
        self.para(f"{label}: {_dash(value)}")

    def block(self, label: str, value: str | None) -> None:
        self.para(f"{label}:")
        body = (value or "").strip() or "-"
        for line in _wrap(body, _WRAP):
            self.para(line)

    def pre(self, text: str) -> None:
        for line in _wrap((text or "").replace("\r", ""), _WRAP):
            self._ensure(_LINE)
            self._text(line, size=_BODY_SIZE)
            self._y -= _LINE

    def para(self, text: str) -> None:
        for line in _wrap(text, _WRAP):
            self._ensure(_LINE)
            self._text(line, size=_BODY_SIZE)
            self._y -= _LINE

    def blank(self) -> None:
        self._y -= 8

    def _ensure(self, need: int) -> None:
        if self._y - need < _MARGIN_BOTTOM:
            self._pages.append([])
            self._y = _MARGIN_TOP

    def _text(
        self,
        text: str,
        *,
        size: int,
        bold: bool = False,
        italic: bool = False,
        align: str = "left",
    ) -> None:
        font = "F2" if bold else "F3" if italic else "F1"
        x = float(_MARGIN_X)
        if align == "center":
            width = _helvetica_bold_width(text, size)
            x = max((_PAGE_W - width) / 2.0, _MARGIN_X / 2.0)
        cmd = (
            f"BT /{font} {size} Tf {x:.2f} {self._y} Td "
            f"({_pdf_escape(text)}) Tj ET"
        )
        self._pages[-1].append(cmd)

    def build(self) -> bytes:
        objects: list[bytes] = []
        # 1 Catalog, 2 Pages — filled after page objects are known
        font_f1 = b"<< /Type /Font /Subtype /Type1 /BaseFont /Helvetica >>"
        font_f2 = b"<< /Type /Font /Subtype /Type1 /BaseFont /Helvetica-Bold >>"
        font_f3 = b"<< /Type /Font /Subtype /Type1 /BaseFont /Helvetica-Oblique >>"

        page_streams: list[bytes] = []
        for index, commands in enumerate(self._pages, start=1):
            stamp = (
                f"BT /F3 8 Tf {_MARGIN_X} 28 Td "
                f"({_pdf_escape(self._footer)}  |  {index}/{len(self._pages)}) Tj ET"
            )
            content = "\n".join([*commands, stamp]).encode("latin-1", "replace")
            page_streams.append(content)

        # Object numbers: 1 Catalog, 2 Pages, 3-5 fonts, then pairs of Page+Content
        fonts_start = 3
        first_page_obj = 6
        kids: list[int] = []
        page_objs: list[tuple[int, bytes]] = []
        for i, stream in enumerate(page_streams):
            page_id = first_page_obj + i * 2
            content_id = page_id + 1
            kids.append(page_id)
            page_dict = (
                f"<< /Type /Page /Parent 2 0 R /MediaBox [0 0 {_PAGE_W} {_PAGE_H}] "
                f"/Contents {content_id} 0 R /Resources << /Font << "
                f"/F1 {fonts_start} 0 R /F2 {fonts_start + 1} 0 R "
                f"/F3 {fonts_start + 2} 0 R >> >> >>"
            ).encode("ascii")
            stream_obj = (
                f"<< /Length {len(stream)} >>\nstream\n".encode("ascii")
                + stream
                + b"\nendstream"
            )
            page_objs.append((page_id, page_dict))
            page_objs.append((content_id, stream_obj))

        kids_ref = " ".join(f"{n} 0 R" for n in kids)
        catalog = b"<< /Type /Catalog /Pages 2 0 R >>"
        pages = (
            f"<< /Type /Pages /Kids [{kids_ref}] /Count {len(self._pages)} >>"
        ).encode("ascii")

        objects = [catalog, pages, font_f1, font_f2, font_f3]
        # page_objs are sequential starting at 6; extend in order
        objects.extend(body for _, body in page_objs)
        return _finalize_pdf(objects)


def _helvetica_bold_width(text: str, size: int) -> float:
    total = 0
    for ch in text.translate(_UNICODE_ASCII):
        o = ord(ch)
        if 32 <= o <= 126:
            total += _HELVETICA_BOLD_ASCII[o - 32]
        else:
            total += 600
    return total * size / 1000.0


def _wrap_to_width(text: str, *, max_pt: float, size: int) -> list[str]:
    raw = (text or "").strip()
    if not raw:
        return [""]
    words = raw.split(" ")
    lines: list[str] = []
    current = ""
    for word in words:
        trial = f"{current} {word}".strip() if current else word
        if _helvetica_bold_width(trial, size) <= max_pt:
            current = trial
            continue
        if current:
            lines.append(current)
        current = word
        while _helvetica_bold_width(current, size) > max_pt and len(current) > 1:
            cut = max(1, int(len(current) * max_pt / _helvetica_bold_width(current, size)))
            lines.append(current[:cut])
            current = current[cut:]
    if current:
        lines.append(current)
    return lines or [""]


def _wrap(text: str, width: int) -> list[str]:
    if not text:
        return [""]
    lines: list[str] = []
    for paragraph in text.replace("\r", "").split("\n"):
        if not paragraph:
            lines.append("")
            continue
        current = ""
        for word in paragraph.split(" "):
            piece = word if word else ""
            trial = f"{current} {piece}".strip() if current else piece
            if len(trial) <= width:
                current = trial
                continue
            if current:
                lines.append(current)
            while len(piece) > width:
                lines.append(piece[:width])
                piece = piece[width:]
            current = piece
        lines.append(current)
    return lines or [""]


def _pdf_escape(text: str) -> str:
    out: list[str] = []
    for ch in text.translate(_UNICODE_ASCII):
        o = ord(ch)
        if ch in "\\()":
            out.append(f"\\{ch}")
        elif 32 <= o <= 126:
            out.append(ch)
        elif 128 <= o <= 255:
            out.append(f"\\{o:03o}")
        else:
            out.append("?")
    return "".join(out)


def _finalize_pdf(objects: list[bytes]) -> bytes:
    chunks: list[bytes] = [b"%PDF-1.4\n"]
    offsets = [0]
    cursor = len(chunks[0])
    for i, body in enumerate(objects, start=1):
        header = f"{i} 0 obj\n".encode("ascii")
        block = header + body + b"\nendobj\n"
        offsets.append(cursor)
        chunks.append(block)
        cursor += len(block)
    xref_pos = cursor
    xref = [f"xref\n0 {len(objects) + 1}\n0000000000 65535 f \n".encode("ascii")]
    for off in offsets[1:]:
        xref.append(f"{off:010d} 00000 n \n".encode("ascii"))
    trailer = (
        f"trailer\n<< /Size {len(objects) + 1} /Root 1 0 R >>\n"
        f"startxref\n{xref_pos}\n%%EOF\n"
    ).encode("ascii")
    return b"".join(chunks + xref + [trailer])
