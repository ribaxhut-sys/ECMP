/**
 * Namespace path helpers (Mode A).
 *
 * After DEC-026 M-026-2, Foundation `/api/v1/complaints` HTTP is retired.
 * Helpers remain so leftover clients are not mistaken for `/api/v1/cm`.
 * Mode B remains CLOSED.
 */

/** Foundation / Sprint delivery lifecycle (legacy ECMF). */
export const FOUNDATION_COMPLAINTS_BASE = "/api/v1/complaints";

/** CM Batch 1 Aggregate intake (FRD-CM-001 / API-500…512). */
export const CM_BATCH1_AGGREGATE_BASE = "/api/v1/cm";

export function isFoundationComplaintsPath(path: string): boolean {
  const normalized = path.trim();
  return (
    normalized === FOUNDATION_COMPLAINTS_BASE ||
    normalized.startsWith(`${FOUNDATION_COMPLAINTS_BASE}/`) ||
    normalized.startsWith(`${FOUNDATION_COMPLAINTS_BASE}?`)
  );
}

export function isCmBatch1AggregatePath(path: string): boolean {
  const normalized = path.trim();
  return (
    normalized === CM_BATCH1_AGGREGATE_BASE ||
    normalized.startsWith(`${CM_BATCH1_AGGREGATE_BASE}/`) ||
    normalized.startsWith(`${CM_BATCH1_AGGREGATE_BASE}?`)
  );
}

/** True when a path clearly belongs to one SoT and not the other. */
export function dualSotNamespaceOf(
  path: string,
): "foundation" | "aggregate" | "unknown" {
  const foundation = isFoundationComplaintsPath(path);
  const aggregate = isCmBatch1AggregatePath(path);
  if (foundation && !aggregate) return "foundation";
  if (aggregate && !foundation) return "aggregate";
  return "unknown";
}
