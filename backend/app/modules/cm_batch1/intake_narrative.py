"""Structured intake narrative markers (Batch-1 history for branch + HQ).

Officer intake and supervisor decisions write one `description` blob with
sections so Supervisor and later Head Office share the same history.
"""

from __future__ import annotations

from dataclasses import dataclass

SECTION_INTAKE_NOTE = "Catatan"
SECTION_BRANCH_RESOLUTION = "Penyelesaian"  # legacy intake-note label
SECTION_ESCALATION_REASON = "Alasan eskalasi"
SECTION_ESCALATION_REQUEST = "Ajuan eskalasi"
SECTION_SUPERVISOR_NOTE = "Catatan Supervisor"
SECTION_REJECTION_NOTE = "Penolakan Eskalasi"
SECTION_CANCEL_NOTE = "Batalkan Eskalasi"
# Legacy label (pre-rename); still parsed for existing rows.
SECTION_CANCEL_NOTE_LEGACY = "Batal Eskalasi"
SECTION_HQ_ACCEPTANCE = "Penerimaan Pusat"
SECTION_HQ_ARRIVAL = "Jadwal kedatangan"
SECTION_HQ_RETURN = "Pengembalian Pusat"

_SECTION_SEP = "\n\n---\n"


@dataclass(frozen=True, slots=True)
class ParsedIntakeNarrative:
    narrative: str
    branch_resolution: str | None = None
    escalation_reason: str | None = None
    escalation_request_note: str | None = None
    supervisor_note: str | None = None
    rejection_note: str | None = None
    cancellation_note: str | None = None
    hq_acceptance_note: str | None = None
    hq_arrival_note: str | None = None
    hq_return_note: str | None = None


def parse_intake_description(raw: str) -> ParsedIntakeNarrative:
    text = (raw or "").strip()
    if not text:
        return ParsedIntakeNarrative(narrative="")

    parts = text.split(_SECTION_SEP)
    narrative = parts[0].strip()
    branch_resolution: str | None = None
    escalation_reason: str | None = None
    escalation_request_note: str | None = None
    supervisor_note: str | None = None
    rejection_note: str | None = None
    cancellation_note: str | None = None
    hq_acceptance_note: str | None = None
    hq_arrival_note: str | None = None
    hq_return_note: str | None = None

    for part in parts[1:]:
        chunk = part.strip()
        if chunk.startswith(f"{SECTION_INTAKE_NOTE}:"):
            branch_resolution = chunk.split(":", 1)[1].strip() or None
        elif chunk.startswith(f"{SECTION_BRANCH_RESOLUTION}:"):
            # Legacy "Penyelesaian:" — same slot as Catatan (prefer Catatan if both).
            if branch_resolution is None:
                branch_resolution = chunk.split(":", 1)[1].strip() or None
        elif chunk.startswith(f"{SECTION_ESCALATION_REASON}:"):
            escalation_reason = chunk.split(":", 1)[1].strip() or None
        elif chunk.startswith(f"{SECTION_ESCALATION_REQUEST}:"):
            escalation_request_note = chunk.split(":", 1)[1].strip() or None
        elif chunk.startswith(f"{SECTION_SUPERVISOR_NOTE}:"):
            supervisor_note = chunk.split(":", 1)[1].strip() or None
        elif chunk.startswith(f"{SECTION_REJECTION_NOTE}:"):
            rejection_note = chunk.split(":", 1)[1].strip() or None
        elif chunk.startswith(f"{SECTION_CANCEL_NOTE}:"):
            cancellation_note = chunk.split(":", 1)[1].strip() or None
        elif chunk.startswith(f"{SECTION_CANCEL_NOTE_LEGACY}:"):
            if cancellation_note is None:
                cancellation_note = chunk.split(":", 1)[1].strip() or None
        elif chunk.startswith(f"{SECTION_HQ_ACCEPTANCE}:"):
            hq_acceptance_note = chunk.split(":", 1)[1].strip() or None
        elif chunk.startswith(f"{SECTION_HQ_ARRIVAL}:"):
            hq_arrival_note = chunk.split(":", 1)[1].strip() or None
        elif chunk.startswith(f"{SECTION_HQ_RETURN}:"):
            hq_return_note = chunk.split(":", 1)[1].strip() or None

    return ParsedIntakeNarrative(
        narrative=narrative,
        branch_resolution=branch_resolution,
        escalation_reason=escalation_reason,
        escalation_request_note=escalation_request_note,
        supervisor_note=supervisor_note,
        rejection_note=rejection_note,
        cancellation_note=cancellation_note,
        hq_acceptance_note=hq_acceptance_note,
        hq_arrival_note=hq_arrival_note,
        hq_return_note=hq_return_note,
    )


