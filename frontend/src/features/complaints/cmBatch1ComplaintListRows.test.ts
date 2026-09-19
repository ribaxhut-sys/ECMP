import { describe, expect, it } from "vitest";
import {
  expandComplaintsToCaseRows,
  type CmBatch1ComplaintListCases,
} from "./cmBatch1ComplaintListRows";
import type { CmBatch1ComplaintResponse, CmCaseSummary } from "@/lib/api";

function complaint(
  overrides: Partial<CmBatch1ComplaintResponse> = {},
): CmBatch1ComplaintResponse {
  return {
    complaintId: "cmp-1",
    complaintNumber: "CMTAB-2608-0001",
    status: "IN_PROGRESS",
    customerId: "cust-1",
    caseCreated: true,
    replayed: false,
    ...overrides,
  };
}

function caseItem(overrides: Partial<CmCaseSummary> = {}): CmCaseSummary {
  return {
    caseId: "case-1",
    caseNumber: "TAB-2608-0001",
    complaintId: "cmp-1",
    status: "IN_PROGRESS",
    ...overrides,
  };
}

describe("expandComplaintsToCaseRows", () => {
  it("keeps one empty row when a complaint has no Case yet", () => {
    const rows = expandComplaintsToCaseRows([complaint({ caseCreated: false })], {
      "cmp-1": [],
    });
    expect(rows).toHaveLength(1);
    expect(rows[0]?.key).toBe("cmp-1");
    expect(rows[0]?.caseItem).toBeNull();
    expect(rows[0]?.casesState).toBe("empty");
  });

  it("emits one row per Case and keeps the parent complaint", () => {
    const parent = complaint();
    const casesByComplaint: Record<string, CmBatch1ComplaintListCases> = {
      "cmp-1": [
        caseItem({ caseId: "a", caseNumber: "TAB-2608-0001" }),
        caseItem({
          caseId: "b",
          caseNumber: "TAB-2608-0002",
          escalatedToPusat: true,
        }),
      ],
    };
    const rows = expandComplaintsToCaseRows([parent], casesByComplaint);
    expect(rows.map((row) => row.caseItem?.caseNumber)).toEqual([
      "TAB-2608-0001",
      "TAB-2608-0002",
    ]);
    expect(rows.every((row) => row.casesState === "ready")).toBe(true);
    expect(rows[1]?.complaint.complaintNumber).toBe("CMTAB-2608-0001");
  });

  it("marks loading and error without claiming there is no Case", () => {
    const parent = complaint();
    expect(
      expandComplaintsToCaseRows([parent], { "cmp-1": "loading" })[0]
        ?.casesState,
    ).toBe("loading");
    expect(
      expandComplaintsToCaseRows([parent], { "cmp-1": "error" })[0]?.casesState,
    ).toBe("error");
  });
});
