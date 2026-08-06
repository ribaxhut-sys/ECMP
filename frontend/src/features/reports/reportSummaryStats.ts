import type { BranchCount, ReportSummary, StatusCount } from "@/lib/api/types";
import type { ProgressMeterTone } from "@/shared/ui";

export type ReportHeadlineCounts = {
  total: number;
  open: number;
  closed: number;
};

export type ResolutionBuckets = {
  resolved: number;
  waiting: number;
  escalated: number;
  inProgress: number;
};

export type BranchPerformanceRow = {
  key: string;
  name: string;
  total: number;
  share: number;
  rank: "top" | "middle" | "lowest";
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
  const waiting =
    (byStatus.get("NEW") ?? 0) +
    (byStatus.get("ASSIGNED") ?? 0) +
    (byStatus.get("PENDING") ?? 0);
  const escalated = byStatus.get("ESCALATED") ?? 0;
  const inProgress = byStatus.get("IN_PROGRESS") ?? 0;

  if (resolved + waiting + escalated + inProgress === 0) return null;

  return { resolved, waiting, escalated, inProgress };
}

/** Rank branches for horizontal performance bars (CSS-only). */
export function branchPerformanceRows(
  rows: BranchCount[] | null | undefined,
): BranchPerformanceRow[] | null {
  if (!rows || rows.length === 0) return null;

  const sorted = [...rows].sort((a, b) => b.total - a.total);
  const max = Math.max(...sorted.map((row) => row.total), 1);
  const last = sorted.length - 1;

  return sorted.map((row, index) => {
    let rank: BranchPerformanceRow["rank"] = "middle";
    if (index === 0) rank = "top";
    else if (index === last) rank = "lowest";

    return {
      key: row.branchId ?? row.branchCode ?? `branch-${index}`,
      name: row.branchName?.trim() || row.branchCode?.trim() || "—",
      total: row.total,
      share: Math.round((row.total / max) * 100),
      rank,
    };
  });
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

/** Highest-volume branch — factual queue proxy, not quality ranking. */
export function highestQueueBranch(
  rows: BranchCount[] | null | undefined,
): BranchCount | null {
  if (!rows || rows.length === 0) return null;
  return [...rows].sort((a, b) => b.total - a.total)[0] ?? null;
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
