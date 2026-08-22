/**
 * Partition Aggregate Case rows into operator-facing Penanganan groups.
 * Case remains SoT behind the UI; labels/groups are presentation only (DEC-020).
 */

import { officerDisplayName, officerInitials } from "./officerDisplayName";

export type PenangananGroupId = "open" | "pusat" | "done" | "cancelled";

/** Intake dispositions: complaint actively on HQ escalation path (not returned/rejected). */
const HQ_INTAKE_DISPOSITIONS = new Set([
  "ESCALATE_PENDING_APPROVAL",
  "ESCALATE_APPROVED",
  "HQ_SCHEDULED",
]);

export function isHqIntakeDisposition(
  disposition: string | null | undefined,
): boolean {
  const d = (disposition || "").trim().toUpperCase();
  return d.length > 0 && HQ_INTAKE_DISPOSITIONS.has(d);
}

/** Operator-facing HQ-path phase. Grouping stays `hq_waiting`; copy splits. */
export type HqPathPhase =
  | "pending_approval"
  | "awaiting_accept"
  | "accepted_unscheduled"
  | "scheduled";

export function resolveHqPathPhase(input: {
  intakeDisposition?: string | null;
  hqAcceptedAt?: string | null;
}): HqPathPhase | null {
  const d = (input.intakeDisposition || "").trim().toUpperCase();
  if (d === "ESCALATE_PENDING_APPROVAL") return "pending_approval";
  if (d === "HQ_SCHEDULED") return "scheduled";
  if (d === "ESCALATE_APPROVED") {
    return input.hqAcceptedAt ? "accepted_unscheduled" : "awaiting_accept";
  }
  return null;
}

export interface HqPathCopyKeys {
  list: string;
  listWithOfficer: string;
  emptyTitle: string;
  emptyDescription: string;
  groupPusat: string;
  pathTitle: string;
  pathDescription: string;
  pageTitle: string;
  pageDescription: string;
}

export function hqPathCopyKeys(phase: HqPathPhase): HqPathCopyKeys {
  switch (phase) {
    case "pending_approval":
      return {
        list: "penangananListHqWaiting",
        listWithOfficer: "penangananListHqWaitingWithOfficer",
        emptyTitle: "penangananEmptyHqTitle",
        emptyDescription: "penangananEmptyHqDescription",
        groupPusat: "penangananGroupPusat",
        pathTitle: "penangananHqPathTitle",
        pathDescription: "penangananHqPathDescription",
        pageTitle: "intakeEscalateBannerTitle",
        pageDescription: "intakeEscalateBannerDescription",
      };
    case "awaiting_accept":
      return {
        list: "penangananListHqAwaitingAccept",
        listWithOfficer: "penangananListHqAwaitingAcceptWithOfficer",
        emptyTitle: "penangananEmptyHqAwaitingAcceptTitle",
        emptyDescription: "penangananEmptyHqAwaitingAcceptDescription",
        groupPusat: "penangananGroupPusat",
        pathTitle: "penangananHqPathTitle",
        pathDescription: "penangananHqPathDescription",
        pageTitle: "escalationApproved",
        pageDescription: "escalationApprovedPageDescription",
      };
    case "accepted_unscheduled":
      return {
        list: "penangananListHqAccepted",
        listWithOfficer: "penangananListHqAcceptedWithOfficer",
        emptyTitle: "penangananEmptyHqAcceptedTitle",
        emptyDescription: "penangananEmptyHqAcceptedDescription",
        groupPusat: "penangananGroupPusat",
        pathTitle: "penangananHqPathTitle",
        pathDescription: "penangananHqPathDescription",
        pageTitle: "hqPathAcceptedPageTitle",
        pageDescription: "hqPathAcceptedPageDescription",
      };
    case "scheduled":
      return {
        list: "penangananListHqScheduled",
        listWithOfficer: "penangananListHqScheduledWithOfficer",
        emptyTitle: "penangananEmptyHqScheduledTitle",
        emptyDescription: "penangananEmptyHqScheduledDescription",
        groupPusat: "penangananGroupPusatScheduled",
        pathTitle: "penangananHqPathScheduledTitle",
        pathDescription: "penangananHqPathScheduledDescription",
        pageTitle: "hqPathScheduledPageTitle",
        pageDescription: "hqPathScheduledPageDescription",
      };
  }
}

export function isComplaintHandlingClosed(input: {
  complaintStatus?: string | null;
  intakeDisposition?: string | null;
}): boolean {
  const status = (input.complaintStatus || "").trim().toUpperCase();
  const disposition = (input.intakeDisposition || "").trim().toUpperCase();
  return status === "CLOSED" || disposition === "BRANCH_CLOSED";
}

/**
 * Map Case status (+ optional complaint HQ path) → Penanganan group.
 * Accepts statuses beyond the Mode A PATCH subset (e.g. ESCALATED) if API returns them.
 */
