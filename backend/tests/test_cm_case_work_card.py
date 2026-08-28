"""Work-card projection for API-539 — mirrors frontend caseHandlingNotes.test.ts."""

from __future__ import annotations

from datetime import UTC, datetime

from app.modules.cm_case.api.schemas import CaseHistoryEntry
from app.modules.cm_case.application.case_work_card import (
    HQ_CLOSED_RESOLUTION,
    NO_BRANCH_RESOLUTION,
    RESCHEDULED_LABEL,
    HandlingNote,
    case_description_narrative,
    collect_handling_notes,
    format_hq_return_note_display,
    format_schedule_body,
    group_handling_notes,
    resolution_card_text,
)
from app.modules.cm_case.application.dto import CaseDTO, ResolutionDTO


def _entry(
    entry_id: str,
    event_code: str,
    *,
    note: str | None = None,
    actor_name: str = "Ayu",
) -> CaseHistoryEntry:
    return CaseHistoryEntry(
        entryId=entry_id,
        eventCode=event_code,
        eventType=event_code,
        occurredAt=datetime(2026, 8, 18, 3, 0, tzinfo=UTC),
        actorName=actor_name,
        note=note,
    )


def _case(**overrides: object) -> CaseDTO:
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


def _note(
    key: str,
    label: str,
    *,
    text: str | None = None,
    event_code: str | None = None,
) -> HandlingNote:
    return HandlingNote(
        key=key,
        source="history",
        label=label,
        text=text or key,
        event_code=event_code,
    )


def test_narrative_keeps_plain_description() -> None:
    assert case_description_narrative("Queue too long") == "Queue too long"


def test_narrative_strips_section_catatan() -> None:
    assert (
        case_description_narrative("Keluhan mesin\n\n---\nCatatan:\nSudah dijelaskan")
        == "Keluhan mesin"
    )


def test_narrative_strips_inline_deskripsi_catatan() -> None:
    assert (
        case_description_narrative(
            "Deskripsi:\nKeluhan A\n\nCatatan:\nSudah diinfokan"
        )
        == "Keluhan A"
    )


def test_collect_keeps_blob_catatan_not_on_timeline() -> None:
    notes = collect_handling_notes(
        "Keluhan\n\n---\nCatatan:\nSudah dijelaskan\n\n---\nAlasan eskalasi:\nPerlu Pusat",
        [
            _entry("2", "CASE_STATUS_CHANGED", note="OK unit"),
            _entry("3", "HQ_ARRIVAL_SCHEDULED", note="Bawa dokumen asli"),
        ],
    )
    assert [row.text for row in notes] == [
        "Sudah dijelaskan",
        "Perlu Pusat",
        "OK unit",
        "Bawa dokumen asli",
    ]
    assert notes[0].source == "blob"
    assert notes[2].source == "history"
    assert notes[2].label == "Status Case diubah"


def test_collect_does_not_duplicate_blob_already_on_timeline() -> None:
    notes = collect_handling_notes(
        "Keluhan\n\n---\nCatatan:\nOK unit",
        [_entry("2", "CASE_STATUS_CHANGED", note="OK unit")],
    )
    assert len(notes) == 1
    assert notes[0].source == "history"
    assert notes[0].text == "OK unit"


def test_collect_skips_history_without_note() -> None:
    notes = collect_handling_notes("Queue too long", [_entry("1", "CASE_CREATED")])
    assert notes == []


def test_collect_surfaces_parent_intake_when_case_row_lacks_it() -> None:
    notes = collect_handling_notes(
        "Queue too long",
        [],
        parent_intake_note="Sudah diinfokan ke wajib pajak",
    )
    assert len(notes) == 1
    assert notes[0].key == "blob-intake-parent"
    assert notes[0].text == "Sudah diinfokan ke wajib pajak"
    assert notes[0].label == "Catatan"


def test_collect_does_not_duplicate_parent_already_on_case_blob() -> None:
    notes = collect_handling_notes(
        "Keluhan\n\n---\nCatatan:\nSudah diinfokan ke wajib pajak",
        [],
        parent_intake_note="Sudah diinfokan ke wajib pajak",
    )
    assert len(notes) == 1
    assert notes[0].key == "blob-intake"


def test_collect_omits_resolve_close_accept_and_dedupes() -> None:
    body = (
        "Vivamus sagittis lacus vel augue laoreet rutrum faucibus dolor auctor.\n"
        "Dilanjutkan sesuai SOP"
    )
    notes = collect_handling_notes(
        "Deskripsi saja",
        [
            _entry("1", "CASE_CREATED", note=body),
            _entry("2", "CASE_RESOLVED", note=body),
            _entry("3", "CASE_OWNER_ACCEPTED", note=body),
            _entry("4", "CASE_CLOSED", note=body),
        ],
    )
    assert len(notes) == 1
    assert notes[0].text == body
    assert notes[0].label == "Case dibuat"


def test_collect_suppresses_text_already_on_resolusi() -> None:
    body = "Dilanjutkan sesuai SOP"
    notes = collect_handling_notes(
        "Deskripsi saja",
        [
            _entry("1", "CASE_CREATED", note=body),
            _entry("2", "CASE_RESOLVED", note=body),
            _entry("3", "CASE_CLOSED", note=body),
        ],
        resolution_texts=[body, body],
    )
    assert notes == []


