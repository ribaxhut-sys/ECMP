import { describe, expect, it } from "vitest";
import {
  branchPerformanceRows,
  escalationTotal,
  highestQueueBranch,
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
      waiting: 2,
      escalated: 4,
      escalationApproved: 2,
      inProgress: 3,
    });
  });
});

describe("escalationTotal", () => {
  it("sums pending and already-approved escalations", () => {
    expect(
      escalationTotal({
        resolved: 0,
        waiting: 0,
        escalated: 3,
        escalationApproved: 2,
        inProgress: 0,
      }),
    ).toBe(5);
  });

  it("returns 0 for null buckets", () => {
    expect(escalationTotal(null)).toBe(0);
  });
});

describe("branchPerformanceRows", () => {
  it("ranks top / middle / lowest by volume", () => {
    const rows = branchPerformanceRows([
      {
        branchId: "b1",
        branchCode: "JKT",
        branchName: "Jakarta",
        total: 10,
        open: 0,
        closed: 10,
        caseTotal: 10,
        caseOpen: 0,
        caseClosed: 10,
      },
      {
        branchId: "b2",
        branchCode: "BDG",
        branchName: "Bandung",
        total: 7,
        open: 0,
        closed: 7,
        caseTotal: 7,
        caseOpen: 0,
        caseClosed: 7,
      },
      {
        branchId: "b3",
        branchCode: "SBY",
        branchName: "Surabaya",
        total: 4,
        open: 0,
        closed: 4,
        caseTotal: 4,
        caseOpen: 0,
        caseClosed: 4,
      },
    ]);

    expect(rows).toEqual([
      {
        key: "b1",
        name: "Jakarta",
        total: 10,
        share: 100,
        rank: "top",
      },
      {
        key: "b2",
        name: "Bandung",
        total: 7,
        share: 70,
        rank: "middle",
      },
      {
        key: "b3",
        name: "Surabaya",
        total: 4,
        share: 40,
        rank: "lowest",
      },
    ]);
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

describe("highestQueueBranch", () => {
  it("returns the busiest branch", () => {
    expect(
      highestQueueBranch([
        {
          branchId: "b1",
          branchCode: "JKT",
          branchName: "Jakarta",
          total: 3,
          open: 1,
          closed: 2,
          caseTotal: 3,
          caseOpen: 1,
          caseClosed: 2,
        },
        {
          branchId: "b2",
          branchCode: "BDG",
          branchName: "Bandung",
          total: 9,
          open: 2,
          closed: 7,
          caseTotal: 9,
          caseOpen: 2,
          caseClosed: 7,
        },
      ])?.branchName,
    ).toBe("Bandung");
  });
});
