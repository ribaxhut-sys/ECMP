/**
 * Knowledge manage UI gate — mirrors backend
 * ``principal_may_manage_knowledge`` / ``require_knowledge_manage``.
 *
 * ``knowledge:manage`` is granted to SUPERVISOR/MANAGER role codes that are
 * shared with Cabang staff; only a Pusat-coded unit (or unscoped Admin) may
 * actually manage. FE must apply the same rule or Cabang managers open the
 * create UI and fail the manage API.
 */

import { isCmBatch1PusatUnitCode } from "@/features/complaints/cmBatch1HqActions";

/** Matches backend gates._KNOWLEDGE_ADMIN_ROLES */
export const KNOWLEDGE_ADMIN_ROLES = ["ADMIN", "ADMINISTRATOR", "SUPER_ADMIN"] as const;

/** Matches backend gates._KNOWLEDGE_UNIT_ROLES */
export const KNOWLEDGE_UNIT_ROLES = ["SUPERVISOR", "BRANCH_SUPERVISOR", "MANAGER"] as const;

const ADMIN_ROLE_SET = new Set<string>(KNOWLEDGE_ADMIN_ROLES);
const UNIT_ROLE_SET = new Set<string>(KNOWLEDGE_UNIT_ROLES);

function normalizeRoles(roles: readonly string[]): string[] {
  return roles.map((role) => (role || "").trim().toUpperCase()).filter(Boolean);
}

/**
 * @param orgUnitCode Branch/unit code from the catalog, or ``null`` when the
 *   principal has no branch (typical Admin Pusat / SUPER_ADMIN).
 */
export function mayManageKnowledge(input: {
  roles: readonly string[];
  hasPermission: (permission: string) => boolean;
  orgUnitCode: string | null;
}): boolean {
  if (!input.hasPermission("knowledge:manage")) return false;

  const roles = normalizeRoles(input.roles);
  const isAdmin = roles.some((role) => ADMIN_ROLE_SET.has(role));
  const isUnitRole = roles.some((role) => UNIT_ROLE_SET.has(role));

  if (isAdmin) {
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
