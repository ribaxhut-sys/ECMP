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
  { id: "complaints", labelKey: "complaints", href: "/complaints", icon: "complaints" },
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
    id: "workspace",
    labelKey: "groupWorkspace",
    itemIds: ["attachments", "reports"],
  },
  {
    id: "administration",
    labelKey: "groupAdministration",
    itemIds: ["users", "settings"],
  },
] as const;
