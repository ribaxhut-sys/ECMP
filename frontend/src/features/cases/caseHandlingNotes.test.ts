import { describe, expect, it } from "vitest";
import type { CmCaseHistoryEntry } from "@/lib/api";
import {
  caseDescriptionNarrative,
  collectCaseHandlingNotes,
  groupCaseHandlingNotes,
  type CaseHandlingNote,
} from "./caseHandlingNotes";

function entry(
  overrides: Partial<CmCaseHistoryEntry> &
    Pick<CmCaseHistoryEntry, "entryId" | "eventCode">,
): CmCaseHistoryEntry {
  return {
    eventType: overrides.eventCode,
    occurredAt: "2026-08-18T03:00:00Z",
    actorName: "Ayu",
    ...overrides,
  };
}

describe("caseDescriptionNarrative", () => {
  it("keeps a plain description", () => {
    expect(caseDescriptionNarrative("Queue too long")).toBe("Queue too long");
  });

  it("strips --- Catatan from the narrative", () => {
    expect(
      caseDescriptionNarrative("Keluhan mesin\n\n---\nCatatan:\nSudah dijelaskan"),
    ).toBe("Keluhan mesin");
  });

  it("strips inline Deskripsi/Catatan labels", () => {
    expect(
      caseDescriptionNarrative("Deskripsi:\nKeluhan A\n\nCatatan:\nSudah diinfokan"),
    ).toBe("Keluhan A");
  });
});

describe("collectCaseHandlingNotes", () => {
  it("lists timeline notes in order and keeps blob catatan that is not on the timeline", () => {
    const notes = collectCaseHandlingNotes(
      "Keluhan\n\n---\nCatatan:\nSudah dijelaskan\n\n---\nAlasan eskalasi:\nPerlu Pusat",
      [
        entry({
          entryId: "2",
          eventCode: "CASE_STATUS_CHANGED",
          note: "OK unit",
        }),
        entry({
          entryId: "3",
          eventCode: "HQ_ARRIVAL_SCHEDULED",
          note: "Bawa dokumen asli",
        }),
      ],
    );
    expect(notes.map((row) => row.text)).toEqual([
      "Sudah dijelaskan",
      "Perlu Pusat",
      "OK unit",
      "Bawa dokumen asli",
    ]);
    expect(notes[0]?.source).toBe("blob");
    expect(notes[2]?.source).toBe("history");
    expect(notes[2]?.labelKey).toBe("eventCaseStatusChanged");
  });

  it("does not duplicate a blob catatan that already appears on the timeline", () => {
    const notes = collectCaseHandlingNotes("Keluhan\n\n---\nCatatan:\nOK unit", [
      entry({
        entryId: "2",
        eventCode: "CASE_STATUS_CHANGED",
        note: "OK unit",
      }),
    ]);
    expect(notes).toHaveLength(1);
    expect(notes[0]?.source).toBe("history");
    expect(notes[0]?.text).toBe("OK unit");
  });

  it("skips history rows without a note", () => {
    const notes = collectCaseHandlingNotes("Queue too long", [
      entry({ entryId: "1", eventCode: "CASE_CREATED" }),
    ]);
    expect(notes).toEqual([]);
  });

  it("surfaces parent intake Catatan when the Case row does not have it", () => {
    const notes = collectCaseHandlingNotes("Queue too long", [], {
      parentIntakeNote: "Sudah diinfokan ke wajib pajak",
    });
    expect(notes).toHaveLength(1);
    expect(notes[0]?.key).toBe("blob-intake-parent");
    expect(notes[0]?.text).toBe("Sudah diinfokan ke wajib pajak");
    expect(notes[0]?.labelKey).toBe("handlingNoteIntake");
  });

  it("does not duplicate parent Catatan already on the Case blob", () => {
    const notes = collectCaseHandlingNotes(
      "Keluhan\n\n---\nCatatan:\nSudah diinfokan ke wajib pajak",
      [],
      { parentIntakeNote: "Sudah diinfokan ke wajib pajak" },
    );
    expect(notes).toHaveLength(1);
    expect(notes[0]?.key).toBe("blob-intake");
  });

  it("omits resolve/close/owner-accept notes and dedupes identical bodies", () => {
    const body =
      "Vivamus sagittis lacus vel augue laoreet rutrum faucibus dolor auctor.\nDilanjutkan sesuai SOP";
    const notes = collectCaseHandlingNotes("Deskripsi saja", [
      entry({ entryId: "1", eventCode: "CASE_CREATED", note: body }),
      entry({ entryId: "2", eventCode: "CASE_RESOLVED", note: body }),
      entry({ entryId: "3", eventCode: "CASE_OWNER_ACCEPTED", note: body }),
      entry({ entryId: "4", eventCode: "CASE_CLOSED", note: body }),
    ]);
    expect(notes).toHaveLength(1);
    expect(notes[0]?.text).toBe(body);
    expect(notes[0]?.labelKey).toBe("eventCaseCreated");
  });

  it("suppresses Catatan text that already appears on Resolusi", () => {
    const body = "Dilanjutkan sesuai SOP";
    const notes = collectCaseHandlingNotes(
      "Deskripsi saja",
      [
        entry({ entryId: "1", eventCode: "CASE_CREATED", note: body }),
        entry({ entryId: "2", eventCode: "CASE_RESOLVED", note: body }),
        entry({ entryId: "3", eventCode: "CASE_CLOSED", note: body }),
      ],
      { resolutionTexts: [body, body] },
    );
    expect(notes).toEqual([]);
  });

  it("keeps distinct operational notes after excluding outcome events", () => {
    const notes = collectCaseHandlingNotes("Keluhan", [
      entry({
        entryId: "1",
        eventCode: "CASE_CREATED",
        note: "Catatan buat case",
      }),
      entry({
        entryId: "2",
        eventCode: "CASE_HANDLING_UNIT_ACCEPTED",
        note: "OK unit",
      }),
      entry({
        entryId: "3",
        eventCode: "CASE_RESOLVED",
        note: "Selesai di cabang",
      }),
      entry({
        entryId: "4",
        eventCode: "CASE_CLOSED",
        note: "Selesai di cabang",
      }),
    ]);
    expect(notes.map((row) => row.text)).toEqual(["Catatan buat case"]);
  });
});

