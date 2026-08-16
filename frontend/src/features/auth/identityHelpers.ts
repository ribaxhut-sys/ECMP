import type { AuthMe } from "@/lib/api/types";
import { nameInitials } from "@/shared/utils/initials";

/** Avatar identitas — aturan 3 huruf tunggal, lihat `shared/utils/initials`. */
export function identityInitials(
  name: string | undefined | null,
  fallback = "?",
): string {
  return nameInitials(name) ?? fallback;
}

export function formatIdentityWhen(
  value: string | null | undefined,
): string | null {
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

export function formatIdentityBranch(
  branchId: string | null | undefined,
  unassignedLabel: string,
): string {
  if (!branchId) return unassignedLabel;
  if (branchId.length <= 12) return branchId;
  return `${branchId.slice(0, 8)}…${branchId.slice(-4)}`;
}

export function moduleRoleDisplayLabels(tUsers: (key: string) => string): Record<string, string> {
  return {
    AGENT: tUsers("roleAgent"),
    CS_AGENT: tUsers("roleAgent"),
    SUPERVISOR: tUsers("roleSupervisor"),
    BRANCH_SUPERVISOR: tUsers("roleBranchManager"),
    MANAGER: tUsers("roleManager"),
    ADMIN: tUsers("roleAdmin"),
    ADMINISTRATOR: tUsers("roleAdmin"),
    SUPER_ADMIN: tUsers("roleAdmin"),
  };
}

export function primaryRoleLabel(
  user: Pick<AuthMe, "roles"> | null | undefined,
  fallback: string,
  labels?: Record<string, string>,
): string {
  const role = user?.roles?.[0]?.trim();
  if (!role) return fallback;
  const mapped = labels?.[role.toUpperCase()];
  return mapped || role;
}
