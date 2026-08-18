import { apiRequest } from "./client";
import type {
  DashboardAggregateKpis,
  DashboardRecentActivityItem,
  DashboardTrends,
  DataResponse,
} from "./types";

/**
 * GET /api/v1/dashboard/aggregate-kpis — CM Aggregate KPI (DEC-026).
 * Gated by dashboard:read (not complaints:read). Branch-scoped principals
 * are locked server-side to their own branch.
 */
export function fetchDashboardAggregateKpis(
  options: { branchId?: string; dateFrom?: string; dateTo?: string } = {},
): Promise<DataResponse<DashboardAggregateKpis>> {
  const params = new URLSearchParams();
  if (options.branchId) params.set("branchId", options.branchId);
  if (options.dateFrom) params.set("dateFrom", options.dateFrom);
  if (options.dateTo) params.set("dateTo", options.dateTo);
  const qs = params.toString();
  return apiRequest<DataResponse<DashboardAggregateKpis>>(
    `/api/v1/dashboard/aggregate-kpis${qs ? `?${qs}` : ""}`,
  );
}

/**
 * UM-BUG-009 — GET /api/v1/dashboard/recent-activity, branch-filterable.
 * Head Office (no own branch) may pass branchId (omit for all branches); a
 * branch-scoped principal is always locked server-side to their own branch.
 */
export function fetchDashboardRecentActivity(
  options: { branchId?: string; limit?: number } = {},
): Promise<DataResponse<DashboardRecentActivityItem[]>> {
  const params = new URLSearchParams();
  if (options.branchId) params.set("branchId", options.branchId);
  if (options.limit) params.set("limit", String(options.limit));
  const qs = params.toString();
  return apiRequest<DataResponse<DashboardRecentActivityItem[]>>(
    `/api/v1/dashboard/recent-activity${qs ? `?${qs}` : ""}`,
  );
}

/**
 * API-393 — GET /api/v1/dashboard/trends (14d default).
 * Counts CM Aggregate intake (DEC-026).
 */
export function fetchDashboardTrends(
  period: "today" | "7d" | "30d" = "7d",
): Promise<DataResponse<DashboardTrends>> {
  const params = new URLSearchParams({ period });
  return apiRequest<DataResponse<DashboardTrends>>(
    `/api/v1/dashboard/trends?${params.toString()}`,
  );
}
