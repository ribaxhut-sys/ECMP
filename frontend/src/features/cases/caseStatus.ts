import type { CmCaseStatus } from "@/lib/api/cmCase";
import type { BadgeTone } from "@/shared/ui";

/** Mode A Delivery Transition Subset — status PATCH edges (FR-004). */
const EDGES: ReadonlyArray<readonly [CmCaseStatus, CmCaseStatus]> = [
  ["CREATED", "ASSIGNED"],
  ["CREATED", "CANCELLED"],
  ["ASSIGNED", "IN_PROGRESS"],
  ["ASSIGNED", "ASSIGNED"],
  ["ASSIGNED", "CANCELLED"],
  ["IN_PROGRESS", "ASSIGNED"],
  ["IN_PROGRESS", "CANCELLED"],
];

export function caseStatusTone(status: CmCaseStatus | string): BadgeTone {
  switch (status) {
    case "CREATED":
      return "neutral";
    case "ASSIGNED":
      return "info";
    case "IN_PROGRESS":
      return "primary";
    case "PENDING":
      return "warning";
    case "ESCALATED":
      return "warning";
    case "RESOLVED":
      return "success";
    case "CLOSED":
      return "neutral";
    case "CANCELLED":
      return "danger";
    default:
      return "neutral";
  }
}

export function allowedStatusTargets(
  current: CmCaseStatus,
): CmCaseStatus[] {
  const targets = new Set<CmCaseStatus>();
  for (const [from, to] of EDGES) {
    if (from === current) targets.add(to);
  }
  return [...targets];
}

export function canResolve(status: CmCaseStatus): boolean {
  return status === "IN_PROGRESS";
}

/** UI: offer Resolve for active branch work; may auto-advance to IN_PROGRESS first. */
export function canOfferResolve(status: CmCaseStatus): boolean {
  return (
    status === "CREATED" ||
    status === "ASSIGNED" ||
    status === "IN_PROGRESS"
  );
}

export function canClose(status: CmCaseStatus): boolean {
  return status === "RESOLVED";
}
