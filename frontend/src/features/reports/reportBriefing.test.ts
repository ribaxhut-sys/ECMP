import { describe, expect, it } from "vitest";
import {
  countDelta,
  previousRateFromSummary,
  rateDelta,
  reportBriefingFacts,
  signedCount,
} from "./reportBriefing";

const summary = {
  total: 39,
  byStatus: [
    { status: "CLOSED" as const, count: 30 },
    { status: "IN_PROGRESS" as const, count: 3 },
    { status: "escalateApproved" as const, count: 4 },
    { status: "escalateScheduled" as const, count: 2 },
    { status: "waitingAssignment" as const, count: 0 },
  ],
};

describe("reportBriefingFacts", () => {
  it("returns null without a summary", () => {
    expect(reportBriefingFacts(null)).toBeNull();
  });

  it("reads closed, open, and live escalation", () => {
    expect(reportBriefingFacts(summary)).toEqual({
      total: 39,
      closed: 30,
      open: 9,
      escalated: 6,
      waiting: 0,
    });
  });
});

describe("countDelta", () => {
  it("returns null without a previous value", () => {
    expect(countDelta(10, null)).toBeNull();
    expect(countDelta(10, undefined)).toBeNull();
  });

  it("subtracts previous from current", () => {
    expect(countDelta(39, 32)).toBe(7);
    expect(countDelta(10, 12)).toBe(-2);
    expect(signedCount(7)).toBe("+7");
    expect(signedCount(-2)).toBe("-2");
    expect(signedCount(0)).toBe("0");
  });
});

describe("rateDelta", () => {
  it("compares whole-percent resolution rates", () => {
    expect(rateDelta(77, 70)).toBe(7);
    expect(rateDelta(null, 70)).toBeNull();
    expect(
      previousRateFromSummary({
        total: 10,
        byStatus: [{ status: "CLOSED", count: 7 }],
      }),
    ).toBe(70);
  });
});