def test_collect_keeps_distinct_operational_notes() -> None:
    notes = collect_handling_notes(
        "Keluhan",
        [
            _entry("1", "CASE_CREATED", note="Catatan buat case"),
            _entry("2", "CASE_HANDLING_UNIT_ACCEPTED", note="OK unit"),
            _entry("3", "CASE_RESOLVED", note="Selesai di cabang"),
            _entry("4", "CASE_CLOSED", note="Selesai di cabang"),
        ],
    )
    assert [row.text for row in notes] == ["Catatan buat case"]


def test_collect_labels_later_escalate_as_re_escalation() -> None:
    notes = collect_handling_notes(
        "Keluhan",
        [
            _entry("1", "CASE_ESCALATED_TO_PUSAT", note="Perlu bantuan Pusat"),
            _entry("2", "CASE_ESCALATION_RETURNED", note="Bukan kewenangan Pusat"),
            _entry("3", "CASE_ESCALATED_TO_PUSAT", note="Dokumen sudah dilengkapi"),
        ],
    )
    assert [row.label for row in notes] == [
        "Diajukan ke Pusat",
        "Dikembalikan Pusat",
        "Diajukan kembali ke Pusat",
    ]
    assert notes[2].text == "Dokumen sudah dilengkapi"


def test_group_nests_hq_accept_and_reschedule() -> None:
    groups = group_handling_notes(
        [
            _note("1", "Case dibuat", event_code="CASE_CREATED", text="Catatan buat case"),
            _note("2", "Diterima Pusat", event_code="HQ_ACCEPTED", text="Diterima di Pusat"),
            _note("3", "Kedatangan dijadwalkan", event_code="HQ_ARRIVAL_SCHEDULED", text="Slot pertama"),
            _note("4", "Kedatangan dijadwalkan", event_code="HQ_ARRIVAL_SCHEDULED", text="Slot kedua"),
        ]
    )
    assert len(groups) == 2
    assert groups[0].parent.key == "1"
    assert [row.key for row in groups[0].children] == ["2"]
    assert groups[1].parent.key == "3"
    assert [row.label for row in groups[1].children] == [RESCHEDULED_LABEL]
    assert groups[1].children[0].text == "Slot kedua"


def test_group_keeps_hq_accept_top_level_without_parent() -> None:
    groups = group_handling_notes(
        [_note("2", "Diterima Pusat", event_code="HQ_ACCEPTED", text="Diterima di Pusat")]
    )
    assert len(groups) == 1
    assert groups[0].parent.key == "2"
    assert groups[0].children == []


def test_group_nests_hq_accept_under_escalate() -> None:
    groups = group_handling_notes(
        [
            _note("e", "Diajukan ke Pusat", event_code="CASE_ESCALATED_TO_PUSAT", text="Perlu Pusat"),
            _note("a", "Diterima Pusat", event_code="HQ_ACCEPTED", text="OK"),
        ]
    )
    assert len(groups) == 1
    assert [row.key for row in groups[0].children] == ["a"]


def test_resolution_hq_closed_uses_work_card_copy() -> None:
    notes = collect_handling_notes(
        "BPHTB",
        [_entry("h", "HQ_COMPLETED", note="WP hadir, selesai di Pusat")],
    )
    lead, extra = resolution_card_text(_case(status="CLOSED"), notes)
    assert lead == HQ_CLOSED_RESOLUTION
    assert extra == []


def test_resolution_open_case_without_row() -> None:
    lead, extra = resolution_card_text(_case(), [])
    assert lead == NO_BRANCH_RESOLUTION
    assert extra == []


def test_resolution_branch_row() -> None:
    lead, extra = resolution_card_text(
        _case(
            resolution=ResolutionDTO(
                resolution_id="r1",
                resolution_code="SOP_DONE",
                summary="Dilanjutkan sesuai SOP",
                status="ACCEPTED",
                comment="Dilanjutkan sesuai SOP",
            )
        ),
        [],
    )
    assert lead == "Resolusi cabang"
    assert extra[0] == "ACCEPTED · SOP_DONE"
    assert "Ringkasan: Dilanjutkan sesuai SOP" in extra


def test_format_hq_return_note_display() -> None:
    assert (
        format_hq_return_note_display("[INCOMPLETE_CHRONOLOGY] Lengkapi kronologi")
        == "Kronologi tidak lengkap - Lengkapi kronologi"
    )


def test_format_schedule_body_adds_slot_and_unit() -> None:
    body = format_schedule_body(
        HandlingNote(
            key="s",
            source="history",
            label="Kedatangan dijadwalkan",
            text="Bawa dokumen asli",
            event_code="HQ_ARRIVAL_SCHEDULED",
            arrival_date="2026-08-20",
            arrival_time="10:00",
        ),
        destination_unit_id="UNIT-HQ",
    )
    assert "20-08-2026, 10:00" in body
    assert "2026-08-20 10:00" not in body
    assert "Unit tujuan: UNIT-HQ" in body
    assert "Bawa dokumen asli" in body
