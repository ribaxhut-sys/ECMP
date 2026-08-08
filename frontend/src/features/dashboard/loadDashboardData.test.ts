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
      { status: "NEW", count: 1 },
      { status: "ESCALATED", count: 0 },
      { status: "CLOSED", count: 2 },
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
      { status: "NEW", count: 0 },
      { status: "ESCALATED", count: 1 },
      { status: "CLOSED", count: 2 },
    ]);
    const byStatusSum = kpis.byStatus.reduce((sum, row) => sum + row.count, 0);
    expect(byStatusSum).toBe(kpis.total);
  });
});