describe("groupCaseHandlingNotes", () => {
  function note(
    overrides: Partial<CaseHandlingNote> & Pick<CaseHandlingNote, "key" | "labelKey">,
  ): CaseHandlingNote {
    return {
      source: "history",
      text: overrides.text ?? overrides.key,
      ...overrides,
    };
  }

  it("nests HQ accept under case created and later slots under the first schedule", () => {
    const groups = groupCaseHandlingNotes([
      note({
        key: "1",
        labelKey: "eventCaseCreated",
        eventCode: "CASE_CREATED",
        text: "Catatan buat case",
      }),
      note({
        key: "2",
        labelKey: "eventHqAccepted",
        eventCode: "HQ_ACCEPTED",
        text: "Diterima di Pusat",
      }),
      note({
        key: "3",
        labelKey: "eventHqScheduled",
        eventCode: "HQ_ARRIVAL_SCHEDULED",
        text: "Slot pertama",
      }),
      note({
        key: "4",
        labelKey: "eventHqScheduled",
        eventCode: "HQ_ARRIVAL_SCHEDULED",
        text: "Slot kedua",
      }),
    ]);
    expect(groups).toHaveLength(2);
    expect(groups[0]?.parent.key).toBe("1");
    expect(groups[0]?.children.map((row) => row.key)).toEqual(["2"]);
    expect(groups[1]?.parent.key).toBe("3");
    expect(groups[1]?.children.map((row) => row.labelKey)).toEqual([
      "eventHqRescheduled",
    ]);
    expect(groups[1]?.children[0]?.text).toBe("Slot kedua");
  });

  it("keeps HQ accept top-level when there is no create/escalate parent", () => {
    const groups = groupCaseHandlingNotes([
      note({
        key: "2",
        labelKey: "eventHqAccepted",
        eventCode: "HQ_ACCEPTED",
        text: "Diterima di Pusat",
      }),
    ]);
    expect(groups).toHaveLength(1);
    expect(groups[0]?.parent.key).toBe("2");
    expect(groups[0]?.children).toEqual([]);
  });

  it("nests HQ accept under escalate-to-HQ when that is the intake parent", () => {
    const groups = groupCaseHandlingNotes([
      note({
        key: "e",
        labelKey: "eventCaseEscalatedToPusat",
        eventCode: "CASE_ESCALATED_TO_PUSAT",
        text: "Perlu Pusat",
      }),
      note({
        key: "a",
        labelKey: "eventHqAccepted",
        eventCode: "HQ_ACCEPTED",
        text: "OK",
      }),
    ]);
    expect(groups).toHaveLength(1);
    expect(groups[0]?.children.map((row) => row.key)).toEqual(["a"]);
  });
});
