import {
  fetchLatestComplaints,
  fetchReportByBranch,
  fetchReportByStatus,
  fetchReportSummary,
} from "@/lib/api";
import type {
  BranchCount,
  Complaint,
  ReportSummary,
  StatusCount,
} from "@/lib/api/types";

export interface DashboardData {
  summary: ReportSummary;
  byStatus: StatusCount[];
  byBranch: BranchCount[];
  latestComplaints: Complaint[];
}

/** Single parallel fetch — each endpoint called exactly once. */
export async function loadDashboardData(): Promise<DashboardData> {
  const [summaryRes, statusRes, branchRes, complaintsRes] = await Promise.all([
    fetchReportSummary(),
    fetchReportByStatus(),
    fetchReportByBranch(),
    fetchLatestComplaints(10),
  ]);

  return {
    summary: summaryRes.data,
    byStatus: statusRes.data,
    byBranch: branchRes.data,
    latestComplaints: complaintsRes.data,
  };
}
