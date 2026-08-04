export interface NavItem {
  id: string;
  /** Key within the "nav" message namespace, e.g. "dashboard" -> t("dashboard") */
  labelKey: string;
  href: string;
  icon:
    | "dashboard"
    | "complaints"
    | "queue"
    | "assignments"
    | "resolutions"
    | "reports"
    | "users"
    | "settings"
    | "attachments";
  /** Optional notification badge (presentation only). */
  badge?: number | string;
  /**
   * Canonical permission strings (existing catalog, see backend/app/core/rbac.py)
   * gating this item's visibility. Item is visible if the user holds at least
   * one. Omit for items with no permission gate.
   */
  requiredPermissions?: readonly string[];
}

/** Visible iff the item has no gate, or the caller holds at least one of its
 * requiredPermissions. hasPermission is caller-supplied so this stays a pure
 * function — AuthProvider.hasPermission already owns wildcard ("*") handling. */
export function isNavItemVisible(
  item: Pick<NavItem, "requiredPermissions">,
  hasPermission: (permission: string) => boolean,
): boolean {
  if (!item.requiredPermissions || item.requiredPermissions.length === 0) {
    return true;
  }
  return item.requiredPermissions.some((permission) => hasPermission(permission));
}

/**
 * Visual nav groups for Sidebar hierarchy only.
 * Does not change routes, menu membership, or item order within each group.
 */
export interface NavGroup {
  id: string;
  /** Key within the "nav" namespace */
  labelKey: string;
  itemIds: readonly string[];
}

/** Primary app navigation — UI routes for modules. */
export const APP_NAV_ITEMS: readonly NavItem[] = [
  { id: "dashboard", labelKey: "dashboard", href: "/dashboard", icon: "dashboard" },
  {
    id: "complaints",
    labelKey: "complaints",
    href: "/complaints",
    icon: "complaints",
    requiredPermissions: [
      "complaints:read",
      "complaints:create",
      "complaints:update",
      "complaints:assign",
      "complaints:escalate",
      "complaints:close",
    ],
  },
  { id: "queue", labelKey: "queue", href: "/queue", icon: "queue" },
  {
    id: "assignments",
    labelKey: "assignments",
    href: "/assignments",
    icon: "assignments",
  },
  {
    id: "resolutions",
    labelKey: "resolutions",
    href: "/resolutions",
    icon: "resolutions",
  },
  {
    id: "attachments",
    labelKey: "attachments",
    href: "/attachments",
    icon: "attachments",
  },
  { id: "reports", labelKey: "reports", href: "/reports", icon: "reports" },
  { id: "users", labelKey: "users", href: "/users", icon: "users" },
  { id: "settings", labelKey: "settings", href: "/settings", icon: "settings" },
] as const;

/** Presentation-only grouping — same items / hrefs as APP_NAV_ITEMS. */
export const APP_NAV_GROUPS: readonly NavGroup[] = [
  {
    id: "operations",
    labelKey: "groupOperations",
    itemIds: ["dashboard", "complaints", "queue", "assignments", "resolutions"],
  },
  {
    id: "knowledge",
    labelKey: "groupKnowledge",
    itemIds: ["attachments", "reports"],
  },
  {
    id: "administration",
    labelKey: "groupAdministration",
    itemIds: ["users", "settings"],
  },
] as const;
