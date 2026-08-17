/** Cabang ↔ Pusat transfer helpers (mirror backend DEFAULT_PUSAT_UNIT_CODES). */

export const PUSAT_UNIT_CODES = new Set([
  "PUSAT",
  "HO",
  "HEAD_OFFICE",
  "HEAD-OFFICE",
]);

export const CANONICAL_PUSAT_UNIT_CODE = "PUSAT";

export function isPusatUnitCode(code: string | null | undefined): boolean {
  const normalized = (code || "").trim().toUpperCase();
  return Boolean(normalized) && PUSAT_UNIT_CODES.has(normalized);
}

/**
 * Source unit for create-form transfer rules.
 * Missing membership (Admin / Kantor Pusat) is treated as Pusat.
 * Branch codes stay as-is; Pusat aliases collapse to PUSAT.
 */
export function resolveCreateSourceUnitCode(
  branchCode: string | null | undefined,
  options?: { treatMissingAsPusat?: boolean },
): string | null {
  const code = (branchCode || "").trim();
  if (code) {
    return isPusatUnitCode(code) ? CANONICAL_PUSAT_UNIT_CODE : code;
  }
  return options?.treatMissingAsPusat === false
    ? null
    : CANONICAL_PUSAT_UNIT_CODE;
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

export const ADMIN_FAMILY_ROLES = new Set([
  "ADMIN",
  "ADMINISTRATOR",
  "SUPER_ADMIN",
]);

export function isAdminFamily(roles: readonly string[]): boolean {
  return roles.some((role) =>
    ADMIN_FAMILY_ROLES.has(role.trim().toUpperCase()),
  );
}

/**
 * Actor source for transfer destination lists.
 * Admin / Pusat → PUSAT (may pick cabang). Anyone else, including missing
 * membership, is treated as cabang (may pick Pusat only).
 */
export function resolveActorTransferSource(
  actorUnitId: string | null | undefined,
  actorIsAdmin = false,
): string {
  if (actorIsAdmin || isPusatUnitCode(actorUnitId)) {
    return CANONICAL_PUSAT_UNIT_CODE;
  }
  const code = (actorUnitId || "").trim();
  return code || "BRANCH";
}

/**
 * Destinations a caller may pick: Cabang → Pusat only; Pusat/Admin → cabang.
 * Intersected with Cabang ↔ Pusat XOR from the current handling unit.
 */
export function filterInternalTransferDestinations<T extends { code: string }>(
  branches: readonly T[],
  options: {
    actorUnitId?: string | null;
    handlingUnitId?: string | null;
    actorIsAdmin?: boolean;
  },
): T[] {
  const handling = (options.handlingUnitId || "").trim();
  if (!handling) return [];
  const byActor = filterTransferDestinations(
    branches,
    resolveActorTransferSource(options.actorUnitId, options.actorIsAdmin === true),
  );
  const byHandling = filterTransferDestinations(branches, handling);
  const allowed = new Set(
    byActor.map((row) => (row.code || "").trim().toUpperCase()),
  );
  return byHandling.filter((row) =>
    allowed.has((row.code || "").trim().toUpperCase()),
  );
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
