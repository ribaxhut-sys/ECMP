import type { RoleRef, UserRef } from "@/lib/api";
import type { BadgeTone } from "@/shared/ui";

export type DirectoryFilter =
  | "all"
  | "active"
  | "inactive"
  | "administrator"
  | "supervisor"
  | "agent";

export type DirectoryRoleFamily =
  | "administrator"
  | "supervisor"
  | "agent"
  | "viewer"
  | "other";

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
      dateStyle: "medium",
      timeStyle: "short",
    }).format(new Date(value));
  } catch {
    return value;
  }
}

export function formatBranch(
  branchId: string | null,
  unassignedLabel: string,
): string {
  if (!branchId) return unassignedLabel;
  if (branchId.length <= 12) return branchId;
  return `${branchId.slice(0, 8)}…${branchId.slice(-4)}`;
}

/** Organization-location badge — mirrors the backend rule (Commit 2): a
 * branch-scoped role always carries a branchId, a head-office scoped role
 * never does, so branchId presence alone is the reliable signal. */
export type DirectoryLocationKind = "headOffice" | "branch";

export function userLocationKind(
  user: Pick<UserRef, "branchId">,
): DirectoryLocationKind {
  return user.branchId ? "branch" : "headOffice";
}

export function directoryLocationTone(kind: DirectoryLocationKind): BadgeTone {
  return kind === "branch" ? "info" : "primary";
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
  if (/(supervisor|supervisory)/.test(hay)) return "supervisor";
  if (/(agent|officer|handler)/.test(hay)) return "agent";
  if (/(viewer|read[_-]?only|readonly)/.test(hay)) return "viewer";
  return "other";
}

export function directoryRoleTone(family: DirectoryRoleFamily): BadgeTone {
  switch (family) {
    case "administrator":
      return "danger";
    case "supervisor":
      return "warning";
    case "agent":
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
    case "supervisor":
      return directoryRoleFamily(user) === "supervisor";
    case "agent":
      return directoryRoleFamily(user) === "agent";
    default:
      return true;
  }
}

export function matchesDirectorySearch(user: UserRef, query: string): boolean {
  const q = query.trim().toLowerCase();
  if (!q) return true;
  return (
    user.username.toLowerCase().includes(q) ||
    user.fullName.toLowerCase().includes(q) ||
    user.email.toLowerCase().includes(q) ||
    (user.roleName ?? "").toLowerCase().includes(q) ||
    (user.roleCode ?? "").toLowerCase().includes(q)
  );
}
