import { describe, expect, it, beforeEach } from "vitest";
import {
  stashCaseCreatePrefill,
  takeCaseCreatePrefill,
} from "./caseCreatePrefill";
import { mergeCreateCaseForm } from "./caseForms";

describe("caseCreatePrefill", () => {
  beforeEach(() => {
    sessionStorage.clear();
  });

  it("stores and consumes matching prefill once", () => {
    stashCaseCreatePrefill({
      complaintId: "c-1",
      caseType: "BILLING",
      category: "BILLING",
      subject: "Late bill",
      description: "Details",
      priority: "HIGH",
      destinationUnitId: "unit-1",
    });
    const first = takeCaseCreatePrefill("c-1");
    expect(first?.subject).toBe("Late bill");
    expect(takeCaseCreatePrefill("c-1")).toBeNull();
  });

  it("ignores prefill for another complaint", () => {
    stashCaseCreatePrefill({
      complaintId: "c-1",
      caseType: "X",
      category: "",
      subject: "S",
      description: "D",
      priority: "MEDIUM",
      destinationUnitId: "",
    });
    expect(takeCaseCreatePrefill("c-2")).toBeNull();
  });
});

describe("mergeCreateCaseForm", () => {
  it("prefills subject description priority and unit", () => {
    const merged = mergeCreateCaseForm({
      caseType: "SERVICE",
      subject: "Hello",
      description: "World",
      priority: "LOW",
      destinationUnitId: "u-9",
    });
    expect(merged.caseType).toBe("SERVICE");
    expect(merged.subject).toBe("Hello");
    expect(merged.description).toBe("World");
    expect(merged.priority).toBe("LOW");
    expect(merged.destinationUnitId).toBe("u-9");
  });
});
