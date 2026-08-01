import type { ComplaintStatus } from "@/lib/api/types";

/** Mirrors backend `app.core.status_transitions` (TASK-009 / TASK-010). */
export const STATUS_TRANSITIONS: Record<
  ComplaintStatus,
  readonly ComplaintStatus[]
> = {
  NEW: [],
  ASSIGNED: ["IN_PROGRESS"],
  IN_PROGRESS: ["PENDING"],
  PENDING: ["IN_PROGRESS"],
  RESOLVED: ["CLOSED", "IN_PROGRESS"],
  CLOSED: [],
  ESCALATED: [],
};

export interface StatusAction {
  labelKey: string;
  target: ComplaintStatus;
}

/**
 * UI action label keys (translated via the "complaints" namespace) for allowed
 * PATCH /status transitions. Assign stays on Assignment card; Resolve stays on
 * Resolution form (API-225).
 */
export function statusActionsFor(
  status: ComplaintStatus,
): readonly StatusAction[] {
  switch (status) {
    case "ASSIGNED":
      return [{ labelKey: "startProgress", target: "IN_PROGRESS" }];
    case "IN_PROGRESS":
      return [{ labelKey: "markPending", target: "PENDING" }];
    case "PENDING":
      return [{ labelKey: "resume", target: "IN_PROGRESS" }];
    case "RESOLVED":
      return [
        { labelKey: "closeComplaint", target: "CLOSED" },
        { labelKey: "reopen", target: "IN_PROGRESS" },
      ];
    default:
      return [];
  }
}
