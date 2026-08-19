/** Status slices for Pengaduan Internal work queues (Mode A). */

export const INTERNAL_ASSIGNMENT_STATUSES = ["ASSIGNED", "CREATED"] as const;
/** Work list: already routed to a handling unit (Assigned) or actively handled. */
export const INTERNAL_FOLLOW_UP_STATUSES = ["IN_PROGRESS", "ASSIGNED"] as const;
export const INTERNAL_VERIFICATION_STATUSES = ["RESOLVED"] as const;

export type InternalQueueKind =
  | "assignments"
  | "followUp"
  | "verification"
  | "reports";

export interface InternalQueueCounts {
  assignments: number;
  followUp: number;
  verification: number;
}

export interface InternalQueueEmptyHint {
  titleKey: string;
  descriptionKey: string;
  descriptionValues?: { count: number };
  primaryHref?: string;
  primaryLabelKey?: string;
  secondaryHref?: string;
  secondaryLabelKey?: string;
}

export function countMatchingStatus(
  rows: readonly { status: string }[],
  statuses: readonly string[],
): number {
  const allowed = new Set(statuses);
  return rows.filter((row) => allowed.has(String(row.status))).length;
}

export function siblingQueueCounts(
  rows: readonly { status: string }[],
): InternalQueueCounts {
  return {
    assignments: countMatchingStatus(rows, INTERNAL_ASSIGNMENT_STATUSES),
    followUp: countMatchingStatus(rows, INTERNAL_FOLLOW_UP_STATUSES),
    verification: countMatchingStatus(rows, INTERNAL_VERIFICATION_STATUSES),
  };
}

/**
 * Empty copy for a queue. Follow-up lists ASSIGNED + IN_PROGRESS. CREATED
 * tickets stay in Antrian terima; RESOLVED stays in Persetujuan penutup.
 */
export function resolveQueueEmptyHint(
  queue: InternalQueueKind,
  counts: InternalQueueCounts,
): InternalQueueEmptyHint {
  if (queue === "followUp") {
    if (counts.assignments > 0) {
      return {
        titleKey: "followUpListEmpty",
        descriptionKey: "followUpEmptyWaitingReceive",
        descriptionValues: { count: counts.assignments },
        primaryHref: "/internal/assignments",
        primaryLabelKey: "openReceiveQueue",
        ...(counts.verification > 0
          ? {
              secondaryHref: "/internal/verification",
              secondaryLabelKey: "openVerificationQueue",
            }
          : {}),
      };
    }
    if (counts.verification > 0) {
      return {
        titleKey: "followUpListEmpty",
        descriptionKey: "followUpEmptyWaitingVerification",
        descriptionValues: { count: counts.verification },
        primaryHref: "/internal/verification",
        primaryLabelKey: "openVerificationQueue",
      };
    }
    return {
      titleKey: "followUpListEmpty",
      descriptionKey: "followUpEmptyDescription",
    };
  }
  if (queue === "assignments") {
    return {
      titleKey: "assignmentsEmpty",
      descriptionKey: "assignmentsEmptyDescription",
    };
  }
  if (queue === "verification") {
    return {
      titleKey: "verificationEmpty",
      descriptionKey: "verificationEmptyDescription",
    };
  }
  return {
    titleKey: "listEmpty",
    descriptionKey: "listEmptyDescription",
  };
}
