import { describe, expect, it } from "vitest";
import type { CycleTimeSummary } from "@/lib/api/types";
import { cycleTimeBucketRows } from "./cycleTimeStats";

const summary = (
  overrides: Partial<CycleTimeSummary> = {},
): CycleTimeSummary => ({
  closedCases: 10,
  averageDays: 4.1,
  medianDays: 4,
  p90Days: 7.4,
  fastestDays: 0.5,
  slowestDays: 9,
  buckets: [
    { key: "sameDay", count: 2 },
    { key: "upTo3Days", count: 3 },
    { key: "upTo7Days", count: 4 },
    { key: "over7Days", count: 1 },
  ],
  ...overrides,
});

describe("cycleTimeBucketRows", () => {
  it("turns each band into a whole-percent share", () => {
    expect(cycleTimeBucketRows(summary()).map((r) => [r.key, r.share])).toEqual([
      ["sameDay", 20],
      ["upTo3Days", 30],
      ["upTo7Days", 40],
      ["over7Days", 10],
    ]);
  });

  it("labels every band it renders", () => {
    for (const row of cycleTimeBucketRows(summary())) {
      expect(row.labelKey).toMatch(/^cycleTimeBand/);
    }
  });

  it("returns nothing when the window closed no cases", () => {
    expect(cycleTimeBucketRows(summary({ closedCases: 0 }))).toEqual([]);
    expect(cycleTimeBucketRows(null)).toEqual([]);
  });

  it("skips bands the UI has no label for instead of rendering a raw key", () => {
    const rows = cycleTimeBucketRows(
      summary({ buckets: [{ key: "someFutureBand", count: 10 }] }),
    );
    expect(rows).toEqual([]);
  });
});
