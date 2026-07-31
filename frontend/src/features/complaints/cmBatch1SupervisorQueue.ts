/**
 * Pure helpers for Batch-1 API-513 supervisor queue visibility (Mode A).
 * No React/Axios — included in FE-CI-POL coverage gates.
 *
 * Contract: later-review + no-Case aging are read-only. Status/reason are
 * pass-through (never remapped). Offset pagination is NOT in OpenAPI —
 * only `limit` caps list size.
 */

export const CM_BATCH1_KNOWN_LATER_REVIEW_REASONS = [
  "duplicate_check_degraded",
  "attachment_bind_failed",
] as const;

export type CmBatch1KnownLaterReviewReason =
  (typeof CM_BATCH1_KNOWN_LATER_REVIEW_REASONS)[number];

/** Fields the supervisor UI renders from LaterReviewWorkItem (API-513). */
export const CM_BATCH1_LATER_REVIEW_UI_FIELDS = [
  "workItemId",
  "customerId",
  "complaintId",
  "reason",
  "status",
  "createdAt",
  "ageHours",
] as const;

/** Fields the supervisor UI renders from AgingComplaintItem (API-513). */
export const CM_BATCH1_AGING_UI_FIELDS = [
  "complaintId",
  "complaintNumber",
  "customerId",
  "status",
  "subject",
  "priority",
  "createdAt",
  "ageHours",
  "caseCreated",
] as const;

export type CmBatch1ReasonTone = "danger" | "warning" | "neutral" | "info";

export function isKnownCmBatch1LaterReviewReason(reason: string): boolean {
  return (CM_BATCH1_KNOWN_LATER_REVIEW_REASONS as readonly string[]).includes(
    reason,
  );
}

/**
 * Pass-through label for work-item reason.
 * Unknown reasons stay verbatim (no synonym rewrite); badge marks unknown.
 */
export function cmBatch1LaterReviewReasonLabel(reason: string): string {
  const raw = (reason ?? "").trim();
  if (!raw) return "(empty reason)";
  if (isKnownCmBatch1LaterReviewReason(raw)) return raw;
  return raw;
}

export function cmBatch1LaterReviewReasonTone(
  reason: string,
): CmBatch1ReasonTone {
  const raw = (reason ?? "").trim();
  if (!raw || !isKnownCmBatch1LaterReviewReason(raw)) return "neutral";
  if (raw === "attachment_bind_failed") return "warning";
  if (raw === "duplicate_check_degraded") return "danger";
  return "info";
}

export function cmBatch1LaterReviewReasonIsUnknown(reason: string): boolean {
  const raw = (reason ?? "").trim();
  return !raw || !isKnownCmBatch1LaterReviewReason(raw);
}

/** Pass-through work-item / complaint status — never rewrite OPEN/CLOSED/REGISTERED. */
export function cmBatch1SupervisorStatusLabel(status: string): string {
  const raw = (status ?? "").trim();
  return raw.length > 0 ? raw : "—";
}

/**
 * Aging inclusion uses BE rule `created_at <= now - agingHours`.
 * Helper mirrors that for UI threshold badge (ageHours >= threshold).
 */
export function isCmBatch1AgingPastThreshold(
  ageHours: number,
  thresholdHours: number,
): boolean {
  if (!Number.isFinite(ageHours) || !Number.isFinite(thresholdHours)) {
    return false;
  }
  return ageHours >= thresholdHours;
}

/** OpenAPI API-513: limit only (no offset/cursor). */
export const CM_BATCH1_SUPERVISOR_QUEUE_LIMIT_MAX = 500;
export const CM_BATCH1_SUPERVISOR_QUEUE_LIMIT_DEFAULT = 100;

export function clampCmBatch1SupervisorQueueLimit(limit: number): number {
  if (!Number.isFinite(limit)) return CM_BATCH1_SUPERVISOR_QUEUE_LIMIT_DEFAULT;
  return Math.max(1, Math.min(Math.trunc(limit), CM_BATCH1_SUPERVISOR_QUEUE_LIMIT_MAX));
}
