/** Pure filter helpers for Pengaduan Internal list. */
import { toLocalDateKey } from "@/shared/utils/datetime";
import type { InternalComplaint } from "./types";
import { isActionNeededInternalComplaint, isIncomingInternalComplaint } from "./internalInbox";

export interface InternalListFilters {
  q: string;
  status: string;
  category: string;
  priority: string;
  ownerUnitId: string;
  handlingUnitId: string;
  /** Inclusive `createdAt` period bounds as `YYYY-MM-DD` calendar days (Asia/Jakarta). */
  dateFrom: string;
  dateTo: string;
  /** Incoming queue at the caller's handling unit (sidebar badge door). */
  needsReceive: boolean;
  /** Work waiting on the signed-in unit (API-551). */
  needsAction: boolean;
}

export function defaultInternalListFilters(): InternalListFilters {
  return {
    q: "",
    status: "",
    category: "",
    priority: "",
    ownerUnitId: "",
    handlingUnitId: "",
    dateFrom: "",
    dateTo: "",
    needsReceive: false,
    needsAction: false,
  };
}

export function hasActiveInternalFilters(filters: InternalListFilters): boolean {
  return (
    Boolean(filters.q && filters.q.trim()) ||
    Boolean(filters.status && filters.status.trim()) ||
    Boolean(filters.category && filters.category.trim()) ||
    Boolean(filters.priority && filters.priority.trim()) ||
    Boolean(filters.ownerUnitId && filters.ownerUnitId.trim()) ||
    Boolean(filters.handlingUnitId && filters.handlingUnitId.trim()) ||
    Boolean(filters.dateFrom && filters.dateFrom.trim()) ||
    Boolean(filters.dateTo && filters.dateTo.trim()) ||
    filters.needsReceive ||
    filters.needsAction
  );
}

/**
 * `createdAt` as an Asia/Jakarta calendar day, or `null` when the instant is
 * unusable — the period filter compares `YYYY-MM-DD` strings, which sort
 * lexicographically, so no Date math is needed past this point.
 */
function createdDateKey(row: InternalComplaint): string | null {
  const created = new Date(row.createdAt);
  if (Number.isNaN(created.getTime())) return null;
  return toLocalDateKey(created);
}

export function filterInternalComplaints(
  rows: readonly InternalComplaint[],
  filters: InternalListFilters,
  actorUnitCode?: string | null,
): InternalComplaint[] {
  const q = filters.q.trim().toLowerCase();
  const dateFrom = filters.dateFrom?.trim() ?? "";
  const dateTo = filters.dateTo?.trim() ?? "";
  return rows.filter((row) => {
    if (filters.needsAction) {
      if (actorUnitCode === undefined) return true;
      if (!isActionNeededInternalComplaint(row, actorUnitCode)) return false;
    } else if (filters.needsReceive) {
      if (actorUnitCode === undefined) return true;
      if (!isIncomingInternalComplaint(row, actorUnitCode)) return false;
    }
    if (filters.status && row.status !== filters.status) return false;
    if (filters.category && row.category !== filters.category) return false;
    if (filters.priority && row.priority !== filters.priority) return false;
    if (filters.ownerUnitId && row.ownerUnitId !== filters.ownerUnitId) return false;
    if (
      filters.handlingUnitId &&
      row.handlingUnitId !== filters.handlingUnitId
    ) {
      return false;
    }
    if (dateFrom || dateTo) {
      // A row whose createdAt cannot be read has no place in a period — better
      // dropped from a dated report than silently counted in every period.
      const day = createdDateKey(row);
      if (day === null) return false;
      if (dateFrom && day < dateFrom) return false;
      if (dateTo && day > dateTo) return false;
    }
    if (!q) return true;
    const hay =
      `${row.number} ${row.title} ${row.description} ${row.createdByName ?? ""} ${row.ownerUnitId} ${row.handlingUnitId}`.toLowerCase();
    return hay.includes(q);
  });
}

export function sortByMostRecent(
  rows: readonly InternalComplaint[],
): InternalComplaint[] {
  return [...rows].sort(
    (a, b) => new Date(b.createdAt).getTime() - new Date(a.createdAt).getTime(),
  );
}

/** True when a row has something the current owner/handling unit should act on. */
export function needsAttention(row: InternalComplaint): boolean {
  return (
    row.status === "RESOLVED" ||
    row.transferRequestStatus === "PENDING" ||
    row.withdrawRequestStatus === "PENDING"
  );
}

/**
 * Dashboard "Perlu tindakan Anda" ordering: rows needing action first (most
 * recent first within that group), then everything else most-recent-first.
 */
export function sortForDashboardAction(
  rows: readonly InternalComplaint[],
): InternalComplaint[] {
  return sortByMostRecent(rows).sort((a, b) => {
    const aUrgent = needsAttention(a);
    const bUrgent = needsAttention(b);
    if (aUrgent === bUrgent) return 0;
    return aUrgent ? -1 : 1;
  });
}
