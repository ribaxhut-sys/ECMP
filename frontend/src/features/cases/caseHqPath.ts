/**
 * Case-detail presentation for a parent complaint on the HQ path.
 * Case status stays Mode A (no ESCALATED); grouping/copy is presentation only.
 */

import {
  canCmBatch1HqReview,
  isCmBatch1PusatUnitCode,
  resolveCmBatch1BranchEscalationCtas,
} from "@/features/complaints/cmBatch1HqActions";
import {
  hqPathCopyKeys,
  isHqIntakeDisposition,
  resolveHqPathPhase,
  type HqPathCopyKeys,
  type HqPathPhase,
} from "@/features/complaints/penangananGroups";

const ADMIN_ROLES = new Set(["ADMIN", "ADMINISTRATOR", "SUPER_ADMIN"]);

export function resolveCaseHqPath(input: {
  intakeDisposition?: string | null;
  hqAcceptedAt?: string | null;
}): {
  onHqPath: boolean;
  phase: HqPathPhase | null;
  copy: HqPathCopyKeys | null;
} {
  const phase = resolveHqPathPhase({
    intakeDisposition: input.intakeDisposition,
    hqAcceptedAt: input.hqAcceptedAt,
  });
  return {
    onHqPath: isHqIntakeDisposition(input.intakeDisposition),
    phase,
    copy: phase ? hqPathCopyKeys(phase) : null,
  };
}

/** True when the caller may work a Case that cabang already sent to Pusat. */
export function actorMayHandleEscalatedCase(input: {
  roles: readonly string[];
  hasPermission: (permission: string) => boolean;
  unitCode: string | null | undefined;
}): boolean {
  if (isCmBatch1PusatUnitCode(input.unitCode)) return true;
  if (canCmBatch1HqReview(input)) return true;
  return input.roles.some((role) => ADMIN_ROLES.has((role || "").toUpperCase()));
}

/** Hide cabang resolve/reassign/claim while this Case is with Pusat
 * or the parent is still on the HQ path (and not already returned). */
export function hideCaseBranchWorkActions(
  onHqPath: boolean,
  caseStatus: string | null | undefined,
  escalatedToPusat = false,
  actorIsPusat = false,
  parentReturnedToBranch = false,
): boolean {
  const status = (caseStatus || "").trim().toUpperCase();
  if (status === "RESOLVED" || status === "CLOSED" || status === "CANCELLED") {
    return false;
  }
  if (parentReturnedToBranch) {
    return escalatedToPusat && !actorIsPusat;
  }
  if (onHqPath) return true;
  if (escalatedToPusat && !actorIsPusat) return true;
  return false;
}

/**
 * Case-page entry for Batalkan Eskalasi — same API-515 gate as confirmation.
 * Cancels the parent complaint HQ path, not this Case alone.
 * Do not pass hasBoundCase: this page is the CTA once a Case exists.
 */
export function showCaseCancelEscalation(input: {
  canDecideEscalation: boolean;
  complaintStatus?: string | null;
  intakeDisposition?: string | null;
  hqAcceptedAt?: string | null;
}): boolean {
  return resolveCmBatch1BranchEscalationCtas({
    status: input.complaintStatus,
    intakeDisposition: input.intakeDisposition,
    hqAcceptedAt: input.hqAcceptedAt,
    canDecideEscalation: input.canDecideEscalation,
    canRequestEscalation: false,
    intakeClosed: false,
    isHqReviewer: false,
    isPusatUnitMember: false,
    intakeEscalateQuery: false,
  }).showCancelEscalation;
}

/** DEC-029 Case-level Batalkan Eskalasi — only before Pusat accepts or claims. */
export function showCaseLevelCancelEscalation(input: {
  escalatedToPusat: boolean;
  handlingClaimedBy?: string | null;
  canCancel: boolean;
  actorIsPusat: boolean;
  caseStatus?: string | null;
  hqAcceptedAt?: string | null;
  intakeDisposition?: string | null;
}): boolean {
  if (!input.canCancel || !input.escalatedToPusat || input.actorIsPusat) {
    return false;
  }
  if ((input.handlingClaimedBy || "").trim()) return false;
  if ((input.hqAcceptedAt || "").trim()) return false;
  const disposition = (input.intakeDisposition || "").trim().toUpperCase();
  if (disposition === "HQ_SCHEDULED") return false;
  const status = (input.caseStatus || "").trim().toUpperCase();
  if (status === "CLOSED" || status === "CANCELLED" || status === "RESOLVED") {
    return false;
  }
  return true;
}

/** API-521 — Pusat returns escalated Case to originating branch. */
export function showCaseReturnEscalation(input: {
  escalatedToPusat: boolean;
  actorIsPusat: boolean;
  canUpdate: boolean;
  caseStatus?: string | null;
}): boolean {
  if (!input.canUpdate || !input.escalatedToPusat || !input.actorIsPusat) {
    return false;
  }
  const status = (input.caseStatus || "").trim().toUpperCase();
  if (status === "CLOSED" || status === "CANCELLED" || status === "RESOLVED") {
    return false;
  }
  return true;
}
