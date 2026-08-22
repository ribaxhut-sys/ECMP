/**
 * Case-detail presentation for a parent complaint on the HQ path.
 * Case status stays Mode A (no ESCALATED); grouping/copy is presentation only.
 */

import { resolveCmBatch1BranchEscalationCtas } from "@/features/complaints/cmBatch1HqActions";
import {
  hqPathCopyKeys,
  isHqIntakeDisposition,
  resolveHqPathPhase,
  type HqPathCopyKeys,
  type HqPathPhase,
} from "@/features/complaints/penangananGroups";

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

/** Hide cabang resolve/reassign/claim while parent is on HQ path and Case work is still open. */
export function hideCaseBranchWorkActions(
  onHqPath: boolean,
  caseStatus: string | null | undefined,
): boolean {
  if (!onHqPath) return false;
  const status = (caseStatus || "").trim().toUpperCase();
  return status !== "RESOLVED" && status !== "CLOSED" && status !== "CANCELLED";
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
