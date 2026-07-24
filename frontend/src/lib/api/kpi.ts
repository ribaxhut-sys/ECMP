import { apiRequest } from "./client";
import type { DataResponse, KpiSummary } from "./types";

export interface KpiSummaryFilters {
  branchId?: string;
  dateFrom?: string;
  dateTo?: string;
  category?: string;
  priority?: "LOW" | "MEDIUM" | "HIGH" | "CRITICAL";
}

/** API-318 KPI Foundation summary (live aggregates). */
export function fetchKpiSummary(
  filters: KpiSummaryFilters = {},
): Promise<DataResponse<KpiSummary>> {
  const params = new URLSearchParams();
  if (filters.branchId) params.set("branchId", filters.branchId);
  if (filters.dateFrom) params.set("dateFrom", filters.dateFrom);
  if (filters.dateTo) params.set("dateTo", filters.dateTo);
  if (filters.category) params.set("category", filters.category);
  if (filters.priority) params.set("priority", filters.priority);
  const qs = params.toString();
  const path = qs ? `/api/v1/kpi/summary?${qs}` : "/api/v1/kpi/summary";
  return apiRequest<DataResponse<KpiSummary>>(path);
}
