import {
  fetchDashboardSummary,
  fetchReportByBranch,
  fetchReportByStatus,
  searchComplaints,
} from "@/lib/api";
import type {
  BranchCount,
  Complaint,
  DashboardHeader,
  DashboardRecentActivityItem,
  DashboardSlaSummary,
  StatusCount,
} from "@/lib/api/types";

export type DashboardData = {
  header: DashboardHeader | null;
  sla: DashboardSlaSummary | null;
  recentActivity: DashboardRecentActivityItem[] | null;
  byStatus: StatusCount[] | null;
  byBranch: BranchCount[] | null;
  latestComplaints: Complaint[] | null;
};

/**
 * Dashboard payload from existing APIs only:
 * - API-319 overview
 * - Reports by-status / by-branch
 * - API-388 latest complaints (search)
 */
export async function loadDashboardData(): Promise<DashboardData> {
  const [overview, byStatus, byBranch, latest] = await Promise.allSettled([
    fetchDashboardSummary(),
    fetchReportByStatus(),
    fetchReportByBranch(),
    searchComplaints({
      page: 1,
      pageSize: 10,
      sort: "createdAt",
      order: "desc",
    }),
  ]);

  if (overview.status === "rejected") {
    throw overview.reason;
  }

  return {
    header: overview.value.data.header,
    sla: overview.value.data.sla,
    recentActivity: overview.value.data.recentActivity,
    byStatus: byStatus.status === "fulfilled" ? byStatus.value.data : null,
    byBranch: byBranch.status === "fulfilled" ? byBranch.value.data : null,
    latestComplaints:
      latest.status === "fulfilled" ? latest.value.items : null,
  };
}
