import {
  fetchDashboardAggregateKpis,
  fetchDashboardSummary,
  fetchDashboardTrends,
  fetchReportByBranch,
  fetchReportByStatus,
} from "@/lib/api";
import type {
  BranchCount,
  ComplaintStatus,
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
  /** Synthesized for existing SummaryCards / QueueHealth status chips. */
  byStatus: StatusCount[];
  header: DashboardHeader;
};

export type DashboardData = {
  header: DashboardHeader | null;
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
}): AggregateDashboardKpis {
  // `open` (status=REGISTERED) and `escalatePending`
  // (intakeDisposition=ESCALATE_PENDING_APPROVAL) are independent filters,
  // not mutually exclusive buckets — a REGISTERED row pending escalation
  // approval matches both. Summed naively as pie slices that double-counts
  // it. "Escalating" is a sub-state of "open", so subtract it out of the
  // NEW bucket; header.openComplaints keeps the full (unadjusted) open
  // count since those items are still genuinely open.
  const byStatus: StatusCount[] = [
    {
      status: "NEW" as ComplaintStatus,
      count: Math.max(0, input.open - input.escalatePending),
    },
    {
      status: "ESCALATED" as ComplaintStatus,
      count: input.escalatePending,
    },
    { status: "CLOSED" as ComplaintStatus, count: input.closed },
  ];
  return {
    ...input,
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
  });
}

/**
 * Dashboard payload:
 * - Complaint KPI numbers prefer Aggregate (dashboard/aggregate-kpis) — where Batch-1 intake writes
 * - SLA / branch / foundation activity remain foundation until Retirement DEC
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
      sla: overview.value.data.sla,
      byStatus: aggregate.value.byStatus,
      byBranch: byBranch.status === "fulfilled" ? byBranch.value.data : null,
      trend,
      complaintKpiSource: "aggregate",
    };
  }

  return {
    header: foundationHeader,
    sla: overview.value.data.sla,
    byStatus: foundationByStatus,
    byBranch: byBranch.status === "fulfilled" ? byBranch.value.data : null,
    trend,
    complaintKpiSource: "foundation",
  };
}
