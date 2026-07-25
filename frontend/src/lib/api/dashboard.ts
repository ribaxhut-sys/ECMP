import { apiRequest } from "./client";
import type { DashboardSummary, DataResponse } from "./types";

/** API-319 — GET /api/v1/dashboard/overview (CAPABILITY-013 moved widgets). */
export function fetchDashboardSummary(): Promise<
  DataResponse<DashboardSummary>
> {
  return apiRequest<DataResponse<DashboardSummary>>(
    "/api/v1/dashboard/overview",
  );
}
