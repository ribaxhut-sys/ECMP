export interface NavItem {
  id: string;
  label: string;
  href: string;
  icon: "dashboard" | "complaints" | "reports" | "users" | "settings";
}

/** Primary app navigation — UI routes for future modules. */
export const APP_NAV_ITEMS: readonly NavItem[] = [
  { id: "dashboard", label: "Dashboard", href: "/dashboard", icon: "dashboard" },
  { id: "complaints", label: "Complaints", href: "/complaints", icon: "complaints" },
  { id: "reports", label: "Reports", href: "/reports", icon: "reports" },
  { id: "users", label: "Users", href: "/users", icon: "users" },
  { id: "settings", label: "Settings", href: "/settings", icon: "settings" },
] as const;
