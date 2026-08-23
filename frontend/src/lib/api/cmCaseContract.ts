/**
 * CAP-008 Mode A Case Management — pure path/header contract (no network).
 * Aggregate `/api/v1/cm` — not interchangeable with Sprint `/v1/cases`.
 */
import { CM_BATCH1_AGGREGATE_BASE } from "./dualSotNamespaces";

export const CM_CASE_BASE = CM_BATCH1_AGGREGATE_BASE;

export interface CmCaseMutateOptions {
  idempotencyKey?: string;
}

export function cmCasePaths() {
  return {
    cases: `${CM_CASE_BASE}/cases`,
    case: (caseId: string) =>
      `${CM_CASE_BASE}/cases/${encodeURIComponent(caseId)}`,
    addCase: (complaintId: string) =>
      `${CM_CASE_BASE}/complaints/${encodeURIComponent(complaintId)}/cases`,
    status: (caseId: string) =>
      `${CM_CASE_BASE}/cases/${encodeURIComponent(caseId)}/status`,
    resolve: (caseId: string) =>
      `${CM_CASE_BASE}/cases/${encodeURIComponent(caseId)}/resolve`,
    acceptance: (caseId: string) =>
      `${CM_CASE_BASE}/cases/${encodeURIComponent(caseId)}/acceptance`,
    close: (caseId: string) =>
      `${CM_CASE_BASE}/cases/${encodeURIComponent(caseId)}/close`,
    escalateToPusat: (caseId: string) =>
      `${CM_CASE_BASE}/cases/${encodeURIComponent(caseId)}/escalate-to-pusat`,
    cancelEscalationToPusat: (caseId: string) =>
      `${CM_CASE_BASE}/cases/${encodeURIComponent(caseId)}/cancel-escalation-to-pusat`,
    returnEscalation: (caseId: string) =>
      `${CM_CASE_BASE}/cases/${encodeURIComponent(caseId)}/return-escalation`,
    history: (caseId: string) =>
      `${CM_CASE_BASE}/cases/${encodeURIComponent(caseId)}/history`,
  } as const;
}

export function buildCmCaseMutateHeaders(
  options: CmCaseMutateOptions = {},
): Record<string, string> {
  const headers: Record<string, string> = {};
  const key = options.idempotencyKey?.trim();
  if (key) {
    headers["Idempotency-Key"] = key;
  }
  return headers;
}
