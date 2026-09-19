import { describe, expect, it } from "vitest";
import {
  buildAggregateKpis,
  dashboardStatusDonutRows,
  toCabangDashboardBook,
} from "./loadDashboardData";

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
      { status: "waitingAssignment", count: 1, labelKey: "openUnescalated" },
      { status: "escalatePending", count: 0, labelKey: "waitingEscalationApproval" },
      { status: "escalateApproved", count: 0, labelKey: "escalationApproved" },
      { status: "escalateScheduled", count: 0, labelKey: "escalationScheduled" },
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
      { status: "waitingAssignment", count: 0, labelKey: "openUnescalated" },
      { status: "escalatePending", count: 1, labelKey: "waitingEscalationApproval" },
      { status: "escalateApproved", count: 0, labelKey: "escalationApproved" },
      { status: "escalateScheduled", count: 0, labelKey: "escalationScheduled" },
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
      { status: "waitingAssignment", count: 3, labelKey: "openUnescalated" },
      { status: "escalatePending", count: 4, labelKey: "waitingEscalationApproval" },
      { status: "escalateApproved", count: 1, labelKey: "escalationApproved" },
      { status: "escalateScheduled", count: 0, labelKey: "escalationScheduled" },
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

describe("toCabangDashboardBook", () => {
  it("drops HQ-accepted open rows from cabang totals, rate, and queue book", () => {
    const kpis = buildAggregateKpis({
      total: 30,
      open: 19,
      closed: 11,
      escalatePending: 0,
      waitingAssignment: 0,
      escalateApproved: 0,
      escalateScheduled: 12,
      hqAcceptedOpen: 12,
      inProgress: 7,
    });
    const book = toCabangDashboardBook({
      header: kpis.header,
      sla: null,
      byStatus: kpis.byStatus,
      trend: null,
      hqAcceptedOpen: 12,
      returnedToBranch: kpis.returnedToBranch,
    });
    expect(book.header).toEqual({
      totalComplaints: 18,
      openComplaints: 7,
      closedComplaints: 11,
    });
    expect(
      book.byStatus?.find((row) => row.status === "escalateScheduled")?.count,
    ).toBe(0);
    expect(
      book.byStatus?.find((row) => row.status === "IN_PROGRESS")?.count,
    ).toBe(7);
    expect(
      book.byStatus?.find((row) => row.status === "CLOSED")?.count,
    ).toBe(11);
    expect(
      book.byStatus?.reduce((sum, row) => sum + row.count, 0),
    ).toBe(18);
    // 11 / 18 = 61% — Perlu perhatian, not Kritis (< 60%).
    expect(
      Math.round((book.header!.closedComplaints / book.header!.totalComplaints) * 100),
    ).toBe(61);
  });

  it("leaves the book unchanged when Pusat has accepted nothing", () => {
    const kpis = buildAggregateKpis({
      total: 3,
      open: 1,
      closed: 2,
      escalatePending: 0,
      waitingAssignment: 1,
      hqAcceptedOpen: 0,
    });
    const data = {
      header: kpis.header,
      sla: null,
      byStatus: kpis.byStatus,
      trend: null,
      hqAcceptedOpen: 0,
      returnedToBranch: kpis.returnedToBranch,
    };
    expect(toCabangDashboardBook(data)).toBe(data);
  });

  it("subtracts accepted-unscheduled leftovers from in-progress, not closed", () => {
    const kpis = buildAggregateKpis({
      total: 5,
      open: 4,
      closed: 1,
      escalatePending: 0,
      waitingAssignment: 0,
      escalateApproved: 0,
      escalateScheduled: 1,
      hqAcceptedOpen: 3,
      inProgress: 3,
    });
    const book = toCabangDashboardBook({
      header: kpis.header,
      sla: null,
      byStatus: kpis.byStatus,
      trend: null,
      hqAcceptedOpen: 3,
      returnedToBranch: kpis.returnedToBranch,
    });
    expect(book.header).toEqual({
      totalComplaints: 2,
      openComplaints: 1,
      closedComplaints: 1,
    });
    expect(
      book.byStatus?.find((row) => row.status === "escalateScheduled")?.count,
    ).toBe(0);
    expect(
      book.byStatus?.find((row) => row.status === "IN_PROGRESS")?.count,
    ).toBe(1);
  });
});

describe("dashboardStatusDonutRows", () => {
  it("keeps HQ-scheduled on the cabang donut while the work book drops them", () => {
    const kpis = buildAggregateKpis({
      total: 30,
      open: 19,
      closed: 11,
      escalatePending: 0,
      waitingAssignment: 0,
      escalateApproved: 0,
      escalateScheduled: 12,
      hqAcceptedOpen: 12,
      inProgress: 7,
    });
    const origin = {
      header: kpis.header,
      sla: null,
      byStatus: kpis.byStatus,
      trend: null,
      hqAcceptedOpen: 12,
      returnedToBranch: kpis.returnedToBranch,
    };
    const book = toCabangDashboardBook(origin);
    const donut = dashboardStatusDonutRows(origin, book, false);
    expect(
      donut?.find((row) => row.status === "escalateScheduled")?.count,
    ).toBe(12);
    expect(donut?.reduce((sum, row) => sum + row.count, 0)).toBe(30);
    expect(
      book.byStatus?.find((row) => row.status === "escalateScheduled")?.count,
    ).toBe(0);
  });

  it("uses the unpartitioned book for Pusat", () => {
    const kpis = buildAggregateKpis({
      total: 3,
      open: 3,
      closed: 0,
      escalatePending: 0,
      escalateScheduled: 3,
      hqAcceptedOpen: 3,
      inProgress: 0,
    });
    const origin = {
      header: kpis.header,
      sla: null,
      byStatus: kpis.byStatus,
      trend: null,
      hqAcceptedOpen: 3,
      returnedToBranch: kpis.returnedToBranch,
    };
    expect(dashboardStatusDonutRows(origin, origin, true)).toBe(origin.byStatus);
  });
});
