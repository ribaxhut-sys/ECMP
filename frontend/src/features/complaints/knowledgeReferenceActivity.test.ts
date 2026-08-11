import { describe, expect, it } from "vitest";
import { isKnowledgeReferenceActive } from "./knowledgeReferenceActivity";

describe("isKnowledgeReferenceActive", () => {
  const now = new Date("2026-08-11T00:00:00Z");

  it("returns true for ACTIVE without effective bounds", () => {
    expect(
      isKnowledgeReferenceActive(
        { status: "ACTIVE", effectiveFrom: null, effectiveTo: null },
        now,
      ),
    ).toBe(true);
  });

  it("returns false for ARCHIVED / DRAFT", () => {
    expect(
      isKnowledgeReferenceActive(
        { status: "ARCHIVED", effectiveFrom: null, effectiveTo: null },
        now,
      ),
    ).toBe(false);
    expect(
      isKnowledgeReferenceActive(
        { status: "DRAFT", effectiveFrom: null, effectiveTo: null },
        now,
      ),
    ).toBe(false);
  });

  it("returns false when outside the effective window", () => {
    expect(
      isKnowledgeReferenceActive(
        {
          status: "ACTIVE",
          effectiveFrom: null,
          effectiveTo: "2026-01-01T00:00:00Z",
        },
        now,
      ),
    ).toBe(false);
    expect(
      isKnowledgeReferenceActive(
        {
          status: "ACTIVE",
          effectiveFrom: "2026-12-01T00:00:00Z",
          effectiveTo: null,
        },
        now,
      ),
    ).toBe(false);
  });
});
