import { apiRequest } from "./client";
import type { DashboardSummary, DataResponse } from "./types";

/** API-319 — GET /api/v1/dashboard/summary */
export function fetchDashboardSummary(): Promise<
  DataResponse<DashboardSummary>
> {
  return apiRequest<DataResponse<DashboardSummary>>(
    "/api/v1/dashboard/summary",
  );
}
