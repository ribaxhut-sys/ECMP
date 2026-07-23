export interface QuickAction {
  id: string;
  label: string;
  permission: string;
  description: string;
}

/** RBAC-gated quick actions — UI only; no new backend endpoints. */
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
    description: "Browse the complaint queue",
  },
  {
    id: "assign-complaint",
    label: "Assign Complaint",
    permission: "complaints:assign",
    description: "Assign or reassign a handler",
  },
  {
    id: "escalate-complaint",
    label: "Escalate Complaint",
    permission: "complaints:escalate",
    description: "Escalate to a higher authority",
  },
  {
    id: "manage-users",
    label: "Manage Users",
    permission: "users:read",
    description: "View and administer users",
  },
  {
    id: "create-user",
    label: "Create User",
    permission: "users:create",
    description: "Provision a new user account",
  },
  {
    id: "refresh-reports",
    label: "Refresh Reports",
    permission: "reports:read",
    description: "Reload dashboard aggregations",
  },
] as const;
