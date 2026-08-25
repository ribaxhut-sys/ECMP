import { describe, expect, it } from "vitest";
import type { CmBatch1ComplaintResponse } from "@/lib/api";
import type { CmCaseSummary } from "@/lib/api/cmCase";
import {
  buildFollowUpRows,
  filterFollowUpRows,
  followUpRowHref,
  isActiveCaseStatus,
} from "./followUpRows";

function complaint(
  overrides: Partial<CmBatch1ComplaintResponse> = {},
): CmBatch1ComplaintResponse {
  return {
    complaintId: "cx-1",
    complaintNumber: "TAB-0001",
    status: "REGISTERED",
    customerId: "cust-1",
    caseCreated: true,
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

describe("buildFollowUpRows", () => {
  it("shows caseNumber as the row identity and carries subject for the list column", () => {
    const rows = buildFollowUpRows({
      complaints: [complaint()],
      allCases: [caseSummary({ subject: "Koreksi SPPT" })],
    });
    expect(rows).toHaveLength(1);
    expect(rows[0].number).toBe("CASE-2026-000001");
    expect(rows[0].subject).toBe("Koreksi SPPT");
    expect(rows[0].parentComplaintId).toBe("cx-1");
    expect(rows[0].parentComplaintNumber).toBe("TAB-0001");
    expect(rows[0].isUnread).toBe(false);
  });

  it("marks a Pusat follow-up row unread from the parent receipt", () => {
    const rows = buildFollowUpRows({
      complaints: [
        complaint({
          pusatUnread: true,
          intakeDisposition: "HQ_SCHEDULED",
          hqAcceptedAt: "2026-08-17T10:00:00Z",
        }),
      ],
      allCases: [caseSummary({ isRead: true, escalatedToPusat: true })],
      audience: "pusat",
    });
    expect(rows).toHaveLength(1);
    expect(rows[0].isUnread).toBe(true);
  });

  it("marks a Cabang follow-up row unread from Case isRead", () => {
    const rows = buildFollowUpRows({
      complaints: [complaint({ pusatUnread: false })],
      allCases: [caseSummary({ isRead: false })],
      audience: "cabang",
    });
    expect(rows).toHaveLength(1);
    expect(rows[0].isUnread).toBe(true);
  });

  it("omits complaints that have no visible Case", () => {
    const rows = buildFollowUpRows({
      complaints: [complaint({ caseCreated: false })],
      allCases: [],
    });
    expect(rows).toHaveLength(0);
  });

  it("does not emit a second complaint row when HQ has accepted the escalation", () => {
    const rows = buildFollowUpRows({
      complaints: [
        complaint({
          intakeDisposition: "ESCALATE_APPROVED",
          hqAcceptedAt: "2026-08-17T10:00:00Z",
        }),
      ],
      allCases: [caseSummary({ status: "CREATED" })],
    });
    expect(rows).toHaveLength(1);
    expect(rows[0].number).toBe("CASE-2026-000001");
    expect(rows[0].statusKey).toBe("hqAcceptedUnscheduled");
  });

  it("labels HQ_SCHEDULED as taxpayer arrival and copies the slot + handler", () => {
    const rows = buildFollowUpRows({
      complaints: [
        complaint({
          intakeDisposition: "HQ_SCHEDULED",
          hqArrivalDate: "2026-08-20",
          hqArrivalTime: "09:30",
        }),
      ],
      allCases: [
        caseSummary({
          status: "CREATED",
          handlingClaimedByName: "Dewi Hidayat",
        }),
      ],
    });
    expect(rows[0].statusKey).toBe("hqScheduled");
    expect(rows[0].hqArrivalDate).toBe("2026-08-20");
    expect(rows[0].hqArrivalTime).toBe("09:30");
    expect(rows[0].handlerName).toBe("Dewi Hidayat");
  });

  it("keeps one row per Case when a complaint has several Cases", () => {
    const rows = buildFollowUpRows({
      complaints: [complaint()],
      allCases: [
        caseSummary({ caseId: "case-a", caseNumber: "CASE-A", status: "IN_PROGRESS" }),
        caseSummary({ caseId: "case-b", caseNumber: "CASE-B", status: "CREATED" }),
      ],
    });
    expect(rows.map((r) => r.number).sort()).toEqual(["CASE-A", "CASE-B"]);
    expect(rows.every((r) => r.parentComplaintNumber === "TAB-0001")).toBe(true);
  });

  it("drops terminal-status cases from the default view", () => {
    const rows = buildFollowUpRows({
      complaints: [complaint()],
      allCases: [
        caseSummary({ status: "CLOSED" }),
        caseSummary({ status: "CANCELLED", caseId: "case-2" }),
      ],
    });
    expect(rows).toHaveLength(0);
  });

  it("sorts by inherited complaint buckets then newest Case first", () => {
    const rows = buildFollowUpRows({
      complaints: [
        complaint({
          complaintId: "cx-approval",
          complaintNumber: "TAB-A",
          intakeDisposition: "ESCALATE_PENDING_APPROVAL",
        }),
        complaint({
          complaintId: "cx-hq",
          complaintNumber: "TAB-H",
          intakeDisposition: "ESCALATE_APPROVED",
        }),
        complaint({
          complaintId: "cx-returned",
          complaintNumber: "TAB-R",
          intakeDisposition: "RETURNED_TO_BRANCH",
        }),
        complaint({
          complaintId: "cx-w",
          complaintNumber: "TAB-W",
        }),
      ],
      allCases: [
        caseSummary({
          caseId: "case-approval",
          complaintId: "cx-approval",
          status: "CREATED",
        }),
        caseSummary({
          caseId: "case-hq",
          complaintId: "cx-hq",
          status: "IN_PROGRESS",
        }),
        caseSummary({
          caseId: "case-returned",
          complaintId: "cx-returned",
          status: "ASSIGNED",
        }),
        caseSummary({
          caseId: "case-working",
          complaintId: "cx-w",
          status: "IN_PROGRESS",
        }),
      ],
    });
    expect(rows.map((r) => `${r.caseId}:${r.statusKey}`)).toEqual([
      "case-approval:awaitingApproval",
      "case-hq:hqAwaitingAccept",
      "case-returned:returnedToBranch",
      "case-working:caseWorking",
    ]);
  });

  it("drops never-handled intake for the Pusat audience (Pengaduan owns it)", () => {
    const rows = buildFollowUpRows({
      complaints: [
        complaint({
          intakeDisposition: "ESCALATE_APPROVED",
        }),
      ],
      allCases: [
        caseSummary({
          status: "IN_PROGRESS",
          escalatedToPusat: true,
        }),
      ],
      audience: "pusat",
    });
    expect(rows).toHaveLength(0);
  });

  it("keeps accepted Pusat work for the Pusat audience", () => {
    const rows = buildFollowUpRows({
      complaints: [
        complaint({
          intakeDisposition: "ESCALATE_APPROVED",
          hqAcceptedAt: "2026-08-17T10:00:00Z",
        }),
      ],
      allCases: [
        caseSummary({
          status: "IN_PROGRESS",
          escalatedToPusat: true,
        }),
      ],
      audience: "pusat",
    });
    expect(rows).toHaveLength(1);
    expect(rows[0].statusKey).toBe("hqAcceptedUnscheduled");
  });

  it("orders same-bucket rows by newest createdAt first", () => {
    const rows = buildFollowUpRows({
      complaints: [],
      allCases: [
        caseSummary({
          caseId: "older",
          status: "CREATED",
          createdAt: "2026-08-01T00:00:00Z",
        }),
        caseSummary({
          caseId: "newer",
          status: "ASSIGNED",
          createdAt: "2026-08-05T00:00:00Z",
        }),
      ],
    });
    expect(rows.map((r) => r.caseId)).toEqual(["newer", "older"]);
  });
});

describe("filterFollowUpRows", () => {
  const stage = (row: { statusKey: string }) =>
    row.statusKey === "hqScheduled" ? "Jadwal kedatangan WP" : "Sedang dikerjakan di cabang";

  it("matches case number, subject, CRO, and stage label", () => {
    const rows = buildFollowUpRows({
      complaints: [
        complaint({
          intakeDisposition: "HQ_SCHEDULED",
          hqAcceptedAt: "2026-08-17T10:00:00Z",
          hqArrivalDate: "2026-08-20",
          hqArrivalTime: "09:00",
        }),
      ],
      allCases: [
        caseSummary({
          subject: "Koreksi SPPT",
          handlingClaimedByName: "Siti CRO",
          escalatedToPusat: true,
          status: "IN_PROGRESS",
        }),
      ],
    });
    expect(filterFollowUpRows(rows, "CASE-2026", stage)).toHaveLength(1);
    expect(filterFollowUpRows(rows, "sppt", stage)).toHaveLength(1);
    expect(filterFollowUpRows(rows, "siti", stage)).toHaveLength(1);
    expect(filterFollowUpRows(rows, "jadwal", stage)).toHaveLength(1);
    expect(filterFollowUpRows(rows, "tidak-ada", stage)).toHaveLength(0);
  });

  it("returns all rows when the query is blank", () => {
    const rows = buildFollowUpRows({
      complaints: [complaint()],
      allCases: [caseSummary({ subject: "A" }), caseSummary({ caseId: "c2", caseNumber: "CASE-2", subject: "B" })],
    });
    expect(filterFollowUpRows(rows, "  ", stage)).toHaveLength(2);
  });
});

describe("followUpRowHref (DEC-025 CM door)", () => {
  it("opens Case work on the Case detail route", () => {
    expect(followUpRowHref({ caseId: "case-1" })).toBe("/complaints/cm/cases/case-1");
  });
});
