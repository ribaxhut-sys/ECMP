import { describe, expect, it } from "vitest";
import { deriveContextLevel } from "./deriveContextLevel";

describe("deriveContextLevel", () => {
  it("returns 1 for normal open complaint", () => {
    expect(
      deriveContextLevel({ status: "IN_PROGRESS", priority: "MEDIUM" }),
    ).toBe(1);
  });

  it("returns 3 for escalated", () => {
    expect(
      deriveContextLevel({ status: "ESCALATED", priority: "MEDIUM" }),
    ).toBe(3);
  });

  it("returns 4 for critical priority", () => {
    expect(
      deriveContextLevel({ status: "ASSIGNED", priority: "CRITICAL" }),
    ).toBe(4);
  });

  it("returns 4 when SLA breached", () => {
    expect(
      deriveContextLevel({
        status: "IN_PROGRESS",
        priority: "LOW",
        slaBreached: true,
      }),
    ).toBe(4);
  });

  it("does not invent level 2 without repeat signal", () => {
    expect(
      deriveContextLevel({ status: "PENDING", priority: "HIGH" }),
    ).toBe(1);
  });
});
