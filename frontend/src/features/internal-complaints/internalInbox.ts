import { isPusatUnitCode } from "@/shared/utils/pusatUnits";

/** Incoming queue at the current handling unit (CREATED/ASSIGNED). */
export const INTERNAL_INBOX_STATUSES = ["CREATED", "ASSIGNED"] as const;

/** Full list — used when the action-needed badge is zero. */
export const INTERNAL_LIST_HREF = "/internal/complaints";

/** Sidebar work door — tickets waiting on the signed-in unit. */
export const INTERNAL_ACTION_HREF = "/internal/complaints?needsAction=1";

/** @deprecated Prefer INTERNAL_ACTION_HREF; incoming-only remains needsReceive. */
export const INTERNAL_INBOX_HREF = INTERNAL_ACTION_HREF;

export function isInternalInboxStatus(status: string): boolean {
  return (INTERNAL_INBOX_STATUSES as readonly string[]).includes(status);
}

/**
 * Whether a ticket is incoming for the signed-in unit (same rule as needsReceive).
 * Cabang: handling unit is the branch. Pusat: handling is any Pusat unit.
 */
export function isIncomingInternalComplaint(
  row: { status: string; handlingUnitId: string },
  actorUnitCode: string | null | undefined,
): boolean {
  if (!isInternalInboxStatus(row.status)) return false;
  const unit = (actorUnitCode ?? "").trim();
  if (!unit) return false;
  if (isPusatUnitCode(unit)) {
    return isPusatUnitCode(row.handlingUnitId);
  }
  return row.handlingUnitId === unit;
}

function unitIsActor(candidate: string, actorUnitCode: string): boolean {
  if (isPusatUnitCode(actorUnitCode)) {
    return isPusatUnitCode(candidate);
  }
  return candidate === actorUnitCode;
}

/**
 * Work waiting on this unit (API-551 / needsAction).
 * Login Cabang: incoming, owner usulan hidup, close-gate.
 * Login Pusat: incoming, rebound after tolak/kembalikan, withdraw, close-gate.
 */
export function isActionNeededInternalComplaint(
  row: {
    status: string;
    handlingUnitId: string;
    ownerUnitId: string;
    resolutionStatus?: string | null;
    withdrawRequestStatus?: string | null;
  },
  actorUnitCode: string | null | undefined,
): boolean {
  if (isIncomingInternalComplaint(row, actorUnitCode)) return true;
  const unit = (actorUnitCode ?? "").trim();
  if (!unit) return false;
  const ownerIsActor = unitIsActor(row.ownerUnitId, unit);
  const handlingIsActor = unitIsActor(row.handlingUnitId, unit);
  const latest = (row.resolutionStatus || "").trim().toUpperCase();
  if (
    row.status === "IN_PROGRESS" &&
    ownerIsActor &&
    latest === "PENDING_APPROVAL"
  ) {
    return true;
  }
  if (
    row.status === "IN_PROGRESS" &&
    handlingIsActor &&
    (latest === "REJECTED" || latest === "ACCEPTED")
  ) {
    return true;
  }
  if (
    (row.withdrawRequestStatus || "").trim().toUpperCase() === "PENDING" &&
    handlingIsActor
  ) {
    return true;
  }
  if (row.status === "RESOLVED" && (ownerIsActor || handlingIsActor)) {
    return true;
  }
  return false;
}

export function internalComplaintsNavHref(actionCount: number): string {
  return actionCount > 0 ? INTERNAL_ACTION_HREF : INTERNAL_LIST_HREF;
}