export function penangananGroupForStatus(
  status: string | null | undefined,
  options?: { complaintOnHqPath?: boolean; escalatedToPusat?: boolean },
): PenangananGroupId {
  const s = (status || "").trim().toUpperCase();
  if (s === "CANCELLED") return "cancelled";
  if (s === "RESOLVED" || s === "CLOSED") return "done";
  if (s === "ESCALATED") return "pusat";
  if (options?.escalatedToPusat) return "pusat";
  if (options?.complaintOnHqPath && s !== "") return "pusat";
  return "open";
}

export interface PenangananPartitions<T extends { status: string }> {
  open: T[];
  pusat: T[];
  done: T[];
  cancelled: T[];
}

export function partitionPenanganan<
  T extends { status: string; escalatedToPusat?: boolean },
>(
  items: readonly T[],
  options?: { complaintOnHqPath?: boolean },
): PenangananPartitions<T> {
  const open: T[] = [];
  const pusat: T[] = [];
  const done: T[] = [];
  const cancelled: T[] = [];
  for (const item of items) {
    const group = penangananGroupForStatus(item.status, {
      ...options,
      escalatedToPusat: item.escalatedToPusat,
    });
    if (group === "open") open.push(item);
    else if (group === "pusat") pusat.push(item);
    else if (group === "done") done.push(item);
    else cancelled.push(item);
  }
  return { open, pusat, done, cancelled };
}

export function penangananSummaryCounts(
  parts: PenangananPartitions<{ status: string }>,
): { open: number; pusat: number; done: number; cancelled: number } {
  return {
    open: parts.open.length,
    pusat: parts.pusat.length,
    done: parts.done.length,
    cancelled: parts.cancelled.length,
  };
}

/** PIC yang ditampilkan pada kolom Aggregate list: case terbuka/HQ pertama. */
export type PenangananHandlerRef = {
  /** Identitas unik user; jatuh ke nama bila API tidak mengirim id. */
  key: string;
  name: string;
};

export function handlerRefFromCases(
  items: readonly {
    status: string;
    handlingClaimedBy?: string | null;
    handlingClaimedByName?: string | null;
  }[],
  intakeDisposition?: string | null,
): PenangananHandlerRef | null {
  const parts = partitionPenanganan(items, {
    complaintOnHqPath: isHqIntakeDisposition(intakeDisposition),
  });
  for (const item of [...parts.open, ...parts.pusat]) {
    const name = officerDisplayName(item.handlingClaimedByName);
    if (!name) continue;
    return { key: (item.handlingClaimedBy || "").trim() || name, name };
  }
  return null;
}

/** Counts for Aggregate list column (open / HQ / done). */
export function handlerInitialsFromCases(
  items: readonly {
    status: string;
    handlingClaimedByName?: string | null;
  }[],
  intakeDisposition?: string | null,
): string | null {
  const parts = partitionPenanganan(items, {
    complaintOnHqPath: isHqIntakeDisposition(intakeDisposition),
  });
  for (const item of [...parts.open, ...parts.pusat]) {
    const initials = officerInitials(item.handlingClaimedByName);
    if (initials) return initials;
  }
  return null;
}

export function penangananCountsFromCases(
  items: readonly { status: string }[],
  intakeDisposition?: string | null,
): { open: number; pusat: number; done: number; cancelled: number } {
  return penangananSummaryCounts(
    partitionPenanganan(items, {
      complaintOnHqPath: isHqIntakeDisposition(intakeDisposition),
    }),
  );
}

export type PenangananCounts = {
  open: number;
  pusat: number;
  done: number;
};

/**
 * Build summary segments, omitting zero counts.
 * Example: open=2, pusat=0, done=0 → ["2 terbuka"]
 */
export function buildPenangananSummarySegments(
  counts: PenangananCounts,
  labels: { open: (n: number) => string; pusat: (n: number) => string; done: (n: number) => string },
): string[] {
  const parts: string[] = [];
  if (counts.open > 0) parts.push(labels.open(counts.open));
  if (counts.pusat > 0) parts.push(labels.pusat(counts.pusat));
  if (counts.done > 0) parts.push(labels.done(counts.done));
  return parts;
}

export function joinPenangananSummarySegments(parts: readonly string[]): string | null {
  if (parts.length === 0) return null;
  return parts.join(" · ");
}

/**
 * List/detail empty-state kind (priority order).
 * "none" = Belum ada penanganan (open branch, zero cases only).
 */
export type PenangananContextKind =
  | "closed"
  | "hq_waiting"
  | "has_counts"
  | "none";

export function resolvePenangananContextKind(input: {
  complaintStatus?: string | null;
  intakeDisposition?: string | null;
  counts: PenangananCounts;
}): PenangananContextKind {
  if (
    isComplaintHandlingClosed({
      complaintStatus: input.complaintStatus,
      intakeDisposition: input.intakeDisposition,
    })
  ) {
    return "closed";
  }
  if (isHqIntakeDisposition(input.intakeDisposition)) {
    return "hq_waiting";
  }
  const total =
    input.counts.open + input.counts.pusat + input.counts.done;
  if (total > 0) return "has_counts";
  return "none";
}
