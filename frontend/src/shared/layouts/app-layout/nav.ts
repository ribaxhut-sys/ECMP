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

/** Primary app navigation — UI routes for future modules. */
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
