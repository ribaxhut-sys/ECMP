/**
 * BR-017 compact vs full: the complaint page shows aggregate events plus a
 * one-line Case milestone. Case work detail belongs on the Case page.
 */

/** Case work log — hide from Riwayat Pengaduan; show on the Case page. */
export const CASE_WORK_DETAIL_EVENT_CODES = new Set([
  "CASE_WORK_STARTED",
  "CASE_ASSIGNED",
  "CASE_STATUS_CHANGED",
  "HANDLING_CONTINUED",
  "HANDLING_TAKEN_OVER",
  "CASE_HANDLING_UNIT_ACCEPTED",
  "CASE_OWNER_ACCEPTED",
  "CASE_HANDLING_UNIT_REJECTED",
  "CASE_OWNER_REJECTED",
  "RESOLUTION_UPDATED",
]);

/** One-line Case milestones that stay on the complaint summary log. */
export const CASE_SUMMARY_EVENT_CODES = new Set([
  "CASE_CREATED",
  "CASE_CLOSED",
  "CASE_RESOLVED",
  "CASE_CANCELLED",
  "CASE_ESCALATED_TO_PUSAT",
  "CASE_ESCALATION_TO_PUSAT_CANCELLED",
  "CASE_ESCALATION_RETURNED",
]);

export function isCaseWorkDetailEvent(eventCode: string): boolean {
  return CASE_WORK_DETAIL_EVENT_CODES.has(eventCode.trim().toUpperCase());
}

/** CASE_CREATED / CLOSED / RESOLVED / CANCELLED — one-line on complaint, note body on Case. */
export function isCaseSummaryEvent(eventCode: string): boolean {
  return CASE_SUMMARY_EVENT_CODES.has(eventCode.trim().toUpperCase());
}

export type CaseHistoryHint = {
  eventCode: string;
  caseNumber?: string | null;
  occurredAt: string;
};

export function latestCaseHistoryEvent(
  entries: readonly CaseHistoryHint[],
  caseNumber: string,
): CaseHistoryHint | null {
  const wanted = caseNumber.trim();
  if (!wanted) return null;
  const matched = entries.filter(
    (entry) => (entry.caseNumber || "").trim() === wanted,
  );
  if (matched.length === 0) return null;
  return matched.reduce((latest, entry) =>
    entry.occurredAt > latest.occurredAt ? entry : latest,
  );
}

/**
 * Backend `history.event_code()` for Duplicate* timeline types (API-507).
 * Complaint log badges must use these keys — never the raw `DUPLICATE_*` code.
 */
export const INTAKE_DUPLICATE_HISTORY_LABEL_KEYS: Record<string, string> = {
  DUPLICATE_FOUND: "tagDuplicateFound",
  DUPLICATE_OVERRIDDEN: "tagDuplicateOverridden",
  DUPLICATE_LINKED: "tagDuplicateLinked",
  DUPLICATE_REDIRECTED: "tagDuplicateRedirected",
  DUPLICATE_RECOMMENDED: "tagDuplicateRecommended",
  DUPLICATE_BLOCKED: "tagDuplicateBlocked",
};

/** Fallback when `IntakeDispositionRecorded` has an unmapped disposition. */
export const INTAKE_RECORDED_HISTORY_LABEL_KEY = "tagIntakeRecorded";

export const CASE_LAST_EVENT_LABEL_KEYS: Record<string, string> = {
  CASE_CREATED: "eventCaseCreated",
  CASE_WORK_STARTED: "eventCaseWorkStarted",
  CASE_ASSIGNED: "eventCaseAssigned",
  CASE_CANCELLED: "eventCaseCancelled",
  CASE_STATUS_CHANGED: "eventCaseStatusChanged",
  CASE_CLOSED: "eventCaseClosed",
  CASE_RESOLVED: "eventCaseResolved",
  CASE_ESCALATED_TO_PUSAT: "eventCaseEscalatedToPusat",
  CASE_ESCALATION_TO_PUSAT_CANCELLED: "eventCaseEscalationToPusatCancelled",
  CASE_ESCALATION_RETURNED: "eventCaseEscalationReturned",
  HANDLING_CONTINUED: "eventHandlingContinued",
  HANDLING_TAKEN_OVER: "eventHandlingTakenOver",
  CASE_HANDLING_UNIT_ACCEPTED: "eventHandlingUnitAccepted",
  CASE_OWNER_ACCEPTED: "eventOwnerAccepted",
  CASE_HANDLING_UNIT_REJECTED: "eventHandlingUnitRejected",
  CASE_OWNER_REJECTED: "eventOwnerRejected",
  RESOLUTION_UPDATED: "eventResolutionUpdated",
};
