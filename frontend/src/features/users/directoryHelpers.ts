import type { RoleRef, UserRef } from "@/lib/api";
import type { BadgeTone } from "@/shared/ui";

export type DirectoryFilter =
  | "all"
  | "active"
  | "inactive"
  | "administrator"
  | "manager"
  | "supervisor"
  | "officer";

export type DirectoryRoleFamily =
  | "administrator"
  | "manager"
  | "supervisor"
  | "officer"
  | "viewer"
  | "other";

/**
 * Canonical personas for Mode A user create/edit pickers.
 * System role aliases (ADMINISTRATOR, BRANCH_OFFICER, HO_ENGINEER, …) remain
 * in the catalog for compatibility but are hidden from operator UX.
 */
export const CANONICAL_USER_FORM_ROLE_CODES = [
  "ADMIN",
  "MANAGER",
  "SUPERVISOR",
  "BRANCH_SUPERVISOR",
  "AGENT",
  "VIEWER",
] as const;

const CANONICAL_USER_FORM_ROLE_ORDER = new Map<string, number>(
  CANONICAL_USER_FORM_ROLE_CODES.map((code, index) => [code, index]),
);

/** Keep only canonical roles, sorted Admin → Supervisor → Agent → Viewer. */
export function filterRolesForUserForm(roles: RoleRef[]): RoleRef[] {
  return roles
    .filter((row) => CANONICAL_USER_FORM_ROLE_ORDER.has(row.code))
    .sort(
      (a, b) =>
        (CANONICAL_USER_FORM_ROLE_ORDER.get(a.code) ?? 99) -
        (CANONICAL_USER_FORM_ROLE_ORDER.get(b.code) ?? 99),
    );
}

/** Mirrors backend BRANCH_SCOPED_ROLE_CODES. */
export const BRANCH_SCOPED_ROLE_CODES = new Set([
  "AGENT",
  "CS_AGENT",
  "BRANCH_OFFICER",
  "SUPERVISOR",
  "BRANCH_SUPERVISOR",
  "MANAGER",
]);

/** Mirrors backend HEAD_OFFICE_SCOPED_ROLE_CODES (Commit 2). */
export const HEAD_OFFICE_SCOPED_ROLE_CODES = new Set([
  "ADMIN",
  "ADMINISTRATOR",
  "HO_SCHEDULER",
  "HEAD_OFFICE_SCHEDULER",
  "SCHEDULER",
  "HO_ENGINEER",
  "HEAD_OFFICE_ENGINEER",
]);

/**
 * Role picker by home unit:
 * - Cabang: all personas except Admin / other head-office-only codes.
 * - Pusat: same set as cabang **plus** Admin (Pusat also handles complaints).
 */
export function filterRolesForHomeUnit(
  roles: RoleRef[],
  atHeadOffice: boolean,
): RoleRef[] {
  if (atHeadOffice) return roles;
  return roles.filter((row) => !HEAD_OFFICE_SCOPED_ROLE_CODES.has(row.code));
}

export function userInitials(user: Pick<UserRef, "fullName" | "username">): string {
  const name = user.fullName?.trim() || user.username;
  const parts = name.split(/\s+/).filter(Boolean);
  if (parts.length >= 2) {
    return `${parts[0]![0] ?? ""}${parts[1]![0] ?? ""}`.toUpperCase();
  }
  return name.slice(0, 2).toUpperCase();
}

export function formatWhen(value: string | null | undefined): string | null {
  if (!value) return null;
  try {
    return new Intl.DateTimeFormat(undefined, {
      day: "2-digit",
      month: "short",
      year: "numeric",
      hour: "2-digit",
      minute: "2-digit",
      hour12: false,
    }).format(new Date(value));
  } catch {
    return value;
  }
}

/** BRANCH_SUPERVISOR presentation override (Commit 5) — role.code and
 * role.name from the API are unchanged; only the displayed label differs. */
export function roleDisplayName(
  role: Pick<RoleRef, "code" | "name">,
  branchSupervisorLabel: string,
): string {
  return role.code === "BRANCH_SUPERVISOR" ? branchSupervisorLabel : role.name;
}

function roleHaystack(user: Pick<UserRef, "roleCode" | "roleName">): string {
  return `${user.roleCode ?? ""} ${user.roleName ?? ""}`.toLowerCase();
}

export function directoryRoleFamily(
  user: Pick<UserRef, "roleCode" | "roleName">,
): DirectoryRoleFamily {
  const hay = roleHaystack(user);
  if (!hay.trim()) return "other";
  if (/(admin|administrator|sysadmin)/.test(hay)) return "administrator";
  if (/\bmanager\b/.test(hay)) return "manager";
  if (/(supervisor|supervisory)/.test(hay)) return "supervisor";
  if (/(agent|officer|handler)/.test(hay)) return "officer";
  if (/(viewer|read[_-]?only|readonly)/.test(hay)) return "viewer";
  return "other";
}

export function directoryRoleTone(family: DirectoryRoleFamily): BadgeTone {
  switch (family) {
    case "administrator":
      return "danger";
    case "manager":
      return "primary";
    case "supervisor":
      return "warning";
    case "officer":
      return "info";
    case "viewer":
      return "neutral";
    default:
      return "primary";
  }
}

export function directoryRoleLabel(
  user: Pick<UserRef, "roleCode" | "roleName">,
  labels: Record<DirectoryRoleFamily, string>,
  fallback: string,
): string {
  const family = directoryRoleFamily(user);
  if (family !== "other") return labels[family];
  return user.roleName?.trim() || user.roleCode?.trim() || fallback;
}

export function matchesDirectoryFilter(
  user: UserRef,
  filter: DirectoryFilter,
): boolean {
  switch (filter) {
    case "all":
      return true;
    case "active":
      return user.isActive;
    case "inactive":
      return !user.isActive;
    case "administrator":
      return directoryRoleFamily(user) === "administrator";
    case "manager":
      return directoryRoleFamily(user) === "manager";
    case "supervisor":
      return directoryRoleFamily(user) === "supervisor";
    case "officer":
      return directoryRoleFamily(user) === "officer";
    default:
      return true;
  }
}

export function matchesDirectorySearch(user: UserRef, query: string): boolean {
  const q = query.trim().toLowerCase();
  if (!q) return true;
  return (
    user.username.toLowerCase().includes(q) ||
    user.fullName.toLowerCase().includes(q)
  );
}
