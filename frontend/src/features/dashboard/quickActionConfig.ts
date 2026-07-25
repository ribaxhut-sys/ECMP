export interface QuickAction {
  id: string;
  label: string;
  permission: string;
  description: string;
}

/** RBAC-gated quick actions — routes to existing modules only. */
export const QUICK_ACTIONS: readonly QuickAction[] = [
  {
    id: "create-complaint",
    label: "Create Complaint",
    permission: "complaints:create",
    description: "Register a new complaint",
  },
  {
    id: "view-complaints",
    label: "View Complaints",
    permission: "complaints:read",
    description: "Browse and search complaints",
  },
  {
    id: "view-queue",
    label: "Open Queue",
    permission: "complaints:read",
    description: "Work the complaint queue",
  },
  {
    id: "assign-complaint",
    label: "Assignments",
    permission: "complaints:assign",
    description: "Assign or reassign handlers",
  },
  {
    id: "escalate-complaint",
    label: "Resolutions",
    permission: "complaints:read",
    description: "Resolution and escalation actions",
  },
  {
    id: "manage-users",
    label: "Manage Users",
    permission: "users:read",
    description: "View and administer users",
  },
  {
    id: "refresh-reports",
    label: "Refresh Dashboard",
    permission: "dashboard:read",
    description: "Reload dashboard summary",
  },
] as const;
