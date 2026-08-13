import { describe, expect, it } from "vitest";
import type { CmBatch1ComplaintResponse } from "@/lib/api";
import type { CmCaseSummary } from "@/lib/api/cmCase";
import {
  buildFollowUpRows,
  isActiveCaseStatus,
  isFollowUpComplaint,
} from "./followUpRows";

function complaint(
  overrides: Partial<CmBatch1ComplaintResponse> = {},
): CmBatch1ComplaintResponse {
  return {
    complaintId: "cx-1",
    complaintNumber: "TAB-0001",
    status: "REGISTERED",
    customerId: "cust-1",
    caseCreated: false,
    replayed: false,
    createdAt: "2026-08-01T00:00:00Z",
    ...overrides,
  } as CmBatch1ComplaintResponse;
}

function caseSummary(
  overrides: Partial<Omit<CmCaseSummary, "status">> & { status?: string } = {},
): CmCaseSummary {
  return {
    caseId: "case-1",
    caseNumber: "CASE-2026-000001",
    complaintId: "cx-1",
    status: "CREATED",
    createdAt: "2026-08-01T00:00:00Z",
    ...overrides,
  } as CmCaseSummary;
}

describe("isActiveCaseStatus", () => {
  it("excludes terminal statuses", () => {
    expect(isActiveCaseStatus("CLOSED")).toBe(false);
    expect(isActiveCaseStatus("RESOLVED")).toBe(false);
    expect(isActiveCaseStatus("CANCELLED")).toBe(false);
  });

  it("includes the Mode A active subset", () => {
    expect(isActiveCaseStatus("CREATED")).toBe(true);
    expect(isActiveCaseStatus("ASSIGNED")).toBe(true);
    expect(isActiveCaseStatus("IN_PROGRESS")).toBe(true);
  });

  it("includes statuses beyond the Mode A subset when the API returns them", () => {
    expect(isActiveCaseStatus("ESCALATED")).toBe(true);
    expect(isActiveCaseStatus("PENDING")).toBe(true);
  });
});

describe("isFollowUpComplaint", () => {
  it("excludes CLOSED complaints", () => {
    expect(
      isFollowUpComplaint(complaint({ status: "CLOSED" }), false),
    ).toBe(false);
  });

  it("excludes BRANCH_CLOSED disposition", () => {
    expect(
      isFollowUpComplaint(
        complaint({ intakeDisposition: "BRANCH_CLOSED" }),
        false,
      ),
    ).toBe(false);
  });

  it("includes REGISTERED with no visible case and no disposition", () => {
    expect(isFollowUpComplaint(complaint(), false)).toBe(true);
  });

  it("includes IN_PROGRESS with no visible case (DEC-025)", () => {
    expect(
      isFollowUpComplaint(complaint({ status: "IN_PROGRESS" }), false),
    ).toBe(true);
  });

  it("excludes REGISTERED when a case is already visible and no active disposition", () => {
    expect(isFollowUpComplaint(complaint(), true)).toBe(false);
  });

  it("includes REGISTERED with an active HQ intake disposition even if a case exists", () => {
    expect(
      isFollowUpComplaint(
        complaint({ intakeDisposition: "ESCALATE_PENDING_APPROVAL" }),
        true,
      ),
    ).toBe(true);
    expect(
      isFollowUpComplaint(
        complaint({ intakeDisposition: "ESCALATE_APPROVED" }),
        false,
      ),
    ).toBe(true);
    expect(
      isFollowUpComplaint(
        complaint({ intakeDisposition: "HQ_SCHEDULED" }),
        false,
      ),
    ).toBe(true);
    expect(
      isFollowUpComplaint(
        complaint({ intakeDisposition: "RETURNED_TO_BRANCH" }),
        false,
      ),
    ).toBe(true);
  });

  it("excludes rejected/cancelled escalation dispositions with a visible case", () => {
    expect(
      isFollowUpComplaint(
        complaint({ intakeDisposition: "ESCALATE_REJECTED" }),
        true,
      ),
    ).toBe(false);
  });
});

describe("buildFollowUpRows", () => {
  it("always gives Case rows their own caseNumber and a separate parent complaint column", () => {
    const rows = buildFollowUpRows({
      complaints: [complaint()],
      allCases: [caseSummary()],
    });
    const caseRow = rows.find((r) => r.kind === "case")!;
    expect(caseRow.number).toBe("CASE-2026-000001");
    expect(caseRow.parentComplaintId).toBe("cx-1");
    expect(caseRow.parentComplaintNumber).toBe("TAB-0001");
  });

  it("omits a complaint row when an active case already exists and no active disposition", () => {
    const rows = buildFollowUpRows({
      complaints: [complaint()],
      allCases: [caseSummary()],
    });
    expect(rows.some((r) => r.kind === "complaint")).toBe(false);
  });

  it("keeps the complaint row when no case is visible yet", () => {
    const rows = buildFollowUpRows({
      complaints: [complaint()],
      allCases: [],
    });
    const complaintRow = rows.find((r) => r.kind === "complaint")!;
    expect(complaintRow.number).toBe("TAB-0001");
    expect(complaintRow.parentComplaintId).toBeNull();
  });

  it("drops terminal-status cases from the default view", () => {
    const rows = buildFollowUpRows({
      complaints: [],
      allCases: [caseSummary({ status: "CLOSED" }), caseSummary({ status: "CANCELLED", caseId: "case-2" })],
    });
    expect(rows).toHaveLength(0);
  });

  it("sorts by the fixed bucket order: awaiting approval, HQ path, returned, case working/new, no handling", () => {
    const rows = buildFollowUpRows({
      complaints: [
        complaint({
          complaintId: "cx-approval",
          complaintNumber: "TAB-A",
          intakeDisposition: "ESCALATE_PENDING_APPROVAL",
        }),
        complaint({
          complaintId: "cx-returned",
          complaintNumber: "TAB-R",
          intakeDisposition: "RETURNED_TO_BRANCH",
        }),
        complaint({
          complaintId: "cx-none",
          complaintNumber: "TAB-N",
        }),
      ],
      allCases: [
        caseSummary({ caseId: "case-hq", complaintId: "cx-hq", status: "ESCALATED" }),
        caseSummary({ caseId: "case-working", complaintId: "cx-w", status: "IN_PROGRESS" }),
      ],
    });
    const kinds = rows.map((r) => `${r.kind}:${r.statusKey}`);
    expect(kinds).toEqual([
      "complaint:awaitingApproval",
      "case:hqPath",
      "complaint:returnedToBranch",
      "case:caseWorking",
      "complaint:noHandling",
    ]);
  });

  it("orders same-bucket rows by newest createdAt first", () => {
    const rows = buildFollowUpRows({
      complaints: [],
      allCases: [
        caseSummary({ caseId: "older", status: "CREATED", createdAt: "2026-08-01T00:00:00Z" }),
        caseSummary({ caseId: "newer", status: "ASSIGNED", createdAt: "2026-08-05T00:00:00Z" }),
      ],
    });
    expect(rows.map((r) => r.caseId)).toEqual(["newer", "older"]);
  });
});
