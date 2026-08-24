/**
 * Pusat unit codes — single FE mirror of the backend rule in
 * `app/core/authorization/visibility.py`.
 *
 * Pusat visibility still covers CRO / Sekretariat / Suban sub-units. HQ
 * **arrival schedule** destinations are CRO only — Suban and Sekretariat are
 * not booked in this app (branch closes with a redirect note instead).
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

/** Compact destination label from a Pusat unit code: PUSAT-CRO → CRO. */
export function pusatUnitShortCode(code: string | null | undefined): string {
  const normalized = (code || "").trim().toUpperCase();
  if (!normalized) return "";
  for (const root of PUSAT_UNIT_ROOT_CODES) {
    for (const sep of PUSAT_SUBUNIT_SEPARATORS) {
      const prefix = `${root}${sep}`;
      if (normalized.startsWith(prefix) && normalized.length > prefix.length) {
        return normalized.slice(prefix.length);
      }
    }
  }
  return normalized;
}

/**
 * HQ visit schedule door — CRO only (`PUSAT-CRO`, `HO-CRO`, …).
 * Suban / Sekretariat are not schedule destinations in this app.
 */
export function isHqScheduleDestinationUnitCode(
  code: string | null | undefined,
): boolean {
  if (!isPusatUnitCode(code) || isPusatRootUnitCode(code)) return false;
  const short = pusatUnitShortCode(code).toUpperCase();
  return short === "CRO" || short.startsWith("CRO-") || short.startsWith("CRO.");
}

/** Canonical lab/prod code when the directory has not yet returned a CRO row. */
export const DEFAULT_HQ_SCHEDULE_DESTINATION_UNIT_CODE = "PUSAT-CRO";

/**
 * Resolve the single HQ arrival destination — CRO only, no user pick.
 * Prefer an exact `PUSAT-CRO` / `HO-CRO` match, else the first CRO unit in
 * the directory, else the canonical default.
 */
export function resolveDefaultHqScheduleDestinationUnitCode(
  units: readonly { code: string }[],
): string {
  const croCodes = units
    .map((unit) => unit.code.trim())
    .filter((code) => isHqScheduleDestinationUnitCode(code));
  const preferred = croCodes.find((code) => {
    const short = pusatUnitShortCode(code).toUpperCase();
    return short === "CRO";
  });
  return preferred || croCodes[0] || DEFAULT_HQ_SCHEDULE_DESTINATION_UNIT_CODE;
}
