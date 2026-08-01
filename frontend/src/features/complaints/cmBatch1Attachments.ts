/**
 * Pure helpers for Batch-1 FR-004 attachment UI (SCR-CM-004 / confirmation).
 * Kept free of React/Axios so FE-CI-POL coverage gates can include this file.
 */

import type { CmBatch1AttachmentStatus } from "@/lib/api/cmBatch1";

/** Statuses that may be logically voided (not physical delete). */
const VOIDABLE: ReadonlySet<CmBatch1AttachmentStatus> = new Set([
  "STAGED",
  "ACTIVE",
  "TRANSFERRED",
]);

export function isCmBatch1AttachmentVoidable(
  status: CmBatch1AttachmentStatus | string,
): boolean {
  return VOIDABLE.has(status as CmBatch1AttachmentStatus);
}

/**
 * Normalize void reason (API-512 / BR-012 void-with-reason).
 * Returns null when empty after trim.
 */
export function normalizeCmBatch1VoidReason(
  reason: string | null | undefined,
): string | null {
  const trimmed = (reason ?? "").trim();
  return trimmed.length > 0 ? trimmed : null;
}

export function formatCmBatch1AttachmentBytes(size: number): string {
  if (!Number.isFinite(size) || size < 0) return "—";
  if (size < 1024) return `${Math.round(size)} B`;
  if (size < 1024 * 1024) return `${(size / 1024).toFixed(1)} KB`;
  return `${(size / (1024 * 1024)).toFixed(1)} MB`;
}

export function cmBatch1AttachmentListLabel(
  count: number,
  options?: { voidedHidden?: boolean },
): string {
  const voidedHidden = options?.voidedHidden ?? true;
  if (count <= 0) {
    return voidedHidden
      ? "attachmentCountNone"
      : "noItems";
  }
  return count === 1 ? "attachmentCountOne" : "attachmentCountMany";
}
