/**
 * Batch-1 HQ intake UI gates (Cabang→Pusat lab) — pure helpers.
 *
 * Mirrors backend `principal_may_perform_hq_intake_action` /
 * `require_hq_intake_action` so Confirmation buttons do not invent a second
 * AuthZ rule. Not DEC-F4 Case APIs (API-520…).
 */

/** Matches backend gates._ESCALATION_REVIEW_ROLES */
export const CM_BATCH1_HQ_REVIEW_ROLES = [
  "HO_SCHEDULER",
  "HEAD_OFFICE_SCHEDULER",
  "SCHEDULER",
  "ADMIN",
  "ADMINISTRATOR",
] as const;

/** Matches backend gates._PUSAT_AGENT_ROLES */
export const CM_BATCH1_PUSAT_AGENT_ROLES = [
  "AGENT",
  "CS_AGENT",
  "HANDLER",
  "BRANCH_OFFICER",
] as const;

/** Matches backend visibility.DEFAULT_PUSAT_UNIT_CODES */
export const CM_BATCH1_PUSAT_UNIT_CODES = [
  "PUSAT",
  "HO",
  "HEAD_OFFICE",
  "HEAD-OFFICE",
] as const;

const HQ_REVIEW_ROLE_SET = new Set<string>(CM_BATCH1_HQ_REVIEW_ROLES);
const PUSAT_AGENT_ROLE_SET = new Set<string>(CM_BATCH1_PUSAT_AGENT_ROLES);
const PUSAT_UNIT_SET = new Set<string>(CM_BATCH1_PUSAT_UNIT_CODES);

export function isCmBatch1PusatUnitCode(code: string | null | undefined): boolean {
  const normalized = (code || "").trim().toUpperCase();
  return normalized.length > 0 && PUSAT_UNIT_SET.has(normalized);
}

export function canCmBatch1HqReview(input: {
  roles: readonly string[];
  hasPermission: (permission: string) => boolean;
  unitCode: string | null | undefined;
}): boolean {
  const roles = input.roles.map((r) => (r || "").toUpperCase());
  if (
    input.hasPermission("escalations:review") &&
    roles.some((r) => HQ_REVIEW_ROLE_SET.has(r))
  ) {
    return true;
  }
  if (
    input.hasPermission("complaints:read") &&
    roles.some((r) => PUSAT_AGENT_ROLE_SET.has(r)) &&
    isCmBatch1PusatUnitCode(input.unitCode)
  ) {
    return true;
  }
  return false;
}

export interface CmBatch1HqActionSnapshot {
  status: string | null | undefined;
  intakeDisposition: string | null | undefined;
  hqAcceptedAt: string | null | undefined;
  hqArrivalDate: string | null | undefined;
  caseCreated: boolean | null | undefined;
}

export interface CmBatch1HqActionVisibility {
  approvedEscalation: boolean;
  hqScheduled: boolean;
  showHqAcceptAndSchedule: boolean;
  showHqReturn: boolean;
  showHqReschedule: boolean;
  showBranchNotifyBanner: boolean;
}

export function resolveCmBatch1HqActionVisibility(
  snapshot: CmBatch1HqActionSnapshot,
  canHqReview: boolean,
): CmBatch1HqActionVisibility {
  const status = (snapshot.status || "").toUpperCase();
  const disposition = (snapshot.intakeDisposition || "").toUpperCase();
  const hqAccepted = Boolean(snapshot.hqAcceptedAt);
  const approvedEscalation =
    status === "REGISTERED" && disposition === "ESCALATE_APPROVED";
  const hqScheduled = status === "REGISTERED" && disposition === "HQ_SCHEDULED";
  return {
    approvedEscalation,
    hqScheduled,
    showHqAcceptAndSchedule: approvedEscalation && canHqReview && !hqAccepted,
    showHqReturn: approvedEscalation && canHqReview && !hqAccepted,
    showHqReschedule:
      canHqReview && hqAccepted && (approvedEscalation || hqScheduled),
    showBranchNotifyBanner:
      hqScheduled && Boolean(snapshot.hqArrivalDate) && !canHqReview,
  };
}

export interface CmBatch1BlobEventInput {
  intakeDisposition: string | null | undefined;
  /** Blob sections already parsed by the caller (backend fields or FE parser). */
  escalationReason: string | null;
  branchResolution: string | null;
  supervisorNote: string | null;
  rejectionNote: string | null;
  cancellationNote: string | null;
  hqReturnNote: string | null | undefined;
  hqAcceptedAt: string | null | undefined;
  hqArrivalDate: string | null | undefined;
  hqArrivalTime: string | null | undefined;
  /** `?intake=closed` confirmation deep-link — branch close not yet in the blob. */
  intakeClosed: boolean;
}

/**
 * Chronological event codes reconstructed from the description blob, used when
 * the timeline read model returns nothing (legacy rows, or history endpoint
 * failure). Every code returned here must exist in the view's tone/label maps.
 */
export function cmBatch1BlobEventCodes(
  input: CmBatch1BlobEventInput,
): string[] {
  const disposition = (input.intakeDisposition ?? "").toUpperCase();
  const codes: string[] = ["REGISTERED"];
  if (input.escalationReason || disposition.startsWith("ESCALATE_")) {
    codes.push("ESCALATION_REQUESTED");
  }
  if (
    input.branchResolution ||
    input.intakeClosed ||
    disposition === "BRANCH_CLOSED"
  ) {
    codes.push("BRANCH_CLOSED");
  }
  if (input.supervisorNote || disposition === "ESCALATE_APPROVED") {
    codes.push("ESCALATION_APPROVED");
  }
  if (input.rejectionNote || disposition === "ESCALATE_REJECTED") {
    codes.push("ESCALATION_REJECTED");
  }
  if (input.cancellationNote || disposition === "ESCALATE_CANCELLED") {
    codes.push("ESCALATION_CANCELLED");
  }
  // HQ return is the event that explains why an approved escalation is back at
  // the branch — without it the blob log jumps from APPROVED to nothing.
  if (input.hqReturnNote || disposition === "RETURNED_TO_BRANCH") {
    codes.push("HQ_RETURNED");
  }
  if (input.hqAcceptedAt) codes.push("HQ_ACCEPTED");
  if (input.hqArrivalDate && input.hqArrivalTime) {
    codes.push("HQ_ARRIVAL_SCHEDULED");
  }
  return codes;
}

/** Note length floor shared with HQ return / accept-and-schedule (DEC-F4 lab OQ). */
export const CM_BATCH1_HQ_NOTE_MIN = 10;

export function isCmBatch1HqNoteReady(note: string, min = CM_BATCH1_HQ_NOTE_MIN): boolean {
  return note.trim().length >= min;
}

export function isCmBatch1HqAcceptScheduleReady(input: {
  arrivalDate: string;
  arrivalTime: string;
  arrivalNote: string;
}): boolean {
  return (
    Boolean(input.arrivalDate.trim() && input.arrivalTime.trim()) &&
    isCmBatch1HqNoteReady(input.arrivalNote)
  );
}

export function isCmBatch1HqRescheduleReady(input: {
  arrivalDate: string;
  arrivalTime: string;
  arrivalNote: string;
}): boolean {
  const note = input.arrivalNote.trim();
  return (
    Boolean(input.arrivalDate.trim() && input.arrivalTime.trim()) &&
    (!note || isCmBatch1HqNoteReady(note))
  );
}
