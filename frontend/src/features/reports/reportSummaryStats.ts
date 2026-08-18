import type { ReportSummary, StatusCount } from "@/lib/api/types";
import type { ProgressMeterTone } from "@/shared/ui";

export type ReportHeadlineCounts = {
  total: number;
  open: number;
  closed: number;
};

/**
 * Mutually exclusive slices of the Aggregate KPI — they must sum to `total`.
 * Status labels arrive from `buildAggregateKpis`:
 * NEW = waiting, ESCALATED = pending approval, ASSIGNED = approved,
 * PENDING = HQ_SCHEDULED (still on the escalation path), IN_PROGRESS = handling.
 */
export type ResolutionBuckets = {
  resolved: number;
  /** NEW — open, not yet escalated or worked. */
  waiting: number;
  /** ESCALATED — escalation awaiting supervisor approval. */
  escalated: number;
  /** ASSIGNED — escalation approved, on its way to Pusat. */
  escalationApproved: number;
  /** PENDING — HQ visit already scheduled (ESCALATION_ACTIVE). */
  escalationScheduled: number;
  inProgress: number;
};

export type OperationalHealth = {
  score: number;
  tone: ProgressMeterTone;
  labelKey: "healthy" | "attention" | "critical";
};

/** Derive headline counts from report summary (or by-status rows). */
export function reportHeadlineCounts(
  summary: Pick<ReportSummary, "total" | "byStatus"> | null | undefined,
): ReportHeadlineCounts | null {
  if (!summary) return null;
  return {
    total: summary.total,
    open: countOpen(summary.byStatus),
    closed: countClosed(summary.byStatus),
  };
}

/** Resolution rate as whole-percent of closed / total. */
export function resolutionRatePercent(
  headlines: ReportHeadlineCounts | null | undefined,
): number | null {
  if (!headlines || headlines.total <= 0) return null;
  return Math.round((headlines.closed / headlines.total) * 100);
}

/** Bucket status rows for resolution-effectiveness cards. */
export function resolutionBuckets(
  rows: StatusCount[] | null | undefined,
): ResolutionBuckets | null {
  if (!rows || rows.length === 0) return null;

  const byStatus = new Map(rows.map((row) => [row.status, row.count]));
  const resolved =
    (byStatus.get("RESOLVED") ?? 0) + (byStatus.get("CLOSED") ?? 0);
  const waiting = byStatus.get("NEW") ?? 0;
  const escalated = byStatus.get("ESCALATED") ?? 0;
  const escalationApproved = byStatus.get("ASSIGNED") ?? 0;
  const escalationScheduled = byStatus.get("PENDING") ?? 0;
  const inProgress = byStatus.get("IN_PROGRESS") ?? 0;

  if (
    resolved +
      waiting +
      escalated +
      escalationApproved +
      escalationScheduled +
      inProgress ===
    0
  ) {
    return null;
  }

  return {
    resolved,
    waiting,
    escalated,
    escalationApproved,
    escalationScheduled,
    inProgress,
  };
}

/** Every live escalation slice, including HQ_SCHEDULED. */
export function escalationTotal(
  buckets: ResolutionBuckets | null | undefined,
): number {
  if (!buckets) return 0;
  return (
    buckets.escalated +
    buckets.escalationApproved +
    buckets.escalationScheduled
  );
}

/** Operational health from resolution rate (higher closure = healthier). */
export function operationalHealthFromRate(
  rate: number | null | undefined,
): OperationalHealth | null {
  if (rate == null) return null;
  if (rate >= 60) {
    return { score: rate, tone: "healthy", labelKey: "healthy" };
  }
  if (rate >= 30) {
    return { score: rate, tone: "attention", labelKey: "attention" };
  }
  return { score: rate, tone: "critical", labelKey: "critical" };
}

function countOpen(rows: StatusCount[]): number {
  return rows
    .filter((row) => row.status !== "CLOSED" && row.status !== "RESOLVED")
    .reduce((acc, row) => acc + row.count, 0);
}

function countClosed(rows: StatusCount[]): number {
  return rows
    .filter((row) => row.status === "CLOSED" || row.status === "RESOLVED")
    .reduce((acc, row) => acc + row.count, 0);
}
