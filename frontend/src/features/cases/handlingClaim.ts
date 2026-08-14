const REASSIGN_ROLES = new Set([
  "SUPERVISOR",
  "BRANCH_SUPERVISOR",
  "MANAGER",
]);

export function isHandlingReassignRole(
  roles: readonly string[] | null | undefined,
): boolean {
  return (roles ?? []).some((role) => REASSIGN_ROLES.has(role.toUpperCase()));
}

export function sameUserId(
  left: string | null | undefined,
  right: string | null | undefined,
): boolean {
  const a = (left || "").trim().toLowerCase();
  const b = (right || "").trim().toLowerCase();
  return Boolean(a) && a === b;
}

export function canClaimHandling(opts: {
  handlingClaimedBy?: string | null;
  userId?: string | null;
}): boolean {
  const claimed = opts.handlingClaimedBy?.trim();
  if (!claimed) return true;
  return sameUserId(claimed, opts.userId);
}
