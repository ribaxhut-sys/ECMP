import type { CmBatch1ComplaintListRow } from "./cmBatch1ComplaintListRows";

const SUCCESS_CASE_STATUSES = new Set(["CLOSED", "RESOLVED"]);

function norm(value: string | null | undefined): string {
  return (value || "").trim().toUpperCase();
}

/** Cabang archive = successful closes; Pusat archive = HQ visit complete. */
export function closedArchiveIntakeDisposition(
  pusatAudience: boolean,
): "HQ_CLOSED" | "COMPLETED" {
  return pusatAudience ? "HQ_CLOSED" : "COMPLETED";
}

export function closedArchivePathLabelKey(
  intakeDisposition: string | null | undefined,
): "tagHqCompleted" | "tagBranchClosed" {
  return norm(intakeDisposition) === "HQ_CLOSED"
    ? "tagHqCompleted"
    : "tagBranchClosed";
}

/**
 * Ditutup table: successful Case rows, plus parent walk-away closes
 * that never created a Case. Hide cancelled siblings.
 */
export function keepClosedArchiveRow(row: CmBatch1ComplaintListRow): boolean {
  if (row.casesState === "loading" || row.casesState === "error") return true;
  if (!row.caseItem) return row.casesState === "empty";
  return SUCCESS_CASE_STATUSES.has(norm(row.caseItem.status));
}
