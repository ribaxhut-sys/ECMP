import {
  fetchReportByBranch,
  fetchReportByStatus,
  fetchReportSummary,
} from "@/lib/api";
import type { BranchCount, ReportSummary, StatusCount } from "@/lib/api/types";

export type ReportsData = {
  summary: ReportSummary | null;
  byStatus: StatusCount[] | null;
  byBranch: BranchCount[] | null;
};

/**
 * Reports page payload from frozen catalog APIs only:
 * - API-210 summary
 * - API-211 by-status
 * - API-212 by-branch
 */
export async function loadReportsData(): Promise<ReportsData> {
  const [summary, byStatus, byBranch] = await Promise.allSettled([
    fetchReportSummary(),
    fetchReportByStatus(),
    fetchReportByBranch(),
  ]);

  if (
    summary.status === "rejected" &&
    byStatus.status === "rejected" &&
    byBranch.status === "rejected"
  ) {
    throw summary.reason;
  }

  return {
    summary: summary.status === "fulfilled" ? summary.value.data : null,
    byStatus: byStatus.status === "fulfilled" ? byStatus.value.data : null,
    byBranch: byBranch.status === "fulfilled" ? byBranch.value.data : null,
  };
}
