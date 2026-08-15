import { fetchDashboardAggregateKpis, fetchReportByBranch } from "@/lib/api";
import type { BranchCount, ReportSummary, StatusCount } from "@/lib/api/types";
import { buildAggregateKpis } from "@/features/dashboard/loadDashboardData";

export type ReportsData = {
  summary: ReportSummary | null;
  byStatus: StatusCount[] | null;
  byBranch: BranchCount[] | null;
};

/**
 * Operational reports use the same Aggregate KPI as the dashboard (DEC-026).
 *
 * Branch rows come from API-212 (`/reports/by-branch`), which reads the same
 * Batch-1 Aggregate. It is a side panel, so a failure there degrades to "no
 * branch data" instead of taking the whole page down with it.
 */
export async function loadReportsData(): Promise<ReportsData> {
  const [res, branchRes] = await Promise.all([
    fetchDashboardAggregateKpis(),
    fetchReportByBranch().catch(() => null),
  ]);
  const kpis = buildAggregateKpis({
    total: res.data.total,
    open: res.data.open,
    closed: res.data.closed,
    escalatePending: res.data.escalatePending,
    waitingAssignment: res.data.waitingAssignment,
    escalateApproved: res.data.escalateApproved,
    inProgress: res.data.inProgress,
  });
  const summary: ReportSummary = {
    total: kpis.total,
    byStatus: kpis.byStatus,
  };
  const branchRows = branchRes?.data ?? [];
  return {
    summary,
    byStatus: kpis.byStatus,
    byBranch: branchRows.length > 0 ? branchRows : null,
  };
}
