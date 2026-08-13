import { fetchDashboardAggregateKpis } from "@/lib/api";
import type { BranchCount, ReportSummary, StatusCount } from "@/lib/api/types";
import { buildAggregateKpis } from "@/features/dashboard/loadDashboardData";

export type ReportsData = {
  summary: ReportSummary | null;
  byStatus: StatusCount[] | null;
  byBranch: BranchCount[] | null;
};

/**
 * Operational reports use the same Aggregate KPI as the dashboard (DEC-026).
 */
export async function loadReportsData(): Promise<ReportsData> {
  const res = await fetchDashboardAggregateKpis();
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
  return {
    summary,
    byStatus: kpis.byStatus,
    byBranch: null,
  };
}
