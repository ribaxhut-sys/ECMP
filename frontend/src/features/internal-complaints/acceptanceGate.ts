/**
 * Internal-complaint dual-acceptance UI gate (ECMP-MODEA-INT-001).
 * Mirrors backend `assert_case_acceptance_authorized` (Mode A):
 * Agent may accept only on own unit; Supervisor/Manager on matching unit;
 * Admin any party; creator SoD unless acting on own unit (Agent, or
 * Supervisor/Manager — 2026-08-19). Admin creators stay blocked.
 *
 * Local (owner = handling): remaining close gate is Supervisor of the owner
 * unit. Handling is already stamped on resolve ACCEPT.
 */

import type { InternalAcceptanceParty } from "./types";

const ADMIN_ROLES = new Set(["ADMIN", "ADMINISTRATOR", "SUPER_ADMIN"]);
const UNIT_APPROVER_ROLES = new Set([
  "SUPERVISOR",
  "BRANCH_SUPERVISOR",
  "MANAGER",
]);
const AGENT_ROLES = new Set(["AGENT", "CS_AGENT", "HANDLER", "BRANCH_OFFICER"]);
const APPROVER_ROLES = new Set([...UNIT_APPROVER_ROLES, ...ADMIN_ROLES]);

function roleSet(roles: readonly string[]): Set<string> {
  return new Set(
    roles.map((role) => role.trim().toUpperCase()).filter(Boolean),
  );
}

function hasAny(roles: Set<string>, allowed: Set<string>): boolean {
  for (const role of roles) {
    if (allowed.has(role)) return true;
  }
  return false;
}

export function normalizeAcceptanceUnit(
  value: string | null | undefined,
): string | null {
  const cleaned = (value || "").trim().toUpperCase();
  return cleaned || null;
}

function idsEqual(left: string | null | undefined, right: string | null | undefined): boolean {
  const a = (left || "").trim().toLowerCase();
  const b = (right || "").trim().toLowerCase();
  return Boolean(a) && Boolean(b) && a === b;
}

export function isSameHandlingAsOwner(
  ownerUnitId: string,
  handlingUnitId: string,
): boolean {
  const owner = normalizeAcceptanceUnit(ownerUnitId);
  const handling = normalizeAcceptanceUnit(handlingUnitId);
  return Boolean(owner) && owner === handling;
}

export type InternalClosureGate = "local" | "transferred";

export function mayRecordInternalAcceptance(input: {
  roles: readonly string[];
  actorUnitCode: string | null;
  party: InternalAcceptanceParty;
  ownerUnitId: string;
  handlingUnitId: string;
  actorUserId: string;
  creatorUserId: string | null;
}): boolean {
  const roles = roleSet(input.roles);
  const isApprover = hasAny(roles, APPROVER_ROLES);
  const isAgent = !isApprover && hasAny(roles, AGENT_ROLES);
  if (!isAgent && !isApprover) return false;

  const isUnitApprover = hasAny(roles, UNIT_APPROVER_ROLES);
  const isCreator = idsEqual(input.actorUserId, input.creatorUserId);

  const actorUnit = normalizeAcceptanceUnit(input.actorUnitCode);
  const required =
    input.party === "OWNER"
      ? normalizeAcceptanceUnit(input.ownerUnitId)
      : normalizeAcceptanceUnit(input.handlingUnitId);
  const ownUnit = Boolean(required) && actorUnit === required;

  if (isCreator && !(isAgent || (isUnitApprover && ownUnit))) {
    return false;
  }
  if (hasAny(roles, ADMIN_ROLES)) return true;
  return ownUnit;
}

/**
 * True when the only reason no accept/reject action is offered is the
 * creator-SoD rule (mirrors backend `case.acceptance_creator_conflict`) —
 * i.e. role/status would otherwise allow it, but the actor authored the
 * complaint themselves. Used to surface an explanatory hint instead of
 * silently showing no actions at all.
 */
export function isBlockedBySelfApproval(input: {
  status: string;
  hasUpdatePermission: boolean;
  actorUnitReady: boolean;
  roles: readonly string[];
  actorUserId: string;
  creatorUserId: string | null;
}): boolean {
  if (
    !input.hasUpdatePermission ||
    !input.actorUnitReady ||
    input.status !== "RESOLVED"
  ) {
    return false;
  }
  const roles = roleSet(input.roles);
  const isApprover = hasAny(roles, APPROVER_ROLES);
  if (!isApprover) return false;
  return idsEqual(input.actorUserId, input.creatorUserId);
}

export function allowedInternalAcceptanceParties(input: {
  roles: readonly string[];
  actorUnitCode: string | null;
  ownerUnitId: string;
  handlingUnitId: string;
  actorUserId: string;
  creatorUserId: string | null;
}): InternalAcceptanceParty[] {
  return (["HANDLING_UNIT", "OWNER"] as const).filter((party) =>
    mayRecordInternalAcceptance({ ...input, party }),
  );
}

export function visibleInternalAcceptanceActions(input: {
  status: string;
  hasUpdatePermission: boolean;
  actorUnitReady: boolean;
  roles: readonly string[];
  actorUnitCode: string | null;
  ownerUnitId: string;
  handlingUnitId: string;
  actorUserId: string;
  creatorUserId: string | null;
  handlingUnitAcceptance: string | null;
  ownerAcceptance: string | null;
}): {
  acceptHandling: boolean;
  acceptOwner: boolean;
  rejectParties: InternalAcceptanceParty[];
  gate: InternalClosureGate;
} {
  const local = isSameHandlingAsOwner(input.ownerUnitId, input.handlingUnitId);
  const gate: InternalClosureGate = local ? "local" : "transferred";
  const closed: {
    acceptHandling: boolean;
    acceptOwner: boolean;
    rejectParties: InternalAcceptanceParty[];
    gate: InternalClosureGate;
  } = {
    acceptHandling: false,
    acceptOwner: false,
    rejectParties: [],
    gate,
  };

  if (
    !input.hasUpdatePermission ||
    !input.actorUnitReady ||
    input.status !== "RESOLVED"
  ) {
    return closed;
  }

  const parties = allowedInternalAcceptanceParties(input);
  const roles = roleSet(input.roles);
  const isApprover = hasAny(roles, APPROVER_ROLES);

  if (local) {
    const canOwnerClose = isApprover && parties.includes("OWNER");
    return {
      acceptHandling: false,
      acceptOwner: canOwnerClose && input.ownerAcceptance !== "ACCEPT",
      rejectParties: canOwnerClose ? ["OWNER"] : [],
      gate,
    };
  }

  return {
    acceptHandling:
      parties.includes("HANDLING_UNIT") &&
      input.handlingUnitAcceptance !== "ACCEPT",
    acceptOwner:
      parties.includes("OWNER") && input.ownerAcceptance !== "ACCEPT",
    rejectParties: parties,
    gate,
  };
}
