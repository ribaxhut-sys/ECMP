import { describe, expect, it } from "vitest";
import { CM_BATCH1_OPEN_HREF } from "@/features/complaints/cmBatch1ListFilters";
import {
  actorInitials,
  aggregateComplaintActivitySummaries,
  branchOptionLabel,
  buildCriticalAlerts,
  buildQueueHealthRows,
  CRITICAL_ALERT_VISIBLE_LIMIT,
  dashboardEmptyWorkCta,
  resolveSystemHealth,
  sortBranchesHeadOfficeFirst,
  visibleAlertSlice,
} from "./dashboardUtils";

describe("branchOptionLabel", () => {
  it("drops the code when it is just the name reformatted", () => {
    expect(
      branchOptionLabel({ code: "UPPPD-PASAR-MINGGU", name: "UPPPD Pasar Minggu" }),
    ).toBe("UPPPD Pasar Minggu");
  });

  it("keeps both when the code carries distinct information", () => {
    expect(
      branchOptionLabel({ code: "JKT-01", name: "Cabang Jakarta Pusat" }),
    ).toBe("JKT-01 — Cabang Jakarta Pusat");
  });
});

describe("sortBranchesHeadOfficeFirst", () => {
  it("puts Pusat first, then the rest alphabetically by name", () => {
    const branches = [
      { code: "UPPPD-SENEN", name: "UPPPD Senen" },
      { code: "JKT-01", name: "Cabang Jakarta Pusat" },
      { code: "PUSAT", name: "Kantor Pusat" },
      { code: "UPPPD-GAMBIR", name: "UPPPD Gambir" },
    ];

    expect(sortBranchesHeadOfficeFirst(branches).map((b) => b.code)).toEqual([
      "PUSAT",
      "JKT-01",
      "UPPPD-GAMBIR",
      "UPPPD-SENEN",
    ]);
  });

  it("does not mutate the input array", () => {
    const branches = [
      { code: "B", name: "Beta" },
      { code: "A", name: "Alfa" },
    ];
    const sorted = sortBranchesHeadOfficeFirst(branches);
    expect(sorted).not.toBe(branches);
    expect(branches.map((b) => b.code)).toEqual(["B", "A"]);
  });
});

describe("buildQueueHealthRows", () => {
  const byStatus = [
    { status: "NEW" as const, count: 4 },
    { status: "ESCALATED" as const, count: 4 },
    { status: "CLOSED" as const, count: 6 },
    { status: "PENDING" as const, count: 0 },
    { status: "IN_PROGRESS" as const, count: 0 },
  ];

  it("shows assignment + escalation bars from CM Aggregate", () => {
    const rows = buildQueueHealthRows({
      byStatus,
      waitingAssignmentHref:
        "/complaints?status=REGISTERED&intakeDisposition=UNESCALATED",
      escalationHref:
        "/complaints?intakeDisposition=ESCALATE_PENDING_APPROVAL",
    });

    expect(rows.map((row) => row.id)).toEqual([
      "waiting-assignment",
      "waiting-escalation",
    ]);
    expect(rows[0]?.count).toBe(4);
    expect(rows[1]?.count).toBe(4);
    expect(rows[1]?.labelKey).toBe("waitingEscalationApproval");
  });
});

describe("dashboardEmptyWorkCta (DEC-026)", () => {
  it("sends officers to the CM open list", () => {
    expect(dashboardEmptyWorkCta()).toEqual({
      href: CM_BATCH1_OPEN_HREF,
      labelKey: "goToComplaints",
    });
  });
});

describe("buildCriticalAlerts", () => {
  it("lists critical SLA alerts before attention alerts", () => {
    const alerts = buildCriticalAlerts({
      breached: 18,
      assignmentBreached: 17,
      resolutionBreached: 16,
      escalated: 4,
      escalationHref:
        "/complaints?intakeDisposition=ESCALATE_PENDING_APPROVAL",
    });

    expect(alerts.map((alert) => alert.id)).toEqual([
      "sla-overall",
      "sla-assignment",
      "sla-resolution",
      "escalation",
    ]);
    expect(alerts.map((alert) => alert.tone)).toEqual([
      "critical",
      "critical",
      "attention",
      "attention",
    ]);
  });
});

describe("actorInitials", () => {
  it("uses three letters from a two-word name (first + first two of last)", () => {
    expect(actorInitials("Dedi Harianto")).toBe("DHA");
    expect(actorInitials("Eko Lestari")).toBe("ELE");
  });

  it("uses the first three letters of a single name", () => {
    expect(actorInitials("Elena")).toBe("ELE");
  });

  it("uses the first letter of the first three words", () => {
    expect(actorInitials("Muhammad Ali Akbar")).toBe("MAA");
  });

  it("falls back for empty values", () => {
    expect(actorInitials("")).toBe("?");
    expect(actorInitials(null)).toBe("?");
  });
});

describe("resolveSystemHealth", () => {
  it("flags attention from Aggregate queue even when SLA clocks are deferred", () => {
    expect(
      resolveSystemHealth({
        loading: false,
        error: false,
        sla: null,
        waitingAssignment: 1,
        escalatePending: 4,
      }),
    ).toBe("attention");
  });

  it("is healthy when Aggregate queue is clear and clocks are deferred", () => {
    expect(
      resolveSystemHealth({
        loading: false,
        error: false,
        sla: null,
        waitingAssignment: 0,
        escalatePending: 0,
      }),
    ).toBe("healthy");
  });
});

describe("visibleAlertSlice", () => {
  const items = [1, 2, 3, 4, 5];

  it("caps at the visible limit until expanded", () => {
    expect(visibleAlertSlice(items, false)).toEqual([1, 2, 3, 4]);
    expect(visibleAlertSlice(items, false).length).toBe(
      CRITICAL_ALERT_VISIBLE_LIMIT,
    );
  });

  it("returns the full list when expanded", () => {
    expect(visibleAlertSlice(items, true)).toEqual(items);
  });
});

describe("aggregateComplaintActivitySummaries", () => {
  it("collapses events for the same complaint into one row", () => {
    const summaries = aggregateComplaintActivitySummaries([
      {
        eventType: "complaint.closed",
        complaintNumber: "TAD-2608-0002",
        timestamp: "2026-08-14T04:22:00.000Z",
        actor: "Ahmad Santoso",
      },
      {
        eventType: "complaint.created",
        complaintNumber: "TAD-2608-0002",
        timestamp: "2026-08-14T04:05:00.000Z",
        actor: "Ahmad Santoso",
      },
      {
        eventType: "complaint.created",
        complaintNumber: "TAB-2608-0001",
        timestamp: "2026-08-14T03:50:00.000Z",
        actor: "Budi",
      },
    ]);

    expect(summaries.map((row) => row.complaintNumber)).toEqual([
      "TAD-2608-0002",
      "TAB-2608-0001",
    ]);
    expect(summaries[0]).toMatchObject({
      lastTimestamp: "2026-08-14T04:22:00.000Z",
      lastEventType: "complaint.closed",
      actor: "Ahmad Santoso",
    });
    expect(summaries[1]).toMatchObject({
      lastTimestamp: "2026-08-14T03:50:00.000Z",
      lastEventType: "complaint.created",
      actor: "Budi",
    });
  });
});
