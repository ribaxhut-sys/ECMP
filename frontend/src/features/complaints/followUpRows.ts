/**
 * Tindak lanjut — presentation-only union of Case (Penanganan) and Complaint
 * (Pengaduan) rows. No new API surface; consumes API-514 / API-536 responses
 * as already shaped by fetchCmBatch1Complaints / fetchCmCases.
 */
import type { CmBatch1ComplaintResponse } from "@/lib/api";
import type { CmCaseSummary } from "@/lib/api/cmCase";
import { isHqIntakeDisposition } from "./penangananGroups";

export type FollowUpRowKind = "case" | "complaint";

/** Sort bucket, lowest first (BR: Menunggu persetujuan → Pusat → dikembalikan → dikerjakan → belum ada penanganan). */
export type FollowUpStatusKey =
  | "awaitingApproval"
  | "hqPath"
  | "returnedToBranch"
  | "caseWorking"
  | "caseNew"
  | "noHandling";

const STATUS_RANK: Record<FollowUpStatusKey, number> = {
  awaitingApproval: 0,
  hqPath: 1,
  returnedToBranch: 2,
  caseWorking: 3,
  caseNew: 3,
  noHandling: 4,
};

export interface FollowUpRow {
  key: string;
  kind: FollowUpRowKind;
  /** caseNumber for Case rows, complaintNumber for Complaint rows. */
  number: string;
  complaintId: string;
  caseId?: string;
  parentComplaintId: string | null;
  parentComplaintNumber: string | null;
  statusKey: FollowUpStatusKey;
  createdAt: string | null;
}

const CASE_TERMINAL_STATUSES = new Set(["CLOSED", "RESOLVED", "CANCELLED"]);

/** Statuses reported as "at/toward Pusat" beyond the Mode A PATCH subset. */
const CASE_HQ_STATUSES = new Set(["ESCALATED", "PENDING"]);

function caseStatusKey(status: string | null | undefined): FollowUpStatusKey {
  const s = (status || "").trim().toUpperCase();
  if (CASE_HQ_STATUSES.has(s)) return "hqPath";
  if (s === "CREATED") return "caseNew";
  return "caseWorking";
}

/** Cases considered active for Tindak lanjut (default view excludes terminal statuses). */
export function isActiveCaseStatus(status: string | null | undefined): boolean {
  const s = (status || "").trim().toUpperCase();
  return s.length > 0 && !CASE_TERMINAL_STATUSES.has(s);
}

function complaintDispositionStatusKey(
  disposition: string | null | undefined,
): FollowUpStatusKey | null {
  const d = (disposition || "").trim().toUpperCase();
  if (d === "ESCALATE_PENDING_APPROVAL") return "awaitingApproval";
  if (isHqIntakeDisposition(d)) return "hqPath";
  if (d === "RETURNED_TO_BRANCH") return "returnedToBranch";
  return null;
}

/**
 * Complaint row eligible for Tindak lanjut iff: not CLOSED, not BRANCH_CLOSED,
 * and (no visible Case for it OR an active intake disposition).
 */
export function isFollowUpComplaint(
  complaint: Pick<CmBatch1ComplaintResponse, "status" | "intakeDisposition">,
  hasVisibleCase: boolean,
): boolean {
  if (complaint.status === "CLOSED") return false;
  if ((complaint.intakeDisposition || "").trim().toUpperCase() === "BRANCH_CLOSED") {
    return false;
  }
  const dispositionKey = complaintDispositionStatusKey(complaint.intakeDisposition);
  return dispositionKey !== null || !hasVisibleCase;
}

function caseRow(
  c: CmCaseSummary,
  complaintNumberById: ReadonlyMap<string, string>,
): FollowUpRow {
  return {
    key: `case:${c.caseId}`,
    kind: "case",
    number: c.caseNumber,
    complaintId: c.complaintId,
    caseId: c.caseId,
    parentComplaintId: c.complaintId,
    parentComplaintNumber: complaintNumberById.get(c.complaintId) ?? null,
    statusKey: caseStatusKey(c.status),
    createdAt: c.createdAt ?? null,
  };
}

function complaintRow(c: CmBatch1ComplaintResponse): FollowUpRow {
  return {
    key: `complaint:${c.complaintId}`,
    kind: "complaint",
    number: c.complaintNumber,
    complaintId: c.complaintId,
    parentComplaintId: null,
    parentComplaintNumber: null,
    statusKey: complaintDispositionStatusKey(c.intakeDisposition) ?? "noHandling",
    createdAt: c.createdAt ?? null,
  };
}

/**
 * Build the union Tindak lanjut row set from already-fetched Aggregate
 * responses. `allCases` should be the unfiltered Case list (any status) so
 * "no visible Case" can be determined correctly for complaint eligibility.
 */
export function buildFollowUpRows(input: {
  complaints: readonly CmBatch1ComplaintResponse[];
  allCases: readonly CmCaseSummary[];
}): FollowUpRow[] {
  const complaintNumberById = new Map<string, string>();
  for (const c of input.complaints) {
    complaintNumberById.set(c.complaintId, c.complaintNumber);
  }
  const complaintIdsWithCase = new Set(input.allCases.map((c) => c.complaintId));

  const rows: FollowUpRow[] = [];
  for (const c of input.allCases) {
    if (!isActiveCaseStatus(c.status)) continue;
    rows.push(caseRow(c, complaintNumberById));
  }
  for (const c of input.complaints) {
    if (!isFollowUpComplaint(c, complaintIdsWithCase.has(c.complaintId))) continue;
    rows.push(complaintRow(c));
  }
  return sortFollowUpRows(rows);
}

export function sortFollowUpRows(rows: readonly FollowUpRow[]): FollowUpRow[] {
  return [...rows].sort((a, b) => {
    const rankDiff = STATUS_RANK[a.statusKey] - STATUS_RANK[b.statusKey];
    if (rankDiff !== 0) return rankDiff;
    const aTime = a.createdAt ? Date.parse(a.createdAt) : Number.NEGATIVE_INFINITY;
    const bTime = b.createdAt ? Date.parse(b.createdAt) : Number.NEGATIVE_INFINITY;
    return bTime - aTime;
  });
}
