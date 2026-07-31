import { describe, expect, it } from "vitest";
import { reportHeadlineCounts } from "./reportSummaryStats";

describe("reportHeadlineCounts", () => {
  it("returns null for missing summary", () => {
    expect(reportHeadlineCounts(null)).toBeNull();
    expect(reportHeadlineCounts(undefined)).toBeNull();
  });

  it("splits open vs resolved/closed", () => {
    expect(
      reportHeadlineCounts({
        total: 10,
        byStatus: [
          { status: "NEW", count: 2 },
          { status: "IN_PROGRESS", count: 3 },
          { status: "RESOLVED", count: 4 },
          { status: "CLOSED", count: 1 },
        ],
      }),
    ).toEqual({ total: 10, open: 5, closed: 5 });
  });
});
