/** Pure aggregation helpers for the Pengaduan Internal "Ringkasan" analytics panel. */
import type { InternalCountBucket as ApiCountBucket } from "@/lib/api";
import { displayInternalUnitCode } from "./transferDirection";
import {
  INTERNAL_PRIORITIES,
  INTERNAL_STATUSES,
  STATUS_LABEL_KEY,
  type InternalComplaint,
  type InternalPriority,
} from "./types";

export interface InternalCountBucket {
  key: string;
  labelKey: string;
  count: number;
}

export interface InternalUnitBucket {
  unitId: string;
  count: number;
}

/** One bucket per status, in `INTERNAL_STATUSES` order, zero-filled — stable chart legend. */
export function countByStatus(
  rows: readonly InternalComplaint[],
): InternalCountBucket[] {
  const counts = new Map<string, number>();
  for (const row of rows) {
    const key = row.status;
    counts.set(key, (counts.get(key) ?? 0) + 1);
  }
  return INTERNAL_STATUSES.map((status) => ({
    key: status,
    labelKey: STATUS_LABEL_KEY[status],
    count: counts.get(status) ?? 0,
  }));
}

/** One bucket per priority, in `INTERNAL_PRIORITIES` order, zero-filled. */
export function countByPriority(
  rows: readonly InternalComplaint[],
): Record<InternalPriority, number> {
  const counts: Record<InternalPriority, number> = {
    LOW: 0,
    MEDIUM: 0,
    HIGH: 0,
    CRITICAL: 0,
  };
  for (const row of rows) {
    const key = row.priority as InternalPriority;
    if (key in counts) counts[key] += 1;
  }
  return counts;
}

/** Handling-unit buckets sorted by volume desc, ties broken alphabetically. */
export function countByHandlingUnit(
  rows: readonly InternalComplaint[],
): InternalUnitBucket[] {
  const counts = new Map<string, number>();
  for (const row of rows) {
    const key = displayInternalUnitCode(row.handlingUnitId) || "—";
    counts.set(key, (counts.get(key) ?? 0) + 1);
  }
  return [...counts.entries()]
    .map(([unitId, count]) => ({ unitId, count }))
    .sort((a, b) => b.count - a.count || a.unitId.localeCompare(b.unitId));
}

export function maxCount(buckets: readonly { count: number }[]): number {
  return buckets.reduce((max, b) => Math.max(max, b.count), 0);
}


/**
 * Server-counted buckets (API-554) reshaped for the same meters the
 * client-side counters feed, so the cards render identically whichever
 * source the page is using.
 */
export function statusBucketsFromSummary(
  buckets: readonly ApiCountBucket[],
): InternalCountBucket[] {
  const counts = new Map(buckets.map((b) => [b.key, b.count]));
  return INTERNAL_STATUSES.map((status) => ({
    key: status,
    labelKey: STATUS_LABEL_KEY[status],
    count: counts.get(status) ?? 0,
  }));
}

export function priorityCountsFromSummary(
  buckets: readonly ApiCountBucket[],
): Record<InternalPriority, number> {
  const counts = new Map(buckets.map((b) => [b.key, b.count]));
  return INTERNAL_PRIORITIES.reduce(
    (acc, priority) => {
      acc[priority] = counts.get(priority) ?? 0;
      return acc;
    },
    { LOW: 0, MEDIUM: 0, HIGH: 0, CRITICAL: 0 } as Record<InternalPriority, number>,
  );
}

/**
 * Unit codes come back raw. They are displayed the way the tables do, and every
 * Pusat variant collapses to one code — so the buckets are merged after the
 * mapping, or `PUSAT-CRO` and `PUSAT` would draw two bars with the same label.
 */
export function unitBucketsFromSummary(
  buckets: readonly ApiCountBucket[],
): InternalUnitBucket[] {
  const merged = new Map<string, number>();
  for (const bucket of buckets) {
    const unitId = displayInternalUnitCode(bucket.key) || "—";
    merged.set(unitId, (merged.get(unitId) ?? 0) + bucket.count);
  }
  return [...merged.entries()]
    .map(([unitId, count]) => ({ unitId, count }))
    .sort((a, b) => b.count - a.count || a.unitId.localeCompare(b.unitId));
}
