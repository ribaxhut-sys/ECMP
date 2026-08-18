import { describe, expect, it } from "vitest";
import {
  escalationTotal,
  operationalHealthFromRate,
  reportHeadlineCounts,
  resolutionBuckets,
  resolutionRatePercent,
} from "./reportSummaryStats";

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

describe("resolutionRatePercent", () => {
  it("returns null without totals", () => {
    expect(resolutionRatePercent(null)).toBeNull();
    expect(resolutionRatePercent({ total: 0, open: 0, closed: 0 })).toBeNull();
  });

  it("rounds closed / total", () => {
    expect(
      resolutionRatePercent({ total: 10, open: 3, closed: 7 }),
    ).toBe(70);
  });
});

describe("resolutionBuckets", () => {
  it("returns null for empty rows", () => {
    expect(resolutionBuckets(null)).toBeNull();
    expect(resolutionBuckets([])).toBeNull();
  });

  it("groups waiting, escalated, and resolved into mutually exclusive slices", () => {
    expect(
      resolutionBuckets([
        { status: "NEW", count: 1 },
        { status: "ASSIGNED", count: 2 },
        { status: "PENDING", count: 1 },
        { status: "IN_PROGRESS", count: 3 },
        { status: "ESCALATED", count: 4 },
        { status: "RESOLVED", count: 5 },
        { status: "CLOSED", count: 2 },
      ]),
    ).toEqual({
      resolved: 7,
      waiting: 1,
      escalated: 4,
      escalationApproved: 2,
      escalationScheduled: 1,
      inProgress: 3,
    });
  });
});

describe("escalationTotal", () => {
  it("sums pending, approved, and HQ-scheduled escalations", () => {
    expect(
      escalationTotal({
        resolved: 0,
        waiting: 0,
        escalated: 3,
        escalationApproved: 2,
        escalationScheduled: 3,
        inProgress: 0,
      }),
    ).toBe(8);
  });

  it("returns 0 for null buckets", () => {
    expect(escalationTotal(null)).toBe(0);
  });
});

describe("operationalHealthFromRate", () => {
  it("maps thresholds", () => {
    expect(operationalHealthFromRate(null)).toBeNull();
    expect(operationalHealthFromRate(75)?.labelKey).toBe("healthy");
    expect(operationalHealthFromRate(45)?.labelKey).toBe("attention");
    expect(operationalHealthFromRate(10)?.labelKey).toBe("critical");
  });
});

