export interface NavItem {
  id: string;
  label: string;
  href: string;
  icon:
    | "dashboard"
    | "complaints"
    | "queue"
    | "assignments"
    | "reports"
    | "users"
    | "settings"
    | "attachments";
}

/** Primary app navigation — UI routes for future modules. */
export const APP_NAV_ITEMS: readonly NavItem[] = [
  { id: "dashboard", label: "Dashboard", href: "/dashboard", icon: "dashboard" },
  { id: "complaints", label: "Complaints", href: "/complaints", icon: "complaints" },
  { id: "queue", label: "Queue", href: "/queue", icon: "queue" },
  {
    id: "assignments",
    label: "Assignments",
    href: "/assignments",
    icon: "assignments",
  },
  {
    id: "attachments",
    label: "Attachments",
    href: "/attachments",
    icon: "attachments",
  },
  { id: "reports", label: "Reports", href: "/reports", icon: "reports" },
  { id: "users", label: "Users", href: "/users", icon: "users" },
  { id: "settings", label: "Settings", href: "/settings", icon: "settings" },
] as const;
