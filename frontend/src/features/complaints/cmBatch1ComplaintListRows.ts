import type { CmBatch1ComplaintResponse, CmCaseSummary } from "@/lib/api";

export type CmBatch1ComplaintListCasesState =
  | "loading"
  | "error"
  | "empty"
  | "ready";

export type CmBatch1ComplaintListRow = {
  key: string;
  complaint: CmBatch1ComplaintResponse;
  caseItem: CmCaseSummary | null;
  casesState: CmBatch1ComplaintListCasesState;
};

export type CmBatch1ComplaintListCases =
  | "loading"
  | "error"
  | CmCaseSummary[];

/**
 * Operator work list: one row per Case. Complaints without a Case stay as a
 * single row so intake that is not yet handled is not dropped (DEC-026).
 *
 * ``loading`` / ``error`` keep a parent placeholder — do not label them as
 * "no case yet" (that is reserved for a finished empty fetch).
 */
export function expandComplaintsToCaseRows(
  complaints: readonly CmBatch1ComplaintResponse[],
  casesByComplaint: Record<string, CmBatch1ComplaintListCases>,
): CmBatch1ComplaintListRow[] {
  const rows: CmBatch1ComplaintListRow[] = [];
  for (const complaint of complaints) {
    const entry = casesByComplaint[complaint.complaintId];
    if (entry === undefined || entry === "loading") {
      rows.push({
        key: complaint.complaintId,
        complaint,
        caseItem: null,
        casesState: "loading",
      });
      continue;
    }
    if (entry === "error") {
      rows.push({
        key: complaint.complaintId,
        complaint,
        caseItem: null,
        casesState: "error",
      });
      continue;
    }
    if (entry.length === 0) {
      rows.push({
        key: complaint.complaintId,
        complaint,
        caseItem: null,
        casesState: "empty",
      });
      continue;
    }
    for (const caseItem of entry) {
      rows.push({
        key: caseItem.caseId,
        complaint,
        caseItem,
        casesState: "ready",
      });
    }
  }
  return rows;
}
