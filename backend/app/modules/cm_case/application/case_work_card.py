"""Work-card projection for API-539 — same Deskripsi/Catatan/Resolusi as the Case page.

Mirrors frontend ``caseHandlingNotes.ts`` + ``parseCmBatch1Description`` so the
PDF is not a raw blob / event-code dump. Indonesian labels are fixed (lab UI).
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from datetime import datetime

from app.modules.cm_batch1.intake_narrative import parse_intake_description
from app.modules.cm_case.api.schemas import CaseHistoryEntry
from app.modules.cm_case.application.dto import CaseDTO, ResolutionDTO

INTAKE_PARENT_CODES = frozenset({"CASE_CREATED", "CASE_ESCALATED_TO_PUSAT"})
HISTORY_NOTE_EXCLUDED_CODES = frozenset(
    {
        "CASE_RESOLVED",
        "CASE_CLOSED",
        "CASE_OWNER_ACCEPTED",
        "CASE_OWNER_REJECTED",
        "CASE_HANDLING_UNIT_ACCEPTED",
        "CASE_HANDLING_UNIT_REJECTED",
    }
)
_RE_ESCALATION_PRIOR = frozenset(
    {
        "CASE_ESCALATED_TO_PUSAT",
        "CASE_ESCALATION_RETURNED",
        "CASE_ESCALATION_TO_PUSAT_CANCELLED",
    }
)
_INLINE_NOTE = re.compile(r"\n\n(?:Catatan|Note):\s*\n", re.IGNORECASE)
_LEADING_DESCRIPTION = re.compile(r"^(Deskripsi|Description):\s*\n", re.IGNORECASE)

EVENT_LABELS: dict[str, str] = {
    "CASE_CREATED": "Case dibuat",
    "CASE_WORK_STARTED": "Pengerjaan dimulai",
    "CASE_ASSIGNED": "Case ditugaskan",
    "CASE_CANCELLED": "Case dibatalkan",
    "CASE_STATUS_CHANGED": "Status Case diubah",
    "CASE_CLOSED": "Case ditutup",
    "CASE_RESOLVED": "Case diselesaikan",
    "HANDLING_CONTINUED": "Melanjutkan penanganan",
    "HANDLING_TAKEN_OVER": "Mengambil alih penanganan",
    "CASE_HANDLING_UNIT_ACCEPTED": "Unit penanganan menerima",
    "CASE_OWNER_ACCEPTED": "Pemilik menerima",
    "CASE_HANDLING_UNIT_REJECTED": "Unit penanganan menolak",
    "CASE_OWNER_REJECTED": "Pemilik menolak",
    "RESOLUTION_UPDATED": "Resolusi diperbarui",
    "ATTACHMENT_BOUND": "Lampiran ditautkan",
    "ATTACHMENT_UPLOADED": "Lampiran diunggah",
    "HQ_ACCEPTED": "Diterima Pusat",
    "HQ_ARRIVAL_SCHEDULED": "Kedatangan dijadwalkan",
    "HQ_COMPLETED": "Selesai di Pusat",
    "HQ_RETURNED": "Dikembalikan Pusat",
    "CASE_ESCALATED_TO_PUSAT": "Diajukan ke Pusat",
    "CASE_ESCALATION_TO_PUSAT_CANCELLED": "Eskalasi dibatalkan",
    "CASE_ESCALATION_RETURNED": "Dikembalikan Pusat",
}
RE_ESCALATED_LABEL = "Diajukan kembali ke Pusat"
RESCHEDULED_LABEL = "Jadwal kedatangan diubah"
INTAKE_LABEL = "Catatan"
HQ_CLOSED_RESOLUTION = (
    "Case ini ditutup melalui penyelesaian di Pusat, bukan alur resolusi "
    "cabang - lihat Catatan di atas untuk hasilnya."
)
NO_BRANCH_RESOLUTION = (
    "Belum ada resolusi. Resolusi akan tampil di sini setelah Case diselesaikan."
)
HQ_RETURN_REASON_LABELS: dict[str, str] = {
    "MISSING_ATTACHMENT": "Lampiran/bukti kurang",
    "INCOMPLETE_CHRONOLOGY": "Kronologi tidak lengkap",
    "UNCLEAR_CUSTOMER_DATA": "Data wajib pajak tidak jelas",
    "WRONG_CATEGORY_OR_ROUTING": "Kategori/rute salah",
    "ADDITIONAL_EVIDENCE_REQUIRED": "Perlu bukti tambahan",
    "OTHER": "Lainnya",
}
_HQ_RETURN_PREFIX = re.compile(r"^\[([A-Z][A-Z0-9_]*)\]\s*([\s\S]*)$")

BLOB_FIELDS = (
    ("escalation_reason", "Alasan eskalasi"),
    ("supervisor_note", "Catatan Supervisor"),
    ("rejection_note", "Penolakan eskalasi"),
    ("cancellation_note", "Batalkan eskalasi"),
)


@dataclass
class HandlingNote:
    key: str
    source: str
    label: str
    text: str
    event_code: str | None = None
    actor_name: str | None = None
    occurred_at: datetime | None = None
    arrival_date: str | None = None
    arrival_time: str | None = None


@dataclass
class HandlingNoteGroup:
    parent: HandlingNote
    children: list[HandlingNote] = field(default_factory=list)


def case_description_narrative(raw: str | None) -> str:
    parsed = parse_intake_description(raw or "")
    return _split_inline_note(parsed.narrative)[0]


def intake_note_from_description(raw: str | None) -> str | None:
    parsed = parse_intake_description(raw or "")
    inline = _split_inline_note(parsed.narrative)[1]
    note = (parsed.branch_resolution or "").strip() or inline
    return note or None


def event_label(event_code: str, prior_codes: list[str] | None = None) -> str:
    code = (event_code or "").strip().upper()
    priors = [(p or "").strip().upper() for p in (prior_codes or [])]
    if code == "CASE_ESCALATED_TO_PUSAT" and any(p in _RE_ESCALATION_PRIOR for p in priors):
        return RE_ESCALATED_LABEL
    return EVENT_LABELS.get(code, code or "Lainnya")


def collect_handling_notes(
    description: str | None,
    entries: list[CaseHistoryEntry],
    *,
    parent_intake_note: str | None = None,
    resolution_texts: list[str | None] | None = None,
) -> list[HandlingNote]:
    seen: set[str] = set()
    for raw in resolution_texts or []:
        text = (raw or "").strip()
        if text:
            seen.add(_norm(text))

    from_history = _history_notes(entries, seen)
    from_blob = [
        row
        for row in _blob_notes(description)
        if _keep_unique(row.text, seen)
    ]
    parent = (parent_intake_note or "").strip()
    if parent and _keep_unique(parent, seen):
        from_blob.append(
            HandlingNote(
                key="blob-intake-parent",
                source="blob",
                label=INTAKE_LABEL,
                text=parent,
            )
        )
    return [*from_blob, *from_history]


def group_handling_notes(notes: list[HandlingNote]) -> list[HandlingNoteGroup]:
    groups: list[HandlingNoteGroup] = []
    intake_group: HandlingNoteGroup | None = None
    schedule_group: HandlingNoteGroup | None = None
    for note in notes:
        code = (note.event_code or "").strip().upper()
        if code == "HQ_ACCEPTED" and intake_group is not None:
            intake_group.children.append(note)
            continue
        if code == "HQ_ARRIVAL_SCHEDULED" and schedule_group is not None:
            schedule_group.children.append(
                HandlingNote(
                    key=note.key,
                    source=note.source,
                    label=RESCHEDULED_LABEL,
                    text=note.text,
                    event_code=note.event_code,
                    actor_name=note.actor_name,
                    occurred_at=note.occurred_at,
                    arrival_date=note.arrival_date,
                    arrival_time=note.arrival_time,
                )
            )
            continue
        group = HandlingNoteGroup(parent=note, children=[])
        groups.append(group)
        if code in INTAKE_PARENT_CODES:
            intake_group = group
        if code == "HQ_ARRIVAL_SCHEDULED":
            schedule_group = group
    return groups


def closed_via_hq_completion(case: CaseDTO, notes: list[HandlingNote]) -> bool:
    if (case.status or "").strip().upper() != "CLOSED":
        return False
    return any((n.event_code or "").upper() == "HQ_COMPLETED" for n in notes)


def resolution_card_text(
    case: CaseDTO,
    notes: list[HandlingNote],
) -> tuple[str, list[str]]:
    """Return (lead sentence, extra body lines) for the Resolusi block."""
    resolution: ResolutionDTO | None = case.resolution
    if resolution is not None:
        lines: list[str] = []
        head = " · ".join(
            part
            for part in (resolution.status, resolution.resolution_code)
            if (part or "").strip()
        )
        if head:
            lines.append(head)
        for label, value in (
            ("Ringkasan", resolution.summary),
            ("Detail", resolution.detail),
            ("Komentar", resolution.comment),
        ):
            text = (value or "").strip()
            if text:
                lines.append(f"{label}: {text}")
        return ("Resolusi cabang", lines)
    if closed_via_hq_completion(case, notes):
        return (HQ_CLOSED_RESOLUTION, [])
    return (NO_BRANCH_RESOLUTION, [])


def format_hq_return_note_display(text: str) -> str:
    trimmed = (text or "").strip()
    match = _HQ_RETURN_PREFIX.match(trimmed)
    if match is None:
        return text
    code, body = match.group(1), (match.group(2) or "").strip()
    label = HQ_RETURN_REASON_LABELS.get(code)
    if not label:
        return text
    return f"{label} - {body}" if body else label


def format_schedule_body(
    note: HandlingNote,
    *,
    destination_unit_id: str | None = None,
) -> str:
    lines: list[str] = []
    code = (note.event_code or "").strip().upper()
    raw_text = (note.text or "").strip()
    if code == "CASE_ESCALATION_RETURNED":
        raw_text = format_hq_return_note_display(raw_text)
    if code in {"HQ_ARRIVAL_SCHEDULED"} or note.label == RESCHEDULED_LABEL:
        slot = " ".join(
            part
            for part in ((note.arrival_date or "").strip(), (note.arrival_time or "").strip())
            if part
        )
        if slot and slot not in raw_text:
            lines.append(slot)
        dest = (destination_unit_id or "").strip()
        if dest and dest not in raw_text:
            lines.append(f"Unit tujuan: {dest}")
    if raw_text:
        lines.append(raw_text)
    return "\n".join(lines)


def _split_inline_note(text: str) -> tuple[str, str | None]:
    match = _INLINE_NOTE.search(text)
    if match is None:
        return _LEADING_DESCRIPTION.sub("", text).strip(), None
    narrative = _LEADING_DESCRIPTION.sub("", text[: match.start()]).strip()
    note = text[match.end() :].strip() or None
    return narrative, note


def _norm(text: str) -> str:
    return re.sub(r"\s+", " ", text).strip().lower()


def _keep_unique(text: str, seen: set[str]) -> bool:
    key = _norm(text)
    if not key or key in seen:
        return False
    seen.add(key)
    return True


def _blob_notes(raw: str | None) -> list[HandlingNote]:
    parsed = parse_intake_description(raw or "")
    notes: list[HandlingNote] = []
    intake = intake_note_from_description(raw)
    if intake:
        notes.append(
            HandlingNote(
                key="blob-intake",
                source="blob",
                label=INTAKE_LABEL,
                text=intake,
            )
        )
    for attr, label in BLOB_FIELDS:
        text = (getattr(parsed, attr) or "").strip()
        if not text:
            continue
        notes.append(
            HandlingNote(
                key=f"blob-{field}",
                source="blob",
                label=label,
                text=text,
            )
        )
    return notes


def _history_notes(
    entries: list[CaseHistoryEntry],
    seen: set[str],
) -> list[HandlingNote]:
    notes: list[HandlingNote] = []
    prior: list[str] = []
    for index, entry in enumerate(entries):
        code = (entry.event_code or "").strip().upper()
        if code in HISTORY_NOTE_EXCLUDED_CODES:
            prior.append(code)
            continue
        text = (entry.note or "").strip()
        if not text:
            prior.append(code)
            continue
        if not _keep_unique(text, seen):
            prior.append(code)
            continue
        notes.append(
            HandlingNote(
                key=entry.entry_id or f"history-{index}",
                source="history",
                label=event_label(code, prior),
                text=text,
                event_code=code,
                actor_name=entry.actor_name or entry.actor_id,
                occurred_at=entry.occurred_at,
                arrival_date=entry.arrival_date,
                arrival_time=entry.arrival_time,
            )
        )
        prior.append(code)
    return notes
