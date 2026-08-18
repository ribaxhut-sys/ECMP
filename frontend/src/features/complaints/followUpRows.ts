/**
 * Tindak lanjut — Case-only work list. Presentation composition over
 * API-514 / API-536. Identity is caseNumber; parent complaint stays in
 * its own column. Status/sort inherit the parent complaint's HQ phase
 * when the complaint is on the HQ path.
 */
import type { CmBatch1ComplaintResponse } from "@/lib/api";
import type { CmCaseSummary } from "@/lib/api/cmCase";
import { officerDisplayName } from "./officerDisplayName";
import { resolveHqPathPhase } from "./penangananGroups";

/** Sort bucket, lowest first (approval → HQ accept → unscheduled → scheduled → returned → branch). */
export type FollowUpStatusKey =
  | "awaitingApproval"
  | "hqAwaitingAccept"
  | "hqAcceptedUnscheduled"
  | "hqScheduled"
  | "returnedToBranch"
  | "caseWorking"
  | "caseNew";

const STATUS_RANK: Record<FollowUpStatusKey, number> = {
  awaitingApproval: 0,
  hqAwaitingAccept: 1,
  hqAcceptedUnscheduled: 2,
  hqScheduled: 3,
  returnedToBranch: 4,
  caseWorking: 5,
  caseNew: 5,
};

export interface FollowUpRow {
  key: string;
  /** Always the Case number. */
  number: string;
  complaintId: string;
  caseId: string;
  parentComplaintId: string;
  parentComplaintNumber: string | null;
  statusKey: FollowUpStatusKey;
  createdAt: string | null;
  hqArrivalDate: string | null;
  hqArrivalTime: string | null;
  handlerName: string | null;
}

const CASE_TERMINAL_STATUSES = new Set(["CLOSED", "RESOLVED", "CANCELLED"]);

/** Statuses reported as "at/toward Pusat" beyond the Mode A PATCH subset. */
const CASE_HQ_STATUSES = new Set(["ESCALATED", "PENDING"]);

function complaintDispositionStatusKey(
  parent: CmBatch1ComplaintResponse | undefined,
): FollowUpStatusKey | null {
  const phase = resolveHqPathPhase({
    intakeDisposition: parent?.intakeDisposition,
    hqAcceptedAt: parent?.hqAcceptedAt,
  });
  switch (phase) {
    case "pending_approval":
      return "awaitingApproval";
    case "awaiting_accept":
      return "hqAwaitingAccept";
    case "accepted_unscheduled":
      return "hqAcceptedUnscheduled";
    case "scheduled":
      return "hqScheduled";
    default:
      break;
  }
  const d = (parent?.intakeDisposition || "").trim().toUpperCase();
  if (d === "RETURNED_TO_BRANCH") return "returnedToBranch";
  return null;
}

function caseStatusKey(
  status: string | null | undefined,
  parent: CmBatch1ComplaintResponse | undefined,
): FollowUpStatusKey {
  const fromComplaint = complaintDispositionStatusKey(parent);
  if (fromComplaint) return fromComplaint;
  const s = (status || "").trim().toUpperCase();
  if (CASE_HQ_STATUSES.has(s)) return "hqAwaitingAccept";
  if (s === "CREATED") return "caseNew";
  return "caseWorking";
}

/** Cases considered active for Tindak lanjut (default view excludes terminal statuses). */
export function isActiveCaseStatus(status: string | null | undefined): boolean {
  const s = (status || "").trim().toUpperCase();
  return s.length > 0 && !CASE_TERMINAL_STATUSES.has(s);
}

function caseRow(
  c: CmCaseSummary,
  complaintById: ReadonlyMap<string, CmBatch1ComplaintResponse>,
): FollowUpRow {
  const parent = complaintById.get(c.complaintId);
  const parentNumber =
    parent?.complaintNumber?.trim() || c.complaintNumber?.trim() || null;
  const arrivalDate = parent?.hqArrivalDate?.trim() || null;
  const arrivalTime = parent?.hqArrivalTime?.trim() || null;
  return {
    key: `case:${c.caseId}`,
    number: c.caseNumber,
    complaintId: c.complaintId,
    caseId: c.caseId,
    parentComplaintId: c.complaintId,
    parentComplaintNumber: parentNumber,
    statusKey: caseStatusKey(c.status, parent),
    createdAt: c.createdAt ?? null,
    hqArrivalDate: arrivalDate,
    hqArrivalTime: arrivalTime,
    handlerName: officerDisplayName(c.handlingClaimedByName),
  };
}

/**
 * Build the Tindak lanjut row set from already-fetched Aggregate responses.
 * Complaints without a visible Case are omitted (not invented).
 */
export function buildFollowUpRows(input: {
  complaints: readonly CmBatch1ComplaintResponse[];
  allCases: readonly CmCaseSummary[];
}): FollowUpRow[] {
  const complaintById = new Map<string, CmBatch1ComplaintResponse>();
  for (const c of input.complaints) {
    complaintById.set(c.complaintId, c);
  }

  const rows: FollowUpRow[] = [];
  for (const c of input.allCases) {
    if (!isActiveCaseStatus(c.status)) continue;
    rows.push(caseRow(c, complaintById));
  }
  return sortFollowUpRows(rows);
}

/** DEC-025 — Tindak lanjut opens CM Case detail, not Foundation. */
export function followUpRowHref(row: Pick<FollowUpRow, "caseId">): string {
  return `/complaints/cm/cases/${encodeURIComponent(row.caseId)}`;
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
