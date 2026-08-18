/**
 * Case-detail presentation for a parent complaint on the HQ path.
 * Case status stays Mode A (no ESCALATED); grouping/copy is presentation only.
 */

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
