/**
 * Partition Aggregate Case rows into operator-facing Penanganan groups.
 * Case remains SoT behind the UI; labels/groups are presentation only (DEC-020).
 */

import { officerInitials } from "./officerDisplayName";

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
  options?: { complaintOnHqPath?: boolean },
): PenangananGroupId {
  const s = (status || "").trim().toUpperCase();
  if (s === "CANCELLED") return "cancelled";
  if (s === "RESOLVED" || s === "CLOSED") return "done";
  if (s === "ESCALATED") return "pusat";
  if (options?.complaintOnHqPath && s !== "") return "pusat";
  return "open";
}

export interface PenangananPartitions<T extends { status: string }> {
  open: T[];
  pusat: T[];
  done: T[];
  cancelled: T[];
}

export function partitionPenanganan<T extends { status: string }>(
  items: readonly T[],
  options?: { complaintOnHqPath?: boolean },
): PenangananPartitions<T> {
  const open: T[] = [];
  const pusat: T[] = [];
  const done: T[] = [];
  const cancelled: T[] = [];
  for (const item of items) {
    const group = penangananGroupForStatus(item.status, options);
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
