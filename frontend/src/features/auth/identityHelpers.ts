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
  locale: string,
): string | null {
  if (!value) return null;
  try {
    return new Intl.DateTimeFormat(locale, {
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

/** Resolve unit UUID/code to a readable name — never show a truncated id. */
export function resolveIdentityUnitLabel(
  branchId: string | null | undefined,
  units: readonly { id: string; code: string; name: string }[],
  unassignedLabel: string,
): string {
  const id = branchId?.trim();
  if (!id) return unassignedLabel;
  const match = units.find((unit) => unit.id === id || unit.code === id);
  if (!match) return unassignedLabel;
  if (match.name.trim() && match.code.trim() && match.name !== match.code) {
    return `${match.name} (${match.code})`;
  }
  return match.name.trim() || match.code.trim() || unassignedLabel;
}

export function isOwnModuleActivity(
  actor: string | null | undefined,
  user: Pick<AuthMe, "id" | "username" | "email" | "fullName"> | null | undefined,
): boolean {
  const needle = actor?.trim().toLowerCase();
  if (!needle || needle === "system" || !user) return false;
  const keys = [user.username, user.fullName, user.email, user.id]
    .map((value) => value?.trim().toLowerCase())
    .filter((value): value is string => Boolean(value));
  return keys.includes(needle);
}

export function moduleRoleDisplayLabels(tUsers: (key: string) => string): Record<string, string> {
  return {
    AGENT: tUsers("roleAgent"),
    CS_AGENT: tUsers("roleAgent"),
    HANDLER: tUsers("roleAgent"),
    BRANCH_OFFICER: tUsers("roleAgent"),
    SUPERVISOR: tUsers("roleSupervisor"),
    BRANCH_SUPERVISOR: tUsers("roleSupervisor"),
    MANAGER: tUsers("roleManager"),
    ADMIN: tUsers("roleAdmin"),
    ADMINISTRATOR: tUsers("roleAdmin"),
    SUPER_ADMIN: tUsers("roleAdmin"),
    VIEWER: tUsers("roleViewer"),
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
