/** Pure filter helpers for Pengaduan Internal list. */
import type { InternalComplaint } from "./types";

export interface InternalListFilters {
  q: string;
  status: string;
  category: string;
  priority: string;
  ownerUnitId: string;
  handlingUnitId: string;
}

export function defaultInternalListFilters(): InternalListFilters {
  return {
    q: "",
    status: "",
    category: "",
    priority: "",
    ownerUnitId: "",
    handlingUnitId: "",
  };
}

export function hasActiveInternalFilters(filters: InternalListFilters): boolean {
  return Object.values(filters).some((v) => Boolean(v && String(v).trim()));
}

export function filterInternalComplaints(
  rows: readonly InternalComplaint[],
  filters: InternalListFilters,
): InternalComplaint[] {
  const q = filters.q.trim().toLowerCase();
  return rows.filter((row) => {
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
