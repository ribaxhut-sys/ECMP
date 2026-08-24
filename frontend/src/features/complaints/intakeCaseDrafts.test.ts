import { describe, expect, it } from "vitest";
import { createEmptyComplaintForm } from "./createComplaintForm";
import {
  MAX_INTAKE_CASES,
  buildIntakeCaseForms,
  buildIntakeDecisionRows,
  extraIntakeCaseIssues,
  filledExtraCaseDrafts,
  intakeDecisionLockSummary,
  intakeMayEscalateToPusat,
  parseIntakeCaseAction,
  sanitizeExtraCaseDrafts,
  validateIntakeCaseRow,
} from "./intakeCaseDrafts";

describe("intakeCaseDrafts", () => {
  it("keeps at most 4 extra drafts", () => {
    const raw = Array.from({ length: 8 }, (_, i) => ({
      id: `e${i}`,
      description: `d${i}`,
    }));
    expect(sanitizeExtraCaseDrafts(raw)).toHaveLength(4);
  });

  it("builds Case 1 from complaint description then extras", () => {
    const values = {
      ...createEmptyComplaintForm({ channel: "BRANCH" }),
      subject: "Mesin error",
      description: "Uraian case 1",
      category: "GENERAL",
      priority: "HIGH" as const,
    };
    const forms = buildIntakeCaseForms(
      values,
      [
        { id: "a", description: "  " },
        { id: "b", subject: "Case 2 mesin", description: "Uraian case 2" },
      ],
      "UPPPD-X",
    );
    expect(forms).toHaveLength(2);
    expect(forms[0]?.description).toBe("Uraian case 1");
    expect(forms[1]?.description).toBe("Uraian case 2");
    expect(forms[1]?.subject).toBe("Case 2 mesin");
    expect(forms[0]?.priority).toBe("HIGH");
    expect(forms[0]?.destinationUnitId).toBe("UPPPD-X");
  });

  it("keeps per-Case action and priority on extras", () => {
    const values = {
      ...createEmptyComplaintForm({ channel: "BRANCH" }),
      subject: "Mesin error",
      description: "Uraian case 1",
      priority: "LOW" as const,
    };
    const rows = buildIntakeDecisionRows(
      values,
      [
        {
          id: "b",
          description: "Uraian case 2",
          priority: "HIGH",
          note: "Selesai di cabang",
          action: "close",
        },
      ],
      "register",
    );
    expect(rows).toHaveLength(2);
    expect(rows[0]?.action).toBe("register");
    expect(rows[1]?.action).toBe("close");
    expect(rows[1]?.priority).toBe("HIGH");
  });

  it("keeps escalate as a per-Case action (API-520 after create)", () => {
    expect(parseIntakeCaseAction("escalate")).toBe("escalate");
    expect(parseIntakeCaseAction("close")).toBe("close");
    expect(parseIntakeCaseAction("nope")).toBe("register");
    const values = {
      ...createEmptyComplaintForm({ channel: "BRANCH" }),
      subject: "Mesin error",
      description: "Uraian case 1",
    };
    const rows = buildIntakeDecisionRows(
      values,
      [
        {
          id: "b",
          description: "Uraian case 2",
          note: "Tidak selesai di cabang, perlu Pusat.",
          action: "escalate",
        },
      ],
      "register",
    );
    expect(rows[1]?.action).toBe("escalate");
  });

  it("offers escalate-to-Pusat only when recording unit is a branch", () => {
    expect(intakeMayEscalateToPusat("JKT01")).toBe(true);
    expect(intakeMayEscalateToPusat("UPPPD-X")).toBe(true);
    expect(intakeMayEscalateToPusat(null)).toBe(true);
    expect(intakeMayEscalateToPusat("PUSAT")).toBe(false);
    expect(intakeMayEscalateToPusat("PUSAT-CRO")).toBe(false);
  });

  it("caps total cases at BQ-003 max", () => {
    const values = {
      ...createEmptyComplaintForm({ channel: "BRANCH" }),
      subject: "S",
      description: "C1",
    };
    const extras = Array.from({ length: 8 }, (_, i) => ({
      id: `e${i}`,
      description: `extra ${i}`,
    }));
    expect(buildIntakeCaseForms(values, extras, "U")).toHaveLength(
      MAX_INTAKE_CASES,
    );
  });

  it("round-trips locked flags on extra drafts", () => {
    const sanitized = sanitizeExtraCaseDrafts([
      { id: "b", description: "Uraian case 2", locked: true, action: "escalate" },
    ]);
    expect(sanitized[0]?.locked).toBe(true);
    const values = {
      ...createEmptyComplaintForm({ channel: "BRANCH" }),
      subject: "Mesin error",
      description: "Uraian case 1",
    };
    const rows = buildIntakeDecisionRows(values, sanitized, "close", true);
    expect(rows[0]?.locked).toBe(true);
    expect(rows[0]?.action).toBe("close");
    expect(rows[1]?.locked).toBe(true);
    expect(rows[1]?.action).toBe("escalate");
  });

  it("validates note length for escalate and summarizes locks", () => {
    const row = {
      id: "primary",
      n: 1,
      subject: "Subjek",
      description: "Uraian",
      priority: "HIGH",
      note: "pendek",
      action: "escalate" as const,
    };
    expect(validateIntakeCaseRow(row)).toBe("escalateShort");
    expect(
      validateIntakeCaseRow({ ...row, note: "Tidak selesai di cabang, perlu Pusat." }),
    ).toBeNull();
    const summary = intakeDecisionLockSummary([
      { ...row, locked: true, action: "register" },
      { ...row, id: "e2", n: 2, locked: false, action: "escalate" },
    ]);
    expect(summary).toMatchObject({
      total: 2,
      locked: 1,
      escalate: 1,
      requiresLock: true,
      allLocked: false,
    });
    expect(intakeDecisionLockSummary([{ ...row, action: "register" }]).requiresLock).toBe(
      true,
    );
  });

  it("drops blank extra Case cards and requires both description and note when either is filled", () => {
    expect(
      filledExtraCaseDrafts([
        { id: "empty", description: "  ", note: "" },
        { id: "subject-only", subject: "Case 2", description: "", note: "" },
        { id: "note-only", description: "", note: "Sudah diinfokan." },
      ]),
    ).toEqual([
      { id: "subject-only", subject: "Case 2", description: "", note: "" },
      { id: "note-only", description: "", note: "Sudah diinfokan." },
    ]);
    expect(
      extraIntakeCaseIssues([
        { id: "empty", description: "", note: "" },
        { id: "subject-only", subject: "Case 2", description: "", note: "" },
        { id: "note-only", description: "", note: "Sudah diinfokan." },
        { id: "ok", description: "Uraian", note: "Catatan cabang" },
        {
          id: "full",
          subject: "Case 2",
          description: "Uraian",
          note: "Catatan cabang",
        },
      ]),
    ).toEqual([
      {
        id: "subject-only",
        description: "required",
        note: "required",
      },
      { id: "note-only", subject: "required", description: "required" },
      { id: "ok", subject: "required" },
    ]);
  });
});
