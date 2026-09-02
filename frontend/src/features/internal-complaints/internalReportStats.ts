/** Pure aggregation helpers for the Pengaduan Internal "Ringkasan" analytics panel. */
import { displayInternalUnitCode } from "./transferDirection";
import {
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
