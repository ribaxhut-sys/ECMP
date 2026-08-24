/**
 * Batch-1 HQ intake UI gates (Cabang→Pusat lab) — pure helpers.
 *
 * Mirrors backend `principal_may_perform_hq_intake_action` /
 * `require_hq_intake_action` so Confirmation buttons do not invent a second
 * AuthZ rule. Not DEC-F4 Case APIs (API-520…).
 */

import {
  PUSAT_UNIT_ROOT_CODES,
  isPusatUnitCode,
  resolveDefaultHqScheduleDestinationUnitCode,
} from "@/shared/utils";

import { isHqIntakeDisposition } from "./penangananGroups";
import { isCaseSummaryEvent } from "./complaintHistoryScope";

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

/** Matches backend visibility.DEFAULT_PUSAT_UNIT_CODES (roots only). */
export const CM_BATCH1_PUSAT_UNIT_CODES = PUSAT_UNIT_ROOT_CODES;

const HQ_REVIEW_ROLE_SET = new Set<string>(CM_BATCH1_HQ_REVIEW_ROLES);
const PUSAT_AGENT_ROLE_SET = new Set<string>(CM_BATCH1_PUSAT_AGENT_ROLES);

/** Root or Pusat sub-unit (PUSAT-CRO, PUSAT-SUBAN-…) — see shared helper. */
export const isCmBatch1PusatUnitCode = isPusatUnitCode;

/** Re-export — HQ schedule door is CRO only (no UI pick). */
export {
  DEFAULT_HQ_SCHEDULE_DESTINATION_UNIT_CODE,
  isHqScheduleDestinationUnitCode,
  resolveDefaultHqScheduleDestinationUnitCode,
} from "@/shared/utils";

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
  showHqComplete: boolean;
  showBranchNotifyBanner: boolean;
}

const HQ_OPEN_STATUSES = new Set(["REGISTERED", "IN_PROGRESS"]);

function isHqOpenStatus(status: string | null | undefined): boolean {
  return HQ_OPEN_STATUSES.has((status || "").trim().toUpperCase());
}

export function resolveCmBatch1HqActionVisibility(
  snapshot: CmBatch1HqActionSnapshot,
  canHqReview: boolean,
): CmBatch1HqActionVisibility {
  const status = (snapshot.status || "").toUpperCase();
  const disposition = (snapshot.intakeDisposition || "").toUpperCase();
  const hqAccepted = Boolean(snapshot.hqAcceptedAt);
  const approvedEscalation =
    isHqOpenStatus(status) && disposition === "ESCALATE_APPROVED";
  const hqScheduled = isHqOpenStatus(status) && disposition === "HQ_SCHEDULED";
  const showHqReschedule =
    canHqReview && hqAccepted && (approvedEscalation || hqScheduled);
  return {
    approvedEscalation,
    hqScheduled,
    showHqAcceptAndSchedule: approvedEscalation && canHqReview && !hqAccepted,
    showHqReturn: approvedEscalation && canHqReview && !hqAccepted,
    showHqReschedule,
    showHqComplete: showHqReschedule,
    // Slot copy lives on PageHeader + Penanganan card — do not repeat a banner.
    showBranchNotifyBanner: false,
  };
}

export interface CmBatch1BranchEscalationCtaInput {
  status: string | null | undefined;
  intakeDisposition: string | null | undefined;
  hqAcceptedAt: string | null | undefined;
  canDecideEscalation: boolean;
  canRequestEscalation: boolean;
  intakeClosed: boolean;
  isHqReviewer: boolean;
  isPusatUnitMember: boolean;
  intakeEscalateQuery: boolean;
  /** Bound Case exists — confirmation hides cancel; Case detail keeps it. */
  hasBoundCase?: boolean;
}

export interface CmBatch1BranchEscalationCtas {
  pendingEscalation: boolean;
  showSupervisorActions: boolean;
  showCancelEscalation: boolean;
  showReRequestEscalation: boolean;
  showManageCases: boolean;
}

/**
 * Branch confirmation CTAs. Batalkan Eskalasi on this page only when no Case
 * exists yet; Case detail is the CTA once a bound Case is present.
 * hqAcceptedAt still blocks. Tangani pengaduan stays off the HQ path.
 */
