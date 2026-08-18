import { apiRequest } from "./client";
import type {
  BranchCount,
  CycleTimeSummary,
  DataResponse,
} from "./types";

/** GET /api/v1/reports/by-branch — used by dashboard Kesehatan Cabang (API-212). */
export function fetchReportByBranch(
  options: { dateFrom?: string; dateTo?: string } = {},
): Promise<DataResponse<BranchCount[]>> {
  const params = new URLSearchParams();
  if (options.dateFrom) params.set("dateFrom", options.dateFrom);
  if (options.dateTo) params.set("dateTo", options.dateTo);
  const qs = params.toString();
  return apiRequest<DataResponse<BranchCount[]>>(
    `/api/v1/reports/by-branch${qs ? `?${qs}` : ""}`,
  );
}

/** GET /api/v1/reports/cycle-time — window filters on case closure date. */
export function fetchReportCycleTime(
  options: { dateFrom?: string; dateTo?: string } = {},
): Promise<DataResponse<CycleTimeSummary>> {
  const params = new URLSearchParams();
  if (options.dateFrom) params.set("dateFrom", options.dateFrom);
  if (options.dateTo) params.set("dateTo", options.dateTo);
  const qs = params.toString();
  return apiRequest<DataResponse<CycleTimeSummary>>(
    `/api/v1/reports/cycle-time${qs ? `?${qs}` : ""}`,
  );
}
