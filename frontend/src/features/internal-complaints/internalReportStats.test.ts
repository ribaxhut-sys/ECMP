import { describe, expect, it } from "vitest";
import {
  countByHandlingUnit,
  countByPriority,
  countByStatus,
  maxCount,
} from "./internalReportStats";
import type { InternalComplaint } from "./types";

function row(overrides: Partial<InternalComplaint>): InternalComplaint {
  return {
    id: "id",
    number: "PI-1",
    title: "t",
    category: "OTHER",
    subcategory: "",
    relatedComplaintId: null,
    relatedComplaintNumber: null,
    priority: "MEDIUM",
    status: "CREATED",
    description: "",
    chronology: "",
    impact: "",
    ownerUnitId: "UPPPD-A",
    handlingUnitId: "PUSAT",
    createdBy: "u1",
    createdByName: null,
    createdAt: "2026-08-19T00:00:00Z",
    updatedAt: null,
    closedBy: null,
    closedByName: null,
    closedAt: null,
    resolutionSummary: null,
    resolutionStatus: null,
    resolutionComment: null,
    resolutionProposedBy: null,
    resolutionProposedByName: null,
    handlingUnitAcceptance: null,
    ownerAcceptance: null,
    history: [],
    transferRequestStatus: null,
    transferRequestDestinationUnitId: null,
    transferRequestReason: null,
    transferRequestedBy: null,
    transferRequestedByName: null,
    transferRequestedAt: null,
    transferDecidedBy: null,
    transferDecidedByName: null,
    transferDecidedAt: null,
    transferDecisionReason: null,
    withdrawRequestStatus: null,
    withdrawRequestReason: null,
    withdrawRequestedBy: null,
    withdrawRequestedByName: null,
    withdrawRequestedAt: null,
    withdrawDecidedBy: null,
    withdrawDecidedByName: null,
    withdrawDecidedAt: null,
    withdrawDecisionReason: null,
    withdrawnBy: null,
    withdrawnByName: null,
    withdrawnAt: null,
    withdrawReason: null,
    completionRequestStatus: null,
    completionReturnReason: null,
    completionReturnedBy: null,
    completionReturnedByName: null,
    completionReturnedAt: null,
    ...overrides,
  };
}

describe("countByStatus", () => {
  it("zero-fills every known status and keeps declared order", () => {
    const rows = [
      row({ status: "RESOLVED" }),
      row({ status: "RESOLVED" }),
      row({ status: "CLOSED" }),
    ];
    const buckets = countByStatus(rows);
    expect(buckets.map((b) => b.key)).toEqual([
      "CREATED",
      "ASSIGNED",
      "IN_PROGRESS",
      "RESOLVED",
      "CLOSED",
      "WITHDRAWN",
    ]);
    expect(buckets.find((b) => b.key === "RESOLVED")?.count).toBe(2);
    expect(buckets.find((b) => b.key === "CLOSED")?.count).toBe(1);
    expect(buckets.find((b) => b.key === "CREATED")?.count).toBe(0);
  });
});

describe("countByPriority", () => {
  it("counts each priority and zero-fills the rest", () => {
    const rows = [row({ priority: "HIGH" }), row({ priority: "HIGH" })];
    expect(countByPriority(rows)).toEqual({
      LOW: 0,
      MEDIUM: 0,
      HIGH: 2,
      CRITICAL: 0,
    });
  });
});

describe("countByHandlingUnit", () => {
  it("sorts by volume desc, ties broken alphabetically", () => {
    const rows = [
      row({ handlingUnitId: "PUSAT" }),
      row({ handlingUnitId: "UPPPD-B" }),
      row({ handlingUnitId: "PUSAT" }),
      row({ handlingUnitId: "UPPPD-A" }),
    ];
    expect(countByHandlingUnit(rows)).toEqual([
      { unitId: "PUSAT", count: 2 },
      { unitId: "UPPPD-A", count: 1 },
      { unitId: "UPPPD-B", count: 1 },
    ]);
  });

  it("collapses Pusat sub-units into PUSAT", () => {
    const rows = [
      row({ handlingUnitId: "PUSAT-CRO" }),
      row({ handlingUnitId: "PUSAT" }),
    ];
    expect(countByHandlingUnit(rows)).toEqual([{ unitId: "PUSAT", count: 2 }]);
  });
});

describe("maxCount", () => {
  it("returns 0 for an empty list", () => {
    expect(maxCount([])).toBe(0);
  });
  it("returns the largest count", () => {
    expect(maxCount([{ count: 1 }, { count: 5 }, { count: 3 }])).toBe(5);
  });
});
