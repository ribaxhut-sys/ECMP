/**
 * Announcement manage UI gate — mirrors backend
 * ``principal_may_manage_announcements`` / ``require_announcement_manage``.
 *
 * ``announcement:manage`` is granted to SUPERVISOR/MANAGER role codes that are
 * shared with Cabang staff; only a Pusat-coded unit (or unscoped Admin) may
 * actually manage. FE must apply the same rule or Cabang managers open the
 * create UI, fail the manage API, and never see the read-only history list.
 */

import { isCmBatch1PusatUnitCode } from "@/features/complaints/cmBatch1HqActions";

/** Matches backend gates._ANNOUNCEMENT_ADMIN_ROLES */
export const ANNOUNCEMENT_ADMIN_ROLES = [
  "ADMIN",
  "ADMINISTRATOR",
  "SUPER_ADMIN",
] as const;

/** Matches backend gates._ANNOUNCEMENT_UNIT_ROLES */
export const ANNOUNCEMENT_UNIT_ROLES = [
  "SUPERVISOR",
  "BRANCH_SUPERVISOR",
  "MANAGER",
] as const;

const ADMIN_ROLE_SET = new Set<string>(ANNOUNCEMENT_ADMIN_ROLES);
const UNIT_ROLE_SET = new Set<string>(ANNOUNCEMENT_UNIT_ROLES);

function normalizeRoles(roles: readonly string[]): string[] {
  return roles.map((role) => (role || "").trim().toUpperCase()).filter(Boolean);
}

/**
 * @param orgUnitCode Branch/unit code from the catalog, or ``null`` when the
 *   principal has no branch (typical Admin Pusat / SUPER_ADMIN).
 */
export function mayManageAnnouncements(input: {
  roles: readonly string[];
  hasPermission: (permission: string) => boolean;
  orgUnitCode: string | null;
}): boolean {
  if (!input.hasPermission("announcement:manage")) return false;

  const roles = normalizeRoles(input.roles);
  const isAdmin = roles.some((role) => ADMIN_ROLE_SET.has(role));
  const isUnitRole = roles.some((role) => UNIT_ROLE_SET.has(role));

  if (isAdmin) {
    // No branch at all reads as head office — same as backend _is_pusat_or_unscoped.
    if (input.orgUnitCode == null || input.orgUnitCode.trim() === "") {
      return true;
    }
    return isCmBatch1PusatUnitCode(input.orgUnitCode);
  }

  if (isUnitRole) {
    return isCmBatch1PusatUnitCode(input.orgUnitCode);
  }

  return false;
}
