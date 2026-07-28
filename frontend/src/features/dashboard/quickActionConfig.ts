export interface QuickAction {
  id: string;
  labelKey: string;
  permission: string;
  descriptionKey: string;
}

/** RBAC-gated quick actions — routes to existing modules only. Labels/descriptions are translated via the "dashboard" namespace. */
export const QUICK_ACTIONS: readonly QuickAction[] = [
  {
    id: "create-complaint",
    labelKey: "createComplaint",
    permission: "complaints:create",
    descriptionKey: "createComplaintDesc",
  },
  {
    id: "view-complaints",
    labelKey: "viewComplaints",
    permission: "complaints:read",
    descriptionKey: "viewComplaintsDesc",
  },
  {
    id: "view-queue",
    labelKey: "openQueue",
    permission: "complaints:read",
    descriptionKey: "openQueueDesc",
  },
  {
    id: "assign-complaint",
    labelKey: "assignments",
    permission: "complaints:assign",
    descriptionKey: "assignmentsDesc",
  },
  {
    id: "escalate-complaint",
    labelKey: "resolutions",
    permission: "complaints:read",
    descriptionKey: "resolutionsDesc",
  },
  {
    id: "manage-users",
    labelKey: "manageUsers",
    permission: "users:read",
    descriptionKey: "manageUsersDesc",
  },
  {
    id: "refresh-reports",
    labelKey: "refreshDashboard",
    permission: "dashboard:read",
    descriptionKey: "refreshDashboardDesc",
  },
] as const;
