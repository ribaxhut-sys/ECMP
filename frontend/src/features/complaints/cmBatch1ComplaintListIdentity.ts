import { isCmBatch1PusatUnitCode } from "./cmBatch1HqActions";

/**
 * Cabang operators read the list by complaint number; Pusat keeps Case-first
 * (DEC-026 row identity unchanged — only presentation).
 *
 * ``null`` / ``undefined`` / empty → not cabang (Admin Pusat, loading, unknown).
 */
export function prefersComplaintNumberIdentity(
  orgUnitCode: string | null | undefined,
): boolean {
  if (orgUnitCode == null) return false;
  const code = orgUnitCode.trim();
  if (!code) return false;
  return !isCmBatch1PusatUnitCode(code);
}

/**
 * Whether the signed-in unit uses the Pusat Pengaduan / Tindak lanjut split.
 * ``null`` while the org unit is still loading — callers must not assume Cabang.
 */
export function isPusatWorkAudience(
  orgUnitCode: string | null | undefined,
): boolean | null {
  if (orgUnitCode === undefined) return null;
  return !prefersComplaintNumberIdentity(orgUnitCode);
}
