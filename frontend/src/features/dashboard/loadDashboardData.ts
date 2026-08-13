import {
  fetchDashboardAggregateKpis,
  fetchDashboardSummary,
  fetchDashboardTrends,
  fetchReportByBranch,
  fetchReportByStatus,
} from "@/lib/api";
import type {
  BranchCount,
  DashboardHeader,
  DashboardSlaSummary,
  DashboardTrendItem,
  StatusCount,
} from "@/lib/api/types";

/**
 * Mode A operational KPI from Aggregate (dashboard/aggregate-kpis).
 * Fills dashboard numbers for Batch-1 intake without Retirement DEC / foundation merge.
 * Gated by dashboard:read so MANAGER (BC-8.4) can see own-branch KPIs without
 * complaints:read / unscoped list access.
 */
export type AggregateDashboardKpis = {
  total: number;
  open: number;
  closed: number;
  escalatePending: number;
  waitingAssignment: number;
  escalateApproved: number;
  inProgress: number;
  /** Mutually exclusive operational slices — sum equals total. */
  byStatus: StatusCount[];
  header: DashboardHeader;
};

export type DashboardData = {
  header: DashboardHeader | null;
  /** Null on Aggregate KPI (BQ-005 / DEC-020) — do not mix foundation clocks. */
  sla: DashboardSlaSummary | null;
  byStatus: StatusCount[] | null;
  byBranch: BranchCount[] | null;
  /**
   * 30-day daily complaint-count trend. Foundation-scoped only (DEC-020) —
   * does not reflect Aggregate-only intake even when complaintKpiSource is
   * "aggregate".
   */
  trend: DashboardTrendItem[] | null;
  /** True when complaint KPI numbers come from Aggregate (DEC-020 coexistence). */
  complaintKpiSource: "aggregate" | "foundation";
};

export function buildAggregateKpis(input: {
  total: number;
  open: number;
  closed: number;
  escalatePending: number;
  waitingAssignment?: number;
  escalateApproved?: number;
  inProgress?: number;
}): AggregateDashboardKpis {
  const escalateApproved = input.escalateApproved ?? 0;
  const inProgress = input.inProgress ?? 0;
  const waitingAssignment =
    input.waitingAssignment ??
    Math.max(0, input.open - input.escalatePending - escalateApproved);
  // Mutually exclusive slices. Open-and-not-escalated is "Terbuka", not "Baru".
  // ESCALATE_PENDING / ESCALATE_APPROVED stay in their own slices.
  const byStatus: StatusCount[] = [
    {
      status: "NEW",
      count: waitingAssignment,
      labelKey: "openUnescalated",
    },
    {
      status: "ESCALATED",
      count: input.escalatePending,
      labelKey: "waitingEscalationApproval",
    },
    {
      status: "ASSIGNED",
      count: escalateApproved,
      labelKey: "escalationApproved",
    },
    {
      status: "IN_PROGRESS",
      count: inProgress,
      labelKey: "queueInProgress",
    },
    {
      status: "CLOSED",
      count: input.closed,
      labelKey: "closedComplaints",
    },
  ];
  return {
    total: input.total,
    open: input.open,
    closed: input.closed,
    escalatePending: input.escalatePending,
    waitingAssignment,
    escalateApproved,
    inProgress,
    byStatus,
    header: {
      totalComplaints: input.total,
      openComplaints: input.open,
      closedComplaints: input.closed,
    },
  };
}

async function loadAggregateKpis(): Promise<AggregateDashboardKpis> {
  const res = await fetchDashboardAggregateKpis();
  const data = res.data;
  return buildAggregateKpis({
    total: data.total,
    open: data.open,
    closed: data.closed,
    escalatePending: data.escalatePending,
    waitingAssignment: data.waitingAssignment,
    escalateApproved: data.escalateApproved,
    inProgress: data.inProgress,
  });
}

/**
 * DEC-020 + BQ-005: do not mix foundation SLA clocks into Aggregate KPI.
 * Mode A Batch-1 binds policy without countdown; foundation breach counts
 * (e.g. 18) belong to a different portfolio than the donut (e.g. 9).
 */
export function selectDashboardSla(input: {
  complaintKpiSource: "aggregate" | "foundation";
  foundationSla: DashboardSlaSummary | null;
}): DashboardSlaSummary | null {
  if (input.complaintKpiSource === "aggregate") return null;
  return input.foundationSla;
}

/**
 * Dashboard payload:
 * - Complaint KPI numbers prefer Aggregate (dashboard/aggregate-kpis) — where Batch-1 intake writes
 * - SLA clocks stay on the same SoT as those KPIs (null while Aggregate / BQ-005)
 * - Branch charts remain foundation until Retirement DEC
 */
export async function loadDashboardData(): Promise<DashboardData> {
  const [overview, byStatus, byBranch, trends, aggregate] =
    await Promise.allSettled([
      fetchDashboardSummary(),
      fetchReportByStatus(),
      fetchReportByBranch(),
      fetchDashboardTrends("30d"),
      loadAggregateKpis(),
    ]);

  if (overview.status === "rejected") {
    throw overview.reason;
  }

  const foundationHeader = overview.value.data.header;
  const foundationByStatus =
    byStatus.status === "fulfilled" ? byStatus.value.data : null;
  const trend = trends.status === "fulfilled" ? trends.value.data.items : null;

  if (aggregate.status === "fulfilled") {
    return {
      header: aggregate.value.header,
      sla: selectDashboardSla({
        complaintKpiSource: "aggregate",
        foundationSla: overview.value.data.sla,
      }),
      byStatus: aggregate.value.byStatus,
      byBranch: byBranch.status === "fulfilled" ? byBranch.value.data : null,
      trend,
      complaintKpiSource: "aggregate",
    };
  }

  return {
    header: foundationHeader,
    sla: selectDashboardSla({
      complaintKpiSource: "foundation",
      foundationSla: overview.value.data.sla,
    }),
    byStatus: foundationByStatus,
    byBranch: byBranch.status === "fulfilled" ? byBranch.value.data : null,
    trend,
    complaintKpiSource: "foundation",
  };
}
