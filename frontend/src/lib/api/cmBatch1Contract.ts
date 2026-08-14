/**
 * Pure CM Batch 1 Aggregate path/header contract (no network).
 * Kept separate so Vitest coverage gates can include helpers without Axios.
 */
import { CM_BATCH1_AGGREGATE_BASE } from "./dualSotNamespaces";

export const CM_BATCH1_BASE = CM_BATCH1_AGGREGATE_BASE;

export interface CmBatch1CreateComplaintOptions {
  idempotencyKey?: string;
  channelMessageId?: string;
}

export function cmBatch1Paths() {
  return {
    customerSearch: `${CM_BATCH1_BASE}/customers/search`,
    customerConfirm: `${CM_BATCH1_BASE}/customers/confirm`,
    customer360: (customerId: string) =>
      `${CM_BATCH1_BASE}/customers/${encodeURIComponent(customerId)}/batch1-360`,
    complaints: `${CM_BATCH1_BASE}/complaints`,
    complaint: (complaintId: string) =>
      `${CM_BATCH1_BASE}/complaints/${encodeURIComponent(complaintId)}`,
    complaintHistory: (complaintId: string) =>
      `${CM_BATCH1_BASE}/complaints/${encodeURIComponent(complaintId)}/history`,
    complaintAttachments: (complaintId: string) =>
      `${CM_BATCH1_BASE}/complaints/${encodeURIComponent(complaintId)}/attachments`,
    intakeEscalationDecision: (complaintId: string) =>
      `${CM_BATCH1_BASE}/complaints/${encodeURIComponent(complaintId)}/intake-escalation/decision`,
    intakeEscalationRequest: (complaintId: string) =>
      `${CM_BATCH1_BASE}/complaints/${encodeURIComponent(complaintId)}/intake-escalation/request`,
    hqAccept: (complaintId: string) =>
      `${CM_BATCH1_BASE}/complaints/${encodeURIComponent(complaintId)}/hq-accept`,
    hqAcceptAndSchedule: (complaintId: string) =>
      `${CM_BATCH1_BASE}/complaints/${encodeURIComponent(complaintId)}/hq-accept-and-schedule`,
    hqReturn: (complaintId: string) =>
      `${CM_BATCH1_BASE}/complaints/${encodeURIComponent(complaintId)}/hq-return`,
    hqScheduleArrival: (complaintId: string) =>
      `${CM_BATCH1_BASE}/complaints/${encodeURIComponent(complaintId)}/hq-schedule-arrival`,
    userWorkStats: (userId: string) =>
      `${CM_BATCH1_BASE}/complaints/work-stats/${encodeURIComponent(userId)}`,
    duplicatesCheck: `${CM_BATCH1_BASE}/duplicates/check`,
    duplicatesDecisions: `${CM_BATCH1_BASE}/duplicates/decisions`,
    attachmentsTransfer: `${CM_BATCH1_BASE}/attachments/transfer`,
    supervisorQueue: `${CM_BATCH1_BASE}/supervisor/queue`,
  } as const;
}

export function buildCmBatch1CreateHeaders(
  options: CmBatch1CreateComplaintOptions = {},
): Record<string, string> {
  const headers: Record<string, string> = {};
  const idempotencyKey = options.idempotencyKey?.trim();
  const channelMessageId = options.channelMessageId?.trim();
  if (idempotencyKey) {
    headers["Idempotency-Key"] = idempotencyKey;
  }
  if (channelMessageId) {
    headers["X-Channel-Message-Id"] = channelMessageId;
  }
  return headers;
}
