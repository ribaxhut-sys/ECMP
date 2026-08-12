import type { AuthMe } from "@/lib/api/types";

export function identityInitials(
  name: string | undefined | null,
  fallback = "?",
): string {
  if (!name?.trim()) return fallback;
  const parts = name.trim().split(/\s+/).filter(Boolean);
  if (parts.length >= 2) {
    return `${parts[0]![0] ?? ""}${parts[parts.length - 1]![0] ?? ""}`.toUpperCase();
  }
  return parts[0]!.slice(0, 2).toUpperCase();
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

export function primaryRoleLabel(
  user: Pick<AuthMe, "roles"> | null | undefined,
  fallback: string,
): string {
  const role = user?.roles?.[0]?.trim();
  return role || fallback;
}
