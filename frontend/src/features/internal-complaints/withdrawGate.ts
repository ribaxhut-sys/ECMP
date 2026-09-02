/** Branch → Pusat withdraw UI gate (ECMP-MODEA-INT-001).

``mayReceiveInternal`` remains the AuthZ of lab ``POST /receive``.
Mode A UI does not show a claim button — propose auto-claims; return does not.
*/

import {
  actorMatchesInternalHandlingUnit,
  isPusatUnitCode,
} from "./transferDirection";

const ADMIN_ROLES = new Set(["ADMIN", "ADMINISTRATOR", "SUPER_ADMIN"]);

function roleSet(roles: readonly string[]): Set<string> {
  return new Set(roles.map((role) => role.trim().toUpperCase()).filter(Boolean));
}

function hasAny(roles: Set<string>, allowed: Set<string>): boolean {
  for (const role of roles) {
    if (allowed.has(role)) return true;
  }
  return false;
}

function idsEqual(
  left: string | null | undefined,
  right: string | null | undefined,
): boolean {
  const a = (left || "").trim().toLowerCase();
  const b = (right || "").trim().toLowerCase();
  return Boolean(a) && Boolean(b) && a === b;
}

function unitsEqual(
  left: string | null | undefined,
  right: string | null | undefined,
): boolean {
  const a = (left || "").trim().toUpperCase();
  const b = (right || "").trim().toUpperCase();
  return Boolean(a) && Boolean(b) && a === b;
}

export function isWaitingForPusatReceive(input: {
  status: string;
  ownerUnitId: string;
  handlingUnitId: string;
}): boolean {
  if (input.status !== "ASSIGNED" && input.status !== "CREATED") return false;
  return (
    !isPusatUnitCode(input.ownerUnitId) && isPusatUnitCode(input.handlingUnitId)
  );
}

export function mayOwnerWithdraw(input: {
  roles: readonly string[];
  actorUserId: string;
  creatorUserId: string;
  actorUnitCode: string | null;
  ownerUnitId: string;
  hasAssignPermission: boolean;
}): boolean {
  if (idsEqual(input.actorUserId, input.creatorUserId)) return true;
  const roles = roleSet(input.roles);
  if (hasAny(roles, ADMIN_ROLES)) return true;
  return (
    input.hasAssignPermission &&
    unitsEqual(input.actorUnitCode, input.ownerUnitId)
  );
}

export function mayReceiveInternal(input: {
  status: string;
  actorUnitCode: string | null;
  handlingUnitId: string;
  hasUpdatePermission: boolean;
  completionRequestStatus?: string | null;
  roles?: readonly string[];
}): boolean {
  if (!input.hasUpdatePermission) return false;
  if ((input.completionRequestStatus || "").trim().toUpperCase() === "PENDING") {
    return false;
  }
  if (input.status !== "CREATED" && input.status !== "ASSIGNED") return false;
  return actorMatchesInternalHandlingUnit(
    input.actorUnitCode,
    input.handlingUnitId,
    input.roles ?? [],
  );
}

export function mayRequestWithdraw(input: {
  status: string;
  ownerUnitId: string;
  handlingUnitId: string;
  withdrawRequestStatus: string | null | undefined;
  roles: readonly string[];
  actorUserId: string;
  creatorUserId: string;
  actorUnitCode: string | null;
  hasAssignPermission: boolean;
}): boolean {
  if (input.status !== "IN_PROGRESS") return false;
  if (isPendingWithdrawRequest(input.withdrawRequestStatus)) return false;
  if (isPusatUnitCode(input.ownerUnitId) || !isPusatUnitCode(input.handlingUnitId)) {
    return false;
  }
  return mayOwnerWithdraw(input);
}

export function isPendingWithdrawRequest(
  status: string | null | undefined,
): boolean {
  return (status || "").trim().toUpperCase() === "PENDING";
}

export function mayDecideWithdraw(input: {
  withdrawRequestStatus: string | null | undefined;
  roles: readonly string[];
  actorUnitCode: string | null;
  handlingUnitId: string;
  hasUpdatePermission: boolean;
}): boolean {
  if (!input.hasUpdatePermission) return false;
  if (!isPendingWithdrawRequest(input.withdrawRequestStatus)) return false;
  const roles = roleSet(input.roles);
  if (hasAny(roles, ADMIN_ROLES)) return true;
  return actorMatchesInternalHandlingUnit(
    input.actorUnitCode,
    input.handlingUnitId,
    input.roles,
  );
}
