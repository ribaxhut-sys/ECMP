import { describe, expect, it } from "vitest";
import type { CmCaseHistoryEntry } from "@/lib/api";
import {
  caseDescriptionNarrative,
  collectCaseHandlingNotes,
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
          eventCode: "CASE_HANDLING_UNIT_ACCEPTED",
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
    expect(notes[2]?.labelKey).toBe("eventHandlingUnitAccepted");
  });

  it("does not duplicate a blob catatan that already appears on the timeline", () => {
    const notes = collectCaseHandlingNotes("Keluhan\n\n---\nCatatan:\nOK unit", [
      entry({
        entryId: "2",
        eventCode: "CASE_HANDLING_UNIT_ACCEPTED",
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
});
