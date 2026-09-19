/**
 * Gate for Pengaduan Internal UI (Cabang ↔ Pusat).
 *
 * Default OFF. Enable for lab/deploy:
 *   NEXT_PUBLIC_ECMP_INTERNAL_COMPLAINTS_UI=true
 *
 * Backend module lives under `/api/v1/internal/complaints` (domain terpisah
 * dari F4). Flag only controls FE nav/routes visibility.
 */
export function isInternalComplaintsUiEnabled(): boolean {
  return process.env.NEXT_PUBLIC_ECMP_INTERNAL_COMPLAINTS_UI === "true";
}
