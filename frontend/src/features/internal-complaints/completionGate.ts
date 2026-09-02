/** Pusat → cabang return for incomplete documents (ECMP-MODEA-INT-001 v0.2). */

import {
  actorMatchesInternalHandlingUnit,
  isPusatUnitCode,
} from "./transferDirection";

function unitsEqual(
  left: string | null | undefined,
  right: string | null | undefined,
): boolean {
  const a = (left || "").trim().toUpperCase();
  const b = (right || "").trim().toUpperCase();
  return Boolean(a) && Boolean(b) && a === b;
}

export function isAwaitingCompletion(
  completionRequestStatus: string | null | undefined,
): boolean {
  return (completionRequestStatus || "").trim().toUpperCase() === "PENDING";
}

export function mayReturnForCompletion(input: {
  status: string;
  actorUnitCode: string | null;
  ownerUnitId: string;
  handlingUnitId: string;
  hasUpdatePermission: boolean;
  completionRequestStatus: string | null | undefined;
  roles?: readonly string[];
}): boolean {
  if (!input.hasUpdatePermission) return false;
  if (isAwaitingCompletion(input.completionRequestStatus)) return false;
  if (input.status !== "ASSIGNED" && input.status !== "IN_PROGRESS") return false;
  if (isPusatUnitCode(input.ownerUnitId) || !isPusatUnitCode(input.handlingUnitId)) {
    return false;
  }
  return actorMatchesInternalHandlingUnit(
    input.actorUnitCode,
    input.handlingUnitId,
    input.roles ?? [],
  );
}

export function mayResendToPusat(input: {
  status: string;
  actorUnitCode: string | null;
  ownerUnitId: string;
  handlingUnitId: string;
  hasUpdatePermission: boolean;
  completionRequestStatus: string | null | undefined;
}): boolean {
  if (!input.hasUpdatePermission) return false;
  if (!isAwaitingCompletion(input.completionRequestStatus)) return false;
  if (input.status !== "ASSIGNED") return false;
  if (!unitsEqual(input.handlingUnitId, input.ownerUnitId)) return false;
  if (isPusatUnitCode(input.ownerUnitId)) return false;
  return unitsEqual(input.actorUnitCode, input.ownerUnitId);
}
