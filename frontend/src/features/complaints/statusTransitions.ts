import type { ComplaintStatus } from "@/lib/api/types";

/** Mirrors backend `app.core.status_transitions` (TASK-009). */
export const STATUS_TRANSITIONS: Record<
  ComplaintStatus,
  readonly ComplaintStatus[]
> = {
  NEW: [],
  ASSIGNED: ["IN_PROGRESS"],
  IN_PROGRESS: ["PENDING", "RESOLVED"],
  PENDING: ["IN_PROGRESS", "RESOLVED"],
  RESOLVED: ["CLOSED", "IN_PROGRESS"],
  CLOSED: [],
  ESCALATED: [],
};

export interface StatusAction {
  label: string;
  target: ComplaintStatus;
}

/** UI action labels for allowed transitions (Assign stays on Assignment card). */
export function statusActionsFor(
  status: ComplaintStatus,
): readonly StatusAction[] {
  switch (status) {
    case "ASSIGNED":
      return [{ label: "Start Progress", target: "IN_PROGRESS" }];
    case "IN_PROGRESS":
      return [
        { label: "Mark Pending", target: "PENDING" },
        { label: "Resolve", target: "RESOLVED" },
      ];
    case "PENDING":
      return [
        { label: "Resume", target: "IN_PROGRESS" },
        { label: "Resolve", target: "RESOLVED" },
      ];
    case "RESOLVED":
      return [
        { label: "Close", target: "CLOSED" },
        { label: "Reopen", target: "IN_PROGRESS" },
      ];
    default:
      return [];
  }
}