export function resolveCmBatch1BranchEscalationCtas(
  input: CmBatch1BranchEscalationCtaInput,
): CmBatch1BranchEscalationCtas {
  const status = (input.status || "").trim().toUpperCase();
  const disposition = (input.intakeDisposition || "").trim().toUpperCase();
  const hqAccepted = Boolean(input.hqAcceptedAt);
  const closed =
    input.intakeClosed || status === "CLOSED" || disposition === "BRANCH_CLOSED";
  const pendingEscalation =
    disposition === "ESCALATE_PENDING_APPROVAL" && status !== "CLOSED";
  const onHqPath = isHqIntakeDisposition(disposition);
  const showCancelEscalation =
    input.canDecideEscalation &&
    disposition === "ESCALATE_APPROVED" &&
    !hqAccepted &&
    status !== "CLOSED" &&
    !input.hasBoundCase;
  return {
    pendingEscalation,
    showSupervisorActions: pendingEscalation && input.canDecideEscalation,
    showCancelEscalation,
    // DEC-029: re-request from the parent complaint is retired.
    showReRequestEscalation: false,
    showManageCases:
      !closed &&
      !onHqPath &&
      !pendingEscalation &&
      !input.intakeEscalateQuery &&
      !input.isHqReviewer &&
      !input.isPusatUnitMember,
  };
}

/**
 * Bottom "Tangani pengaduan" on the parent. Intake HQ path already clears
 * showManageCases. Case-level DEC-029 escalate leaves the parent off that
 * path, so hide the CTA when the only remaining work is already at Pusat.
 * Sibling branch Cases (openCount > 0) may still be handled.
 */
export function showBranchHandleComplaintCta(input: {
  showManageCases: boolean;
  loading: boolean;
  handlingClaimedBy?: string | null;
  openCount: number;
  pusatCount: number;
}): boolean {
  if (!input.showManageCases || input.loading) return false;
  if (input.handlingClaimedBy) return false;
  if (input.pusatCount > 0 && input.openCount === 0) return false;
  return true;
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
  if (disposition === "HQ_CLOSED") {
    codes.push("HQ_COMPLETED");
  }
  return codes;
}

/**
 * Priority on the intake log is only for actions where the operator chose it
 * (Daftarkan / eskalasi). Branch close-at-intake never collects priority.
 */
export function intakeHistoryShowsPriority(
  eventCode: string,
  intakeDisposition: string | null | undefined,
): boolean {
  const code = eventCode.trim().toUpperCase();
  const disposition = (intakeDisposition || "").trim().toUpperCase();
  if (code === "BRANCH_CLOSED") return false;
  if (code === "REGISTERED" && disposition === "BRANCH_CLOSED") return false;
  return true;
}

/**
 * Catatan on the complaint log: REGISTERED / HQ / eskalasi.
 * BRANCH_CLOSED is status-only. Case milestone notes belong on the Case page
 * (BR-017) — keep the one-line CASE_CREATED / CLOSED / RESOLVED / CANCELLED.
 */
export function intakeHistoryShowsNote(eventCode: string): boolean {
  const code = eventCode.trim().toUpperCase();
  if (code === "BRANCH_CLOSED") return false;
  if (isCaseSummaryEvent(code)) return false;
  return true;
}

const CLOSE_EVENT_CODES = new Set([
  "BRANCH_CLOSED",
  "CASE_CLOSED",
  "CASE_RESOLVED",
  "HQ_COMPLETED",
]);

export function intakeHistoryIsCloseEvent(eventCode: string): boolean {
  return CLOSE_EVENT_CODES.has(eventCode.trim().toUpperCase());
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
  /**
   * HQ CRO destination — still required on the API payload, but the UI
   * auto-fills CRO Pusat (no picker). Empty string fails readiness.
   */
  destinationUnitId: string;
}): boolean {
  return (
    Boolean(
      input.arrivalDate.trim() &&
        input.arrivalTime.trim() &&
        input.destinationUnitId.trim(),
    ) && isCmBatch1HqNoteReady(input.arrivalNote)
  );
}

/** Fixed display label for the auto-bound HQ CRO destination. */
export function hqCroDestinationDisplayLabel(
  units: readonly { code: string; name?: string | null }[],
): string {
  const code = resolveDefaultHqScheduleDestinationUnitCode(units);
  const match = units.find(
    (unit) => unit.code.trim().toUpperCase() === code.toUpperCase(),
  );
  const name = match?.name?.trim();
  return name ? `${code} — ${name}` : code;
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
