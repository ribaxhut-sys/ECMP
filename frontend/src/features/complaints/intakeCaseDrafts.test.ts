import { describe, expect, it } from "vitest";
import { createEmptyComplaintForm } from "./createComplaintForm";
import {
  MAX_INTAKE_CASES,
  buildIntakeCaseForms,
  buildIntakeDecisionRows,
  intakeMayEscalateToPusat,
  parseIntakeCaseAction,
  sanitizeExtraCaseDrafts,
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
        { id: "b", description: "Uraian case 2" },
      ],
      "UPPPD-X",
    );
    expect(forms).toHaveLength(2);
    expect(forms[0]?.description).toBe("Uraian case 1");
    expect(forms[1]?.description).toBe("Uraian case 2");
    expect(forms[1]?.subject).toBe("Uraian case 2");
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
});
