/** Cabang ↔ Pusat transfer helpers (mirror backend DEFAULT_PUSAT_UNIT_CODES). */

export const PUSAT_UNIT_CODES = new Set([
  "PUSAT",
  "HO",
  "HEAD_OFFICE",
  "HEAD-OFFICE",
]);

export function isPusatUnitCode(code: string | null | undefined): boolean {
  const normalized = (code || "").trim().toUpperCase();
  return Boolean(normalized) && PUSAT_UNIT_CODES.has(normalized);
}

/**
 * Allowed destinations for Handling Unit transfer:
 * - from Cabang → only Pusat codes
 * - from Pusat → only non-Pusat (cabang) codes
 */
export function filterTransferDestinations<T extends { code: string }>(
  branches: readonly T[],
  sourceUnitId: string | null | undefined,
): T[] {
  const source = (sourceUnitId || "").trim();
  if (!source) return [];
  const fromPusat = isPusatUnitCode(source);
  return branches.filter((b) => {
    const code = (b.code || "").trim();
    if (!code || code.toUpperCase() === source.toUpperCase()) return false;
    return fromPusat ? !isPusatUnitCode(code) : isPusatUnitCode(code);
  });
}

/** Prefer short human label so native <select> stays compact. */
export function formatUnitOptionLabel(
  code: string,
  name?: string | null,
): string {
  const c = (code || "").trim();
  const n = (name || "").trim();
  if (!c && !n) return "";
  if (n) return n;
  return c;
}

/** Related Aggregate option: number only (native select width follows longest option). */
export function formatRelatedComplaintOptionLabel(
  complaintNumber: string,
): string {
  return (complaintNumber || "").trim();
}
