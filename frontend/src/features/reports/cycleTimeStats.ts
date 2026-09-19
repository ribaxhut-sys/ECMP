import type { CycleTimeSummary } from "@/lib/api/types";

export type CycleTimeBucketRow = {
  key: string;
  labelKey: string;
  count: number;
  /** Whole-percent share of all closed cases in the window. */
  share: number;
};

/** Message key per age band; unknown keys from the API fall back to the key. */
const BUCKET_LABEL_KEY: Record<string, string> = {
  sameDay: "cycleTimeBandSameDay",
  upTo3Days: "cycleTimeBandUpTo3Days",
  upTo7Days: "cycleTimeBandUpTo7Days",
  over7Days: "cycleTimeBandOver7Days",
};

/** Age bands with their share of the closed-case set. */
export function cycleTimeBucketRows(
  summary: CycleTimeSummary | null | undefined,
): CycleTimeBucketRow[] {
  if (!summary || summary.closedCases <= 0) return [];
  const labeled = summary.buckets.filter(
    (bucket) => BUCKET_LABEL_KEY[bucket.key] !== undefined,
  );
  let allocated = 0;
  return labeled.map((bucket, index) => {
    const share =
      index === labeled.length - 1
        ? Math.max(0, 100 - allocated)
        : Math.round((bucket.count / summary.closedCases) * 100);
    allocated += share;
    return {
      key: bucket.key,
      labelKey: BUCKET_LABEL_KEY[bucket.key] as string,
      count: bucket.count,
      share,
    };
  });
}
