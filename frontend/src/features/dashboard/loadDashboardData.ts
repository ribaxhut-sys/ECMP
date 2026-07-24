import { fetchDashboardSummary } from "@/lib/api";
import type { DashboardSummary } from "@/lib/api/types";

export type DashboardData = DashboardSummary;

/** Single request — API-319 Dashboard Summary. */
export async function loadDashboardData(): Promise<DashboardData> {
  const res = await fetchDashboardSummary();
  return res.data;
}
