import { apiRequest } from "./client";
import type {
  DashboardAggregateKpis,
  DashboardRecentActivityItem,
  DashboardSummary,
  DashboardTrends,
  DataResponse,
} from "./types";

/** API-319 — GET /api/v1/dashboard/overview (CAPABILITY-013 moved widgets). */
export function fetchDashboardSummary(): Promise<
  DataResponse<DashboardSummary>
> {
  return apiRequest<DataResponse<DashboardSummary>>(
    "/api/v1/dashboard/overview",
  );
}

/**
 * DEC-020 — GET /api/v1/dashboard/aggregate-kpis.
 * Gated by dashboard:read (not complaints:read). Branch-scoped principals
 * are locked server-side to their own branch.
 */
export function fetchDashboardAggregateKpis(
  options: { branchId?: string } = {},
): Promise<DataResponse<DashboardAggregateKpis>> {
  const params = new URLSearchParams();
  if (options.branchId) params.set("branchId", options.branchId);
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
 * Foundation-scoped only (DEC-020) — same coexistence boundary as SLA/branch charts.
 */
export function fetchDashboardTrends(
  period: "today" | "7d" | "30d" = "7d",
): Promise<DataResponse<DashboardTrends>> {
  const params = new URLSearchParams({ period });
  return apiRequest<DataResponse<DashboardTrends>>(
    `/api/v1/dashboard/trends?${params.toString()}`,
  );
}
