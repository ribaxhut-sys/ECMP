import { afterEach, describe, expect, it } from "vitest";
import { CM_BATCH1_HQ_SCHEDULED_HREF, CM_BATCH1_OPEN_HREF, CM_BATCH1_PUSAT_UNHANDLED_HREF } from "@/features/complaints/cmBatch1ListFilters";
import { formatDateTime24 } from "@/shared/utils/datetime";
import {
  actorInitials,
  activitySubjectText,
  aggregateComplaintActivitySummaries,
  branchHealthMonthOptions,
  branchHealthScale,
  branchHealthShortLabel,
  branchHealthYearOptions,
  branchOptionLabel,
  buildCriticalAlerts,
  buildQueueHealthRows,
  CRITICAL_ALERT_VISIBLE_LIMIT,
  dashboardEmptyWorkCta,
  dashboardStatusSliceHref,
  formatRelativeTime,
  resolveSystemHealth,
  slaComplianceLevel,
  completionPercent,
  dashboardEnvironmentLabel,
  monthDateRangeIso,
  sortBranchesByHealth,
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

describe("branchHealthShortLabel", () => {
  it("drops the shared UPPPD prefix", () => {
    expect(branchHealthShortLabel("UPPPD Tanah Abang")).toBe("Tanah Abang");
  });

  it("handles a hyphenated prefix too", () => {
    expect(branchHealthShortLabel("UPPPD-Tanah Abang")).toBe("Tanah Abang");
  });

  it("leaves names without the prefix untouched", () => {
    expect(branchHealthShortLabel("Kantor Pusat")).toBe("Kantor Pusat");
  });
});

describe("branchHealthScale", () => {
  it("takes the largest single value across the 3 bars, maxed across rows", () => {
    const rows = [
      {
        branchId: "a",
        branchCode: "A",
        branchName: "Alpha",
        unitCode: "ALP",
        total: 100,
        open: 20,
        closed: 30,
        escalated: 40,
        caseTotal: 60,
        caseOpen: 10,
        caseClosed: 50,
      },
      {
        branchId: "b",
        branchCode: "B",
        branchName: "Beta",
        unitCode: "BET",
        total: 900,
        open: 5,
        closed: 5,
        escalated: 2,
        caseTotal: 900,
        caseOpen: 5,
        caseClosed: 5,
      },
    ];
    // Row a: max(caseTotal 60, caseClosed 50, escalated 40) = 60.
    // Row b: max(caseTotal 900, caseClosed 5, escalated 2) = 900.
    expect(branchHealthScale(rows)).toBe(900);
  });

  it("is 0 for an empty row set", () => {
    expect(branchHealthScale([])).toBe(0);
  });
});

describe("monthDateRangeIso", () => {
  it("spans the full month in UTC, dateTo inclusive of the last instant", () => {
    const { dateFrom, dateTo } = monthDateRangeIso(2026, 8);
    expect(dateFrom).toBe("2026-08-01T00:00:00.000Z");
    expect(dateTo).toBe("2026-08-31T23:59:59.999Z");
  });

  it("handles February in a leap year", () => {
    const { dateTo } = monthDateRangeIso(2028, 2);
    expect(dateTo).toBe("2028-02-29T23:59:59.999Z");
  });
});

describe("branchHealthMonthOptions", () => {
  it("returns 12 months, 1-indexed, capitalized", () => {
    const options = branchHealthMonthOptions("id");
    expect(options).toHaveLength(12);
    expect(options[0]).toEqual({ value: 1, label: "Januari" });
    expect(options[7]).toEqual({ value: 8, label: "Agustus" });
  });
});

describe("branchHealthYearOptions", () => {
  it("returns the most recent years, newest first", () => {
    expect(branchHealthYearOptions(2026, 3)).toEqual([2026, 2025, 2024]);
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
    { status: "waitingAssignment" as const, count: 4 },
    { status: "escalatePending" as const, count: 4 },
    { status: "escalateApproved" as const, count: 2 },
    { status: "escalateScheduled" as const, count: 1 },
    { status: "CLOSED" as const, count: 6 },
    { status: "IN_PROGRESS" as const, count: 0 },
  ];

  it("shows assignment + HQ-path bars from CM Aggregate", () => {
    const rows = buildQueueHealthRows({
      byStatus,
      waitingAssignmentHref:
        "/complaints?status=REGISTERED&intakeDisposition=UNESCALATED",
      escalationHref:
        "/complaints?intakeDisposition=ESCALATE_PENDING_APPROVAL",
      hqEscalationHref: "/complaints?intakeDisposition=ESCALATE_APPROVED",
      hqScheduledHref: "/complaints?intakeDisposition=HQ_SCHEDULED",
    });

    expect(rows.map((row) => row.id)).toEqual([
      "waiting-assignment",
      "waiting-escalation",
      "waiting-hq-escalation",
      "hq-scheduled",
    ]);
    expect(rows[0]?.count).toBe(4);
    expect(rows[1]?.count).toBe(4);
    expect(rows[1]?.queueKey).toBe("waitingEscalationApproval");
    expect(rows[2]?.count).toBe(2);
    expect(rows[2]?.queueKey).toBe("waitingHqEscalation");
    expect(rows[3]?.count).toBe(1);
    expect(rows[3]?.queueKey).toBe("escalationScheduled");
  });

  it("keeps HQ bars at zero when those slices are absent", () => {
    const rows = buildQueueHealthRows({
      byStatus: [{ status: "waitingAssignment" as const, count: 1 }],
      waitingAssignmentHref: null,
      escalationHref: null,
      hqEscalationHref: null,
      hqScheduledHref: null,
    });
    expect(rows.map((row) => row.count)).toEqual([1, 0, 0, 0]);
  });

  it("replaces cabang bars with a Pusat pipeline and drops empty stages", () => {
    const rows = buildQueueHealthRows({
      byStatus,
      waitingAssignmentHref: null,
      escalationHref: null,
      hqEscalationHref: "/complaints?intakeDisposition=ESCALATE_APPROVED",
      hqScheduledHref: "/complaints?intakeDisposition=HQ_SCHEDULED",
      audience: "pusat",
      pusatQueue: 1,
      hqScheduleToday: 0,
      pusatQueueHref: "/complaints?needsPusatHandling=1",
      hqScheduleTodayHref: "/complaints/cm/hq-schedule",
    });
    expect(rows.map((row) => row.id)).toEqual(["pusat-intake", "hq-scheduled"]);
    expect(rows[0]?.count).toBe(1);
    expect(rows[0]?.href).toBe("/complaints?needsPusatHandling=1");
    expect(rows[1]?.count).toBe(1);
    expect(rows[1]?.href).toBe("/complaints?intakeDisposition=HQ_SCHEDULED");
  });

  it("returns an empty Pusat pipeline when every stage is clear", () => {
    const rows = buildQueueHealthRows({
      byStatus: [{ status: "waitingAssignment" as const, count: 5 }],
      waitingAssignmentHref: null,
      escalationHref: null,
      hqEscalationHref: null,
      hqScheduledHref: "/complaints?intakeDisposition=HQ_SCHEDULED",
      audience: "pusat",
      pusatQueue: 0,
      hqScheduleToday: 0,
    });
    expect(rows).toEqual([]);
  });
});

describe("dashboardEmptyWorkCta (DEC-026)", () => {
  it("sends officers to the CM open list", () => {
    expect(dashboardEmptyWorkCta()).toEqual({
      href: CM_BATCH1_OPEN_HREF,
      ctaKey: "goToComplaints",
    });
  });

  it("sends Pusat officers to the unhandled queue", () => {
    expect(dashboardEmptyWorkCta("pusat")).toEqual({
      href: CM_BATCH1_PUSAT_UNHANDLED_HREF,
      ctaKey: "goToComplaints",
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
    expect(alerts.find((a) => a.id === "sla-assignment")?.href).toBe(
      "/complaints",
    );
  });

  it("surfaces Pusat work queues ahead of branch escalation-pending", () => {
    const alerts = buildCriticalAlerts({
      breached: 0,
      assignmentBreached: 0,
      resolutionBreached: 0,
      escalated: 2,
      escalationHref: "/complaints?intakeDisposition=ESCALATE_PENDING_APPROVAL",
      pusatQueue: 1,
      pusatFollowUp: 0,
      hqScheduleToday: 10,
      escalateScheduled: 12,
    });
    expect(alerts.map((alert) => alert.id)).toEqual([
      "pusat-queue",
      "hq-schedule-today",
      "hq-scheduled",
      "escalation",
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

  it("asks for attention when Pusat HQ work is waiting", () => {
    expect(
      resolveSystemHealth({
        loading: false,
        error: false,
        sla: null,
        waitingAssignment: 0,
        escalatePending: 0,
        pusatQueue: 1,
        hqScheduleToday: 10,
        escalateScheduled: 12,
      }),
    ).toBe("attention");
  });

  it("degrades on an overdue complaint even when the queue is empty", () => {
    // DEC-031: a broken 30-day promise outranks queue counts on this bar.
    expect(
      resolveSystemHealth({
        loading: false,
        error: false,
        sla: { ...emptySla, overdue: 1 },
        waitingAssignment: 0,
        escalatePending: 0,
      }),
    ).toBe("degraded");
  });

  it("asks for attention when a complaint is only approaching its deadline", () => {
    expect(
      resolveSystemHealth({
        loading: false,
        error: false,
        sla: { ...emptySla, warning: 2 },
        waitingAssignment: 0,
        escalatePending: 0,
      }),
    ).toBe("attention");
  });
});

describe("dashboardStatusSliceHref", () => {
  it("opens the HQ scheduled list without pinning Pusat intake", () => {
    expect(dashboardStatusSliceHref("escalateScheduled")).toBe(
      CM_BATCH1_HQ_SCHEDULED_HREF,
    );
    expect(dashboardStatusSliceHref("escalateScheduled")).not.toContain(
      "needsPusatHandling",
    );
  });
});

const emptySla = {
  targetDays: 30,
  onTrack: 0,
  warning: 0,
  overdue: 0,
  met: 0,
  missed: 0,
  unknown: 0,
  compliancePercentage: null,
};

describe("slaComplianceLevel", () => {
  it("is healthy when nothing is measured", () => {
    expect(slaComplianceLevel(null)).toBe("healthy");
  });

  it("does not read 'nothing settled yet' as failure", () => {
    // compliancePercentage null must not be treated as 0%.
    expect(slaComplianceLevel({ ...emptySla, onTrack: 5 })).toBe("healthy");
  });

  it("warns while nothing has settled but something is approaching", () => {
    expect(slaComplianceLevel({ ...emptySla, warning: 1 })).toBe("warning");
  });

  it("is critical whenever a complaint is past the target, whatever the average", () => {
    expect(
      slaComplianceLevel({
        ...emptySla,
        overdue: 1,
        met: 99,
        compliancePercentage: 99,
      }),
    ).toBe("critical");
  });

  it("grades settled compliance", () => {
    expect(
      slaComplianceLevel({ ...emptySla, met: 96, missed: 4, compliancePercentage: 96 }),
    ).toBe("excellent");
    expect(
      slaComplianceLevel({ ...emptySla, met: 88, missed: 12, compliancePercentage: 88 }),
    ).toBe("healthy");
    expect(
      slaComplianceLevel({ ...emptySla, met: 70, missed: 30, compliancePercentage: 70 }),
    ).toBe("warning");
    expect(
      slaComplianceLevel({ ...emptySla, met: 40, missed: 60, compliancePercentage: 40 }),
    ).toBe("critical");
  });
});

describe("dashboardEnvironmentLabel", () => {
  const originalSurface = process.env.NEXT_PUBLIC_ECMP_SURFACE;

  afterEach(() => {
    if (originalSurface === undefined) {
      delete process.env.NEXT_PUBLIC_ECMP_SURFACE;
    } else {
      process.env.NEXT_PUBLIC_ECMP_SURFACE = originalSurface;
    }
  });

  it("returns lab when the lab surface is baked in", () => {
    process.env.NEXT_PUBLIC_ECMP_SURFACE = "lab";
    expect(dashboardEnvironmentLabel()).toBe("lab");
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
        caseNumber: "CASE-TAD-2",
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
      caseNumber: "CASE-TAD-2",
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

  it("ignores complaint.other so the summary badge is a real work state", () => {
    const summaries = aggregateComplaintActivitySummaries([
      {
        eventType: "complaint.other",
        complaintNumber: "TAB-2608-0014",
        caseNumber: "TAB-2608-0014",
        timestamp: "2026-08-26T01:34:10.000Z",
        actor: "Dewi Hidayat",
      },
      {
        eventType: "complaint.handling_continued",
        complaintNumber: "TAB-2608-0014",
        caseNumber: "TAB-2608-0014",
        timestamp: "2026-08-26T01:34:09.000Z",
        actor: "Dewi Hidayat",
      },
      {
        eventType: "complaint.escalated_to_pusat",
        complaintNumber: "TAB-2608-0013",
        caseNumber: "TAB-2608-0013",
        timestamp: "2026-08-26T01:34:08.000Z",
        actor: "Dewi Hidayat",
      },
    ]);

    expect(summaries).toHaveLength(2);
    expect(summaries[0]).toMatchObject({
      complaintNumber: "TAB-2608-0014",
      lastEventType: "complaint.handling_continued",
    });
    expect(summaries[1]).toMatchObject({
      complaintNumber: "TAB-2608-0013",
      lastEventType: "complaint.escalated_to_pusat",
    });
  });

  it("drops a complaint that only has unknown activity", () => {
    expect(
      aggregateComplaintActivitySummaries([
        {
          eventType: "complaint.other",
          complaintNumber: "TAB-2608-0000",
          timestamp: "2026-08-26T01:00:00.000Z",
          actor: "SYSTEM",
        },
      ]),
    ).toEqual([]);
  });

  it("prefers closed over created when timestamps are equal", () => {
    const summaries = aggregateComplaintActivitySummaries([
      {
        eventType: "complaint.created",
        complaintNumber: "TAB-2608-0009",
        timestamp: "2026-08-15T06:55:54.516Z",
        actor: "Ahmad Santoso",
      },
      {
        eventType: "complaint.closed",
        complaintNumber: "TAB-2608-0009",
        timestamp: "2026-08-15T06:55:54.516Z",
        actor: "Ahmad Santoso",
      },
    ]);

    expect(summaries).toHaveLength(1);
    expect(summaries[0].lastEventType).toBe("complaint.closed");
  });
});

describe("completionPercent", () => {
  it("returns null when there is no volume", () => {
    expect(completionPercent(0, 0)).toBeNull();
  });

  it("rounds closed over total", () => {
    expect(completionPercent(9, 9)).toBe(100);
    expect(completionPercent(1, 3)).toBe(33);
  });
});

describe("sortBranchesByHealth", () => {
  it("puts higher case completion first", () => {
    const sorted = sortBranchesByHealth([
      {
        branchId: "a",
        branchCode: "A",
        branchName: "Alpha",
        unitCode: null,
        escalated: 0,
        total: 10,
        open: 9,
        closed: 1,
        caseTotal: 10,
        caseOpen: 9,
        caseClosed: 1,
      },
      {
        branchId: "b",
        branchCode: "B",
        branchName: "Beta",
        unitCode: null,
        escalated: 0,
        total: 3,
        open: 0,
        closed: 3,
        caseTotal: 3,
        caseOpen: 0,
        caseClosed: 3,
      },
    ]);
    expect(sorted.map((row) => row.branchCode)).toEqual(["B", "A"]);
  });
});

describe("formatRelativeTime", () => {
  const nowMs = Date.parse("2026-08-16T12:00:00.000Z");

  it("keeps hour-scale relative labels on the same day", () => {
    expect(
      formatRelativeTime("2026-08-16T10:00:00.000Z", "id", nowMs),
    ).toBe(new Intl.RelativeTimeFormat("id", { numeric: "auto" }).format(-2, "hour"));
  });

  it("uses calendar datetime instead of kemarin dulu after 24h", () => {
    const value = "2026-08-14T12:00:00.000Z";
    expect(formatRelativeTime(value, "id", nowMs)).toBe(formatDateTime24(value, "id"));
    expect(formatRelativeTime(value, "id", nowMs)).not.toMatch(/kemarin/);
  });
});

describe("activitySubjectText", () => {
  it("shows the case number when present", () => {
    expect(
      activitySubjectText({
        complaintNumber: "TAB-2608-0001",
        caseNumber: "CASE-3",
      }),
    ).toBe("CASE-3");
  });

  it("falls back to the complaint number before a case exists", () => {
    expect(
      activitySubjectText({
        complaintNumber: "TAB-2608-0001",
        caseNumber: null,
      }),
    ).toBe("TAB-2608-0001");
  });
});
