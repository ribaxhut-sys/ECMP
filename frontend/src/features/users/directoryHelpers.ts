import type { RoleRef, UserRef } from "@/lib/api";
import type { BadgeTone } from "@/shared/ui";
import { formatDateTime24 } from "@/shared/utils/datetime";
import { nameInitials } from "@/shared/utils/initials";

export type DirectoryFilter =
  | "all"
  | "active"
  | "inactive"
  | "administrator"
  | "manager"
  | "supervisor"
  | "officer"
  | "viewer";

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
  "AGENT",
  "SUPERVISOR",
  "MANAGER",
  "ADMIN",
  "VIEWER",
] as const;

const CANONICAL_USER_FORM_ROLE_ORDER = new Map<string, number>(
  CANONICAL_USER_FORM_ROLE_CODES.map((code, index) => [code, index]),
);

/** Keep only canonical roles, sorted CRO → Staff KaSatPel → KaSatPel → Admin → Viewer. */
export function filterRolesForUserForm(roles: RoleRef[]): RoleRef[] {
  return roles
    .filter((row) => CANONICAL_USER_FORM_ROLE_ORDER.has(row.code))
    .sort(
      (a, b) =>
        (CANONICAL_USER_FORM_ROLE_ORDER.get(a.code) ?? 99) -
        (CANONICAL_USER_FORM_ROLE_ORDER.get(b.code) ?? 99),
    );
}

export type CanonicalUserFormRoleCode =
  (typeof CANONICAL_USER_FORM_ROLE_CODES)[number];

export function userFormRoleLabel(
  code: string,
  labels: Record<CanonicalUserFormRoleCode, string>,
  fallback: string,
): string {
  if (code in labels) {
    return labels[code as CanonicalUserFormRoleCode];
  }
  return fallback;
}

export function canonicalUserFormRoleLabels(
  t: (key: string) => string,
): Record<CanonicalUserFormRoleCode, string> {
  return {
    AGENT: t("roleAgent"),
    SUPERVISOR: t("roleSupervisor"),
    MANAGER: t("roleManager"),
    ADMIN: t("roleAdmin"),
    VIEWER: t("roleViewer"),
  };
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

/** Avatar direktori — aturan 3 huruf tunggal, lihat `shared/utils/initials`. */
export function userInitials(user: Pick<UserRef, "fullName" | "username">): string {
  const name = user.fullName?.trim() || user.username;
  return nameInitials(name) ?? "?";
}

export function formatWhen(
  value: string | null | undefined,
  locale: string,
): string | null {
  if (!value) return null;
  const formatted = formatDateTime24(value, locale);
  return formatted || null;
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
  if (/(staff\s*kasatpel|supervisor|supervisory)/.test(hay)) return "supervisor";
  if (/\bmanager\b/.test(hay) || /\bkasatpel\b/.test(hay)) return "manager";
  if (/(agent|officer|handler|\bcro\b)/.test(hay)) return "officer";
  if (/(viewer|peninjau|read[_-]?only|readonly)/.test(hay)) return "viewer";
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
    case "viewer":
      return directoryRoleFamily(user) === "viewer";
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

/** Sentinel: do not restrict the directory by unit. */
export const DIRECTORY_BRANCH_FILTER_ALL = "all";

/**
 * Admin directory unit filter.
 * Selecting the Pusat catalog row also includes members with no `branchId`
 * (Admin Pusat), because the directory already labels those as Pusat.
 */
export function matchesDirectoryBranch(
  user: Pick<UserRef, "branchId">,
  branchFilter: string,
  pusatBranchId?: string | null,
): boolean {
  if (!branchFilter || branchFilter === DIRECTORY_BRANCH_FILTER_ALL) {
    return true;
  }
  if (user.branchId === branchFilter) return true;
  return (
    Boolean(pusatBranchId) &&
    branchFilter === pusatBranchId &&
    user.branchId == null
  );
}
