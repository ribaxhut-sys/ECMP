import type { ReportSummary, StatusCount } from "@/lib/api/types";
import {
  escalationTotal,
  reportHeadlineCounts,
  resolutionBuckets,
  resolutionRatePercent,
} from "./reportSummaryStats";

export type ReportBriefingFacts = {
  total: number;
  closed: number;
  open: number;
  escalated: number;
  waiting: number;
};

/** Headline numbers for the 15-second reading at the top of /reports. */
export function reportBriefingFacts(
  summary: ReportSummary | null | undefined,
  byStatus?: StatusCount[] | null,
): ReportBriefingFacts | null {
  const headlines = reportHeadlineCounts(summary);
  if (!headlines) return null;
  const buckets = resolutionBuckets(byStatus ?? summary?.byStatus);
  return {
    total: headlines.total,
    closed: headlines.closed,
    open: headlines.open,
    escalated: escalationTotal(buckets),
    waiting: buckets?.waiting ?? 0,
  };
}

/** Current minus previous; null when there is nothing to compare. */
export function countDelta(
  current: number,
  previous: number | null | undefined,
): number | null {
  if (previous == null) return null;
  return current - previous;
}

export function signedCount(delta: number): string {
  if (delta > 0) return `+${delta}`;
  return String(delta);
}

export function rateDelta(
  current: number | null,
  previous: number | null,
): number | null {
  if (current == null || previous == null) return null;
  return current - previous;
}

export function previousRateFromSummary(
  summary: ReportSummary | null | undefined,
): number | null {
  return resolutionRatePercent(reportHeadlineCounts(summary));
}