def append_history_section(raw: str, section_label: str, note: str) -> str:
    """Append or replace a named history section (idempotent for that label)."""
    base = (raw or "").rstrip()
    cleaned_note = (note or "").strip()
    label = (section_label or "").strip()
    if not cleaned_note or not label:
        return base
    prefix = f"{label}:"
    legacy_prefixes = (
        {f"{SECTION_CANCEL_NOTE_LEGACY}:"}
        if label == SECTION_CANCEL_NOTE
        else set()
    )
    parsed_parts = base.split(_SECTION_SEP) if base else [""]
    kept: list[str] = []
    for i, part in enumerate(parsed_parts):
        chunk = part.strip()
        if i == 0:
            kept.append(chunk)
            continue
        if chunk.startswith(prefix) or any(
            chunk.startswith(p) for p in legacy_prefixes
        ):
            continue
        kept.append(chunk)
    kept.append(f"{prefix}\n{cleaned_note}")
    return _SECTION_SEP.join(p for p in kept if p)


def append_supervisor_note(raw: str, note: str) -> str:
    return append_history_section(raw, SECTION_SUPERVISOR_NOTE, note)


def append_rejection_note(raw: str, note: str) -> str:
    return append_history_section(raw, SECTION_REJECTION_NOTE, note)


def append_cancellation_note(raw: str, note: str) -> str:
    return append_history_section(raw, SECTION_CANCEL_NOTE, note)


def append_hq_acceptance_note(raw: str, note: str) -> str:
    return append_history_section(raw, SECTION_HQ_ACCEPTANCE, note)


def append_hq_arrival_note(raw: str, note: str) -> str:
    return append_history_section(raw, SECTION_HQ_ARRIVAL, note)


def append_hq_return_note(raw: str, note: str) -> str:
    return append_history_section(raw, SECTION_HQ_RETURN, note)


_RE_ESCALATE_REQUEST_NOTE = (
    "Menunggu persetujuan Supervisor/Manager cabang untuk eskalasi ke Pusat "
    "(ajuan ulang). Riwayat batalkan/tolak sebelumnya tetap tersimpan."
)


def append_re_escalation_reason(raw: str, note: str) -> str:
    """Accumulate alasan eskalasi and refresh pending marker; keep cancel/reject history.

    Prior ``Batalkan Eskalasi`` / ``Penolakan Eskalasi`` / ``Catatan Supervisor``
    sections are left intact (append-only across labels).

    Do not embed ``---`` inside the alasan value — that is the section separator.
    """
    cleaned = (note or "").strip()
    if not cleaned:
        return (raw or "").rstrip()
    parsed = parse_intake_description(raw)
    if parsed.escalation_reason:
        combined = (
            f"{parsed.escalation_reason.rstrip()}\n\n[Ajuan ulang]\n{cleaned}"
        )
    else:
        combined = cleaned
    updated = append_history_section(raw, SECTION_ESCALATION_REASON, combined)
    return append_history_section(
        updated, SECTION_ESCALATION_REQUEST, _RE_ESCALATE_REQUEST_NOTE
    )


def has_branch_resolution(raw: str) -> bool:
    """True when intake note (Catatan or legacy Penyelesaian) is present."""
    parsed = parse_intake_description(raw)
    return bool(parsed.branch_resolution)


def has_intake_note(raw: str) -> bool:
    """Alias — Catatan wajib saat Daftarkan / Selesai di cabang."""
    return has_branch_resolution(raw)


def has_escalation_reason(raw: str) -> bool:
    parsed = parse_intake_description(raw)
    return bool(parsed.escalation_reason)
