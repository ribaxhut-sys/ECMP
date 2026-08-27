import type { BadgeTone } from "@/shared/ui";

export const CASE_CLOSE_EVENT_CODES = new Set(["CASE_CLOSED", "CASE_RESOLVED"]);

/**
 * Dual-acceptance (Owner / Handling Unit) is the Internal Complaint closure
 * model. On taxpayer CM Case history those codes confuse operators ("Pemilik
 * menerima" ≠ WP). Keep them out of the WP Case log; CLOSE/RESOLVED remain.
 */
export const WP_CASE_HISTORY_HIDDEN_CODES = new Set([
  "CASE_OWNER_ACCEPTED",
  "CASE_OWNER_REJECTED",
  "CASE_HANDLING_UNIT_ACCEPTED",
  "CASE_HANDLING_UNIT_REJECTED",
]);

export const CASE_HISTORY_TONES: Record<string, BadgeTone> = {
  CASE_CREATED: "primary",
  CASE_WORK_STARTED: "info",
  CASE_ASSIGNED: "primary",
  CASE_CANCELLED: "neutral",
  CASE_STATUS_CHANGED: "neutral",
  CASE_CLOSED: "success",
  CASE_RESOLVED: "success",
  HANDLING_CONTINUED: "primary",
  HANDLING_TAKEN_OVER: "primary",
  CASE_HANDLING_UNIT_ACCEPTED: "success",
  CASE_OWNER_ACCEPTED: "success",
  CASE_HANDLING_UNIT_REJECTED: "danger",
  CASE_OWNER_REJECTED: "danger",
  RESOLUTION_UPDATED: "info",
  ATTACHMENT_BOUND: "neutral",
  ATTACHMENT_UPLOADED: "neutral",
  HQ_ACCEPTED: "success",
  HQ_ARRIVAL_SCHEDULED: "info",
  HQ_COMPLETED: "success",
  HQ_RETURNED: "warning",
  CASE_ESCALATED_TO_PUSAT: "warning",
  CASE_ESCALATION_TO_PUSAT_CANCELLED: "neutral",
  CASE_ESCALATION_RETURNED: "warning",
  OTHER: "neutral",
};

/** `cases.*` message keys for Case history event badges. */
export const CASE_HISTORY_LABEL_KEYS: Record<string, string> = {
  CASE_CREATED: "eventCaseCreated",
  CASE_WORK_STARTED: "eventCaseWorkStarted",
  CASE_ASSIGNED: "eventCaseAssigned",
  CASE_CANCELLED: "eventCaseCancelled",
  CASE_STATUS_CHANGED: "eventCaseStatusChanged",
  CASE_CLOSED: "eventCaseClosed",
  CASE_RESOLVED: "eventCaseResolved",
  HANDLING_CONTINUED: "eventHandlingContinued",
  HANDLING_TAKEN_OVER: "eventHandlingTakenOver",
  CASE_HANDLING_UNIT_ACCEPTED: "eventHandlingUnitAccepted",
  CASE_OWNER_ACCEPTED: "eventOwnerAccepted",
  CASE_HANDLING_UNIT_REJECTED: "eventHandlingUnitRejected",
  CASE_OWNER_REJECTED: "eventOwnerRejected",
  RESOLUTION_UPDATED: "eventResolutionUpdated",
  ATTACHMENT_BOUND: "eventAttachmentBound",
  ATTACHMENT_UPLOADED: "eventAttachmentUploaded",
  HQ_ACCEPTED: "eventHqAccepted",
  HQ_ARRIVAL_SCHEDULED: "eventHqScheduled",
  HQ_COMPLETED: "eventHqCompleted",
  HQ_RETURNED: "eventHqReturned",
  CASE_ESCALATED_TO_PUSAT: "eventCaseEscalatedToPusat",
  CASE_ESCALATION_TO_PUSAT_CANCELLED: "eventCaseEscalationToPusatCancelled",
  CASE_ESCALATION_RETURNED: "eventCaseEscalationReturned",
  OTHER: "eventOther",
};

export function isCaseCloseEvent(code: string): boolean {
  return CASE_CLOSE_EVENT_CODES.has(code.trim().toUpperCase());
}

export function caseHistoryLabelKey(eventCode: string): string {
  return CASE_HISTORY_LABEL_KEYS[eventCode] ?? "eventOther";
}

const RE_ESCALATION_PRIOR_CODES = new Set([
  "CASE_ESCALATED_TO_PUSAT",
  "CASE_ESCALATION_RETURNED",
  "CASE_ESCALATION_TO_PUSAT_CANCELLED",
]);

/** Same API event as the first send; later sends after return/cancel are re-escalation. */
export function caseHistoryDisplayLabelKey(
  eventCode: string,
  priorEventCodes: readonly string[] = [],
): string {
  const code = eventCode.trim().toUpperCase();
  if (
    code === "CASE_ESCALATED_TO_PUSAT" &&
    priorEventCodes.some((prior) =>
      RE_ESCALATION_PRIOR_CODES.has((prior || "").trim().toUpperCase()),
    )
  ) {
    return "eventCaseReEscalatedToPusat";
  }
  return caseHistoryLabelKey(eventCode);
}

export function isWpCaseHistoryHidden(eventCode: string): boolean {
  return WP_CASE_HISTORY_HIDDEN_CODES.has(eventCode.trim().toUpperCase());
}

/** Taxpayer CM Case log — drop Internal dual-acceptance events. */
export function filterWpCaseHistoryEntries<T extends { eventCode: string }>(
  entries: T[],
): T[] {
  return entries.filter((entry) => !isWpCaseHistoryHidden(entry.eventCode));
}
