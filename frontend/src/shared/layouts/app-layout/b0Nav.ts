import type { NavGroup, NavItem } from "./nav";
import { SHELL_PERMISSIONS } from "@/auth/mockAuth";

/**
 * Batch B0 navigation — WF-001-R1 / NAV-001 closed set (shell only).
 * No complaint feature destinations. Manager Dashboard deferred (not listed).
 */
export const B0_NAV_ITEMS: readonly NavItem[] = [
  {
    id: "workspace",
    labelKey: "workspace",
    href: "/workspace",
    icon: "complaints",
    requiredPermissions: [SHELL_PERMISSIONS.workspaceIntake],
  },
  {
    id: "queue",
    labelKey: "queue",
    href: "/queue",
    icon: "queue",
    requiredPermissions: [
      SHELL_PERMISSIONS.queueAssigned,
      SHELL_PERMISSIONS.queueSupervisor,
    ],
  },
  {
    id: "settings",
    labelKey: "settings",
    href: "/settings",
    icon: "settings",
    requiredPermissions: [SHELL_PERMISSIONS.settings],
  },
] as const;

export const B0_NAV_GROUPS: readonly NavGroup[] = [
  {
    id: "workspace",
    labelKey: "groupWorkspace",
    itemIds: ["workspace", "queue"],
  },
  {
    id: "administration",
    labelKey: "groupAdministration",
    itemIds: ["settings"],
  },
] as const;
