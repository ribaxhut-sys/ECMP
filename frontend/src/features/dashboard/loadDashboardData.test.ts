import { describe, expect, it } from "vitest";
import { buildAggregateKpis } from "./loadDashboardData";

describe("buildAggregateKpis", () => {
  it("maps Aggregate totals into dashboard header and status chips", () => {
    const kpis = buildAggregateKpis({
      total: 3,
      open: 1,
      closed: 2,
      escalatePending: 0,
    });
    expect(kpis.header).toEqual({
      totalComplaints: 3,
      openComplaints: 1,
      closedComplaints: 2,
    });
    expect(kpis.byStatus).toEqual([
      { status: "NEW", count: 1, labelKey: "openUnescalated" },
      { status: "ESCALATED", count: 0, labelKey: "waitingEscalationApproval" },
      { status: "ASSIGNED", count: 0, labelKey: "escalationApproved" },
      { status: "PENDING", count: 0, labelKey: "escalationScheduled" },
      { status: "IN_PROGRESS", count: 0, labelKey: "queueInProgress" },
      { status: "CLOSED", count: 2, labelKey: "closedComplaints" },
    ]);
  });

  it("does not double-count a REGISTERED row that is also escalate-pending", () => {
    // Real case: 1 row is status=REGISTERED AND
    // intakeDisposition=ESCALATE_PENDING_APPROVAL — the same physical
    // complaint, not two. byStatus must sum back to the real total (3),
    // not 4.
    const kpis = buildAggregateKpis({
      total: 3,
      open: 1,
      closed: 2,
      escalatePending: 1,
    });
    expect(kpis.byStatus).toEqual([
      { status: "NEW", count: 0, labelKey: "openUnescalated" },
      { status: "ESCALATED", count: 1, labelKey: "waitingEscalationApproval" },
      { status: "ASSIGNED", count: 0, labelKey: "escalationApproved" },
      { status: "PENDING", count: 0, labelKey: "escalationScheduled" },
      { status: "IN_PROGRESS", count: 0, labelKey: "queueInProgress" },
      { status: "CLOSED", count: 2, labelKey: "closedComplaints" },
    ]);
    const byStatusSum = kpis.byStatus.reduce((sum, row) => sum + row.count, 0);
    expect(byStatusSum).toBe(kpis.total);
  });

  it("does not label ESCALATE_APPROVED as waiting-assignment / Baru", () => {
    const kpis = buildAggregateKpis({
      total: 16,
      open: 8,
      closed: 6,
      escalatePending: 4,
      waitingAssignment: 3,
      escalateApproved: 1,
      inProgress: 2,
    });
    expect(kpis.byStatus).toEqual([
      { status: "NEW", count: 3, labelKey: "openUnescalated" },
      { status: "ESCALATED", count: 4, labelKey: "waitingEscalationApproval" },
      { status: "ASSIGNED", count: 1, labelKey: "escalationApproved" },
      { status: "PENDING", count: 0, labelKey: "escalationScheduled" },
      { status: "IN_PROGRESS", count: 2, labelKey: "queueInProgress" },
      { status: "CLOSED", count: 6, labelKey: "closedComplaints" },
    ]);
    expect(kpis.byStatus.reduce((sum, row) => sum + row.count, 0)).toBe(16);
  });

  it("keeps HQ_SCHEDULED on the escalation path instead of in-progress", () => {
    const kpis = buildAggregateKpis({
      total: 3,
      open: 3,
      closed: 0,
      escalatePending: 0,
      waitingAssignment: 0,
      escalateApproved: 0,
      escalateScheduled: 3,
      inProgress: 0,
    });
    expect(
      kpis.byStatus.find((row) => row.labelKey === "escalationScheduled")?.count,
    ).toBe(3);
    expect(
      kpis.byStatus.find((row) => row.labelKey === "queueInProgress")?.count,
    ).toBe(0);
    expect(kpis.byStatus.reduce((sum, row) => sum + row.count, 0)).toBe(3);
  });
});
