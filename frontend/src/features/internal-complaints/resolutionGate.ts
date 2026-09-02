/** Two-party resolution proposal (ECMP-MODEA-INT-001 v0.4). */

import {
  actorMatchesInternalHandlingUnit,
  isAdminFamily,
} from "./transferDirection";
import { isPendingWithdrawRequest } from "./withdrawGate";

function unitsEqual(
  left: string | null | undefined,
  right: string | null | undefined,
): boolean {
  const a = (left || "").trim().toUpperCase();
  const b = (right || "").trim().toUpperCase();
  return Boolean(a) && Boolean(b) && a === b;
}

function idsEqual(
  left: string | null | undefined,
  right: string | null | undefined,
): boolean {
  const a = (left || "").trim();
  const b = (right || "").trim();
  return Boolean(a) && Boolean(b) && a === b;
}

export function isPendingResolutionProposal(
  status: string | null | undefined,
): boolean {
  return (status || "").trim().toUpperCase() === "PENDING_APPROVAL";
}

export function mayProposeResolution(input: {
  status: string;
  actorUnitCode: string | null;
  handlingUnitId: string;
  hasUpdatePermission: boolean;
  roles: readonly string[];
  completionRequestStatus?: string | null;
  withdrawRequestStatus?: string | null;
}): boolean {
  if (!input.hasUpdatePermission) return false;
  if (isPendingWithdrawRequest(input.withdrawRequestStatus)) return false;
  if ((input.completionRequestStatus || "").trim().toUpperCase() === "PENDING") {
    return false;
  }
  if (
    input.status !== "IN_PROGRESS" &&
    input.status !== "CREATED" &&
    input.status !== "ASSIGNED"
  ) {
    return false;
  }
  if (isAdminFamily(input.roles)) return true;
  return actorMatchesInternalHandlingUnit(
    input.actorUnitCode,
    input.handlingUnitId,
    input.roles,
  );
}

export function mayDecideResolutionProposal(input: {
  status: string;
  actorUnitCode: string | null;
  ownerUnitId: string;
  hasUpdatePermission: boolean;
  roles: readonly string[];
  actorUserId: string;
  proposedBy: string | null | undefined;
  resolutionStatus: string | null | undefined;
  withdrawRequestStatus?: string | null;
}): boolean {
  if (!input.hasUpdatePermission) return false;
  if (isPendingWithdrawRequest(input.withdrawRequestStatus)) return false;
  if (input.status !== "IN_PROGRESS") return false;
  if (!isPendingResolutionProposal(input.resolutionStatus)) return false;
  if (idsEqual(input.actorUserId, input.proposedBy)) return false;
  if (isAdminFamily(input.roles)) return true;
  return unitsEqual(input.actorUnitCode, input.ownerUnitId);
}

export function isWaitingOnResolutionProposal(input: {
  status: string;
  actorUnitCode: string | null;
  handlingUnitId: string;
  hasUpdatePermission: boolean;
  roles: readonly string[];
  actorUserId: string;
  proposedBy: string | null | undefined;
  resolutionStatus: string | null | undefined;
  withdrawRequestStatus?: string | null;
}): boolean {
  if (!input.hasUpdatePermission) return false;
  if (isPendingWithdrawRequest(input.withdrawRequestStatus)) return false;
  if (input.status !== "IN_PROGRESS") return false;
  if (!isPendingResolutionProposal(input.resolutionStatus)) return false;
  if (idsEqual(input.actorUserId, input.proposedBy)) return true;
  if (isAdminFamily(input.roles)) return false;
  return actorMatchesInternalHandlingUnit(
    input.actorUnitCode,
    input.handlingUnitId,
    input.roles,
  );
}

export function visibleInternalResolutionActions(input: {
  status: string;
  actorUnitCode: string | null;
  ownerUnitId: string;
  handlingUnitId: string;
  hasUpdatePermission: boolean;
  roles: readonly string[];
  actorUserId: string;
  proposedBy: string | null | undefined;
  resolutionStatus: string | null | undefined;
  completionRequestStatus?: string | null;
  withdrawRequestStatus?: string | null;
}): {
  showToolbar: boolean;
  mayPropose: boolean;
  mayDecide: boolean;
  waiting: boolean;
} {
  const mayPropose = mayProposeResolution(input);
  const mayDecide = mayDecideResolutionProposal(input);
  const waiting = isWaitingOnResolutionProposal(input);
  return {
    showToolbar: mayPropose || mayDecide || waiting,
    mayPropose,
    mayDecide,
    waiting,
  };
}
