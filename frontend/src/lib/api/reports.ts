import { apiRequest, apiRequestBlob } from "./client";
import type {
  BranchCount,
  CycleTimeSummary,
  DataResponse,
  ReportPrintCategory,
  UserActivityCount,
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
  options: { branchId?: string; dateFrom?: string; dateTo?: string } = {},
): Promise<DataResponse<CycleTimeSummary>> {
  const params = new URLSearchParams();
  if (options.branchId) params.set("branchId", options.branchId);
  if (options.dateFrom) params.set("dateFrom", options.dateFrom);
  if (options.dateTo) params.set("dateTo", options.dateTo);
  const qs = params.toString();
  return apiRequest<DataResponse<CycleTimeSummary>>(
    `/api/v1/reports/cycle-time${qs ? `?${qs}` : ""}`,
  );
}

/** GET /api/v1/reports/by-user — per-officer operational activity (API-547). */
export function fetchReportByUser(
  options: { branchId?: string; dateFrom?: string; dateTo?: string } = {},
): Promise<DataResponse<UserActivityCount[]>> {
  const params = new URLSearchParams();
  if (options.branchId) params.set("branchId", options.branchId);
  if (options.dateFrom) params.set("dateFrom", options.dateFrom);
  if (options.dateTo) params.set("dateTo", options.dateTo);
  const qs = params.toString();
  return apiRequest<DataResponse<UserActivityCount[]>>(
    `/api/v1/reports/by-user${qs ? `?${qs}` : ""}`,
  );
}

export interface ReportPrintResult {
  blob: Blob;
  filename: string;
}

/** GET /api/v1/reports/print (API-546) — export-to-PDF, rendered server-side. */
export async function printReportPdf(options: {
  category: ReportPrintCategory;
  periodLabel: string;
  dateFrom?: string;
  dateTo?: string;
  branchId?: string;
  lang?: string;
  compareDateFrom?: string;
  compareDateTo?: string;
}): Promise<ReportPrintResult> {
  const params = new URLSearchParams({
    category: options.category,
    periodLabel: options.periodLabel,
  });
  if (options.dateFrom) params.set("dateFrom", options.dateFrom);
  if (options.dateTo) params.set("dateTo", options.dateTo);
  if (options.branchId) params.set("branchId", options.branchId);
  if (options.lang) params.set("lang", options.lang);
  if (options.compareDateFrom) params.set("compareDateFrom", options.compareDateFrom);
  if (options.compareDateTo) params.set("compareDateTo", options.compareDateTo);

  const result = await apiRequestBlob(
    `/api/v1/reports/print?${params.toString()}`,
  );
  const match = /filename="([^"]+)"/i.exec(result.contentDisposition ?? "");
  return {
    blob: result.blob,
    filename: match?.[1] ?? `laporan-pengaduan-${options.category}.pdf`,
  };
}
