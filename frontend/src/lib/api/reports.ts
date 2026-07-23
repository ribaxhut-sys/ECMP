import { apiRequest } from "./client";
import type {
  BranchCount,
  DataResponse,
  ReportSummary,
  StatusCount,
} from "./types";

export function fetchReportSummary(): Promise<DataResponse<ReportSummary>> {
  return apiRequest<DataResponse<ReportSummary>>("/api/v1/reports/summary");
}

export function fetchReportByStatus(): Promise<DataResponse<StatusCount[]>> {
  return apiRequest<DataResponse<StatusCount[]>>("/api/v1/reports/by-status");
}

export function fetchReportByBranch(): Promise<DataResponse<BranchCount[]>> {
  return apiRequest<DataResponse<BranchCount[]>>("/api/v1/reports/by-branch");
}
