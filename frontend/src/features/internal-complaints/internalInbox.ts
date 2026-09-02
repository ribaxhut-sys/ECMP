import { isPusatUnitCode } from "@/shared/utils/pusatUnits";

/** Incoming queue at the current handling unit (CREATED/ASSIGNED). */
export const INTERNAL_INBOX_STATUSES = ["CREATED", "ASSIGNED"] as const;

/** Sidebar work door — incoming queue at the caller's handling unit. */
export const INTERNAL_INBOX_HREF = "/internal/complaints?needsReceive=1";

export function isInternalInboxStatus(status: string): boolean {
  return (INTERNAL_INBOX_STATUSES as readonly string[]).includes(status);
}

/**
 * Whether a ticket is incoming for the signed-in unit (same rule as API-551).
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
