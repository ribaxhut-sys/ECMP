/** Pure filter helpers for Pengaduan Internal list. */
import type { InternalComplaint } from "./types";
import { isIncomingInternalComplaint } from "./internalInbox";

export interface InternalListFilters {
  q: string;
  status: string;
  category: string;
  priority: string;
  ownerUnitId: string;
  handlingUnitId: string;
  /** Incoming queue at the caller's handling unit (sidebar badge door). */
  needsReceive: boolean;
}

export function defaultInternalListFilters(): InternalListFilters {
  return {
    q: "",
    status: "",
    category: "",
    priority: "",
    ownerUnitId: "",
    handlingUnitId: "",
    needsReceive: false,
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
    filters.needsReceive
  );
}

export function filterInternalComplaints(
  rows: readonly InternalComplaint[],
  filters: InternalListFilters,
  actorUnitCode?: string | null,
): InternalComplaint[] {
  const q = filters.q.trim().toLowerCase();
  return rows.filter((row) => {
    if (filters.needsReceive) {
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
