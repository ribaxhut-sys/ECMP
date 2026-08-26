import { describe, expect, it } from "vitest";
import type { CmBatch1ComplaintResponse, CmCaseSummary } from "@/lib/api";
import type { CmBatch1ComplaintListRow } from "./cmBatch1ComplaintListRows";
import {
  closedArchiveIntakeDisposition,
  closedArchivePathLabelKey,
  keepClosedArchiveRow,
} from "./closedArchiveRows";

function complaint(
  overrides: Partial<CmBatch1ComplaintResponse> = {},
): CmBatch1ComplaintResponse {
  return {
    complaintId: "cmp-1",
    complaintNumber: "CMTAB-2608-0001",
    status: "CLOSED",
    customerId: "cust-1",
    caseCreated: true,
    replayed: false,
    ...overrides,
  };
}

function row(
  overrides: Partial<CmBatch1ComplaintListRow> &
    Pick<CmBatch1ComplaintListRow, "casesState">,
): CmBatch1ComplaintListRow {
  return {
    key: "cmp-1",
    complaint: complaint(),
    caseItem: null,
    ...overrides,
  };
}

function caseItem(overrides: Partial<CmCaseSummary> = {}): CmCaseSummary {
  return {
    caseId: "case-1",
    caseNumber: "TAB-2608-0001",
    complaintId: "cmp-1",
    status: "CLOSED",
    ...overrides,
  };
}

describe("closedArchiveIntakeDisposition", () => {
  it("pins Pusat to HQ_CLOSED and Cabang to COMPLETED", () => {
    expect(closedArchiveIntakeDisposition(true)).toBe("HQ_CLOSED");
    expect(closedArchiveIntakeDisposition(false)).toBe("COMPLETED");
  });
});

describe("closedArchivePathLabelKey", () => {
  it("labels HQ close vs branch close", () => {
    expect(closedArchivePathLabelKey("HQ_CLOSED")).toBe("tagHqCompleted");
    expect(closedArchivePathLabelKey("BRANCH_CLOSED")).toBe("tagBranchClosed");
  });
});

describe("keepClosedArchiveRow", () => {
  it("keeps closed and resolved Cases, drops cancelled", () => {
    expect(
      keepClosedArchiveRow({
        key: "a",
        complaint: complaint(),
        caseItem: caseItem({ status: "CLOSED" }),
        casesState: "ready",
      }),
    ).toBe(true);
    expect(
      keepClosedArchiveRow({
        key: "b",
        complaint: complaint(),
        caseItem: caseItem({ status: "RESOLVED" }),
        casesState: "ready",
      }),
    ).toBe(true);
    expect(
      keepClosedArchiveRow({
        key: "c",
        complaint: complaint(),
        caseItem: caseItem({ status: "CANCELLED" }),
        casesState: "ready",
      }),
    ).toBe(false);
  });

  it("keeps walk-away parents that never created a Case", () => {
    expect(keepClosedArchiveRow(row({ casesState: "empty" }))).toBe(true);
  });
});
