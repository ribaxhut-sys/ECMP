import { describe, expect, it } from "vitest";
import { createEmptyComplaintForm } from "./createComplaintForm";
import {
  MAX_INTAKE_CASES,
  buildIntakeCaseForms,
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
    expect(forms[0]?.priority).toBe("HIGH");
    expect(forms[0]?.destinationUnitId).toBe("UPPPD-X");
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
