/**
 * Pusat unit codes — single FE mirror of the backend rule in
 * `app/core/authorization/visibility.py`.
 *
 * Pusat is not one door: a taxpayer escalated to Pusat may be directed to CRO,
 * to Sekretariat, or to a Suban. Those sub-units are coded as a root code plus
 * a separator ("PUSAT-CRO", "PUSAT-SUBAN-1"), so every gate that asks "is this
 * Pusat?" must accept them too. A separator is required — "PUSATAKA" is a
 * different branch, not a Pusat sub-unit.
 */

/** Root codes only; sub-units are derived, never enumerated. */
export const PUSAT_UNIT_ROOT_CODES = [
  "PUSAT",
  "HO",
  "HEAD_OFFICE",
  "HEAD-OFFICE",
] as const;

export const CANONICAL_PUSAT_UNIT_CODE = "PUSAT";

/** "_" is not a separator: it is a LIKE wildcard on the SQL side. */
const PUSAT_SUBUNIT_SEPARATORS = ["-", ".", "/"] as const;

const ROOT_SET = new Set<string>(PUSAT_UNIT_ROOT_CODES);

export function isPusatUnitCode(code: string | null | undefined): boolean {
  const normalized = (code || "").trim().toUpperCase();
  if (!normalized) return false;
  if (ROOT_SET.has(normalized)) return true;
  return PUSAT_UNIT_ROOT_CODES.some((root) =>
    PUSAT_SUBUNIT_SEPARATORS.some((sep) => normalized.startsWith(`${root}${sep}`)),
  );
}

/** True only for a root Pusat code — "PUSAT-CRO" is a sub-unit, not the root. */
export function isPusatRootUnitCode(code: string | null | undefined): boolean {
  return ROOT_SET.has((code || "").trim().toUpperCase());
}
