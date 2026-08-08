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

/**
 * Default void reason when the uploader removes a file in one click.
 * BR-012 / API-512 still require a non-empty audit reason; the UI no longer
 * prompts for it because only the uploader / complaint creator / admin may void.
 */
export const CM_BATCH1_VOID_REASON_UPLOADER_REMOVED = "removed_by_uploader";

/** BR-012 A3 — limited bulk upload per file-picker action. */
export const CM_BATCH1_MAX_MULTI_UPLOAD = 10;

/**
 * Collect files from an ``<input type="file" multiple>`` selection.
 * Caps at ``max`` (default {@link CM_BATCH1_MAX_MULTI_UPLOAD}).
 */
export function pickCmBatch1UploadFiles(
  list: FileList | null | undefined,
  max: number = CM_BATCH1_MAX_MULTI_UPLOAD,
): { files: File[]; truncated: boolean } {
  const all = list ? Array.from(list) : [];
  if (all.length === 0) return { files: [], truncated: false };
  if (all.length <= max) return { files: all, truncated: false };
  return { files: all.slice(0, Math.max(0, max)), truncated: true };
}

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

/** Resolve Batch-1 / platform ids from camelCase or snake_case payloads. */
export function cmBatch1AttachmentIds(item: {
  attachmentId?: string | null;
  platformAttachmentId?: string | null;
  attachment_id?: string | null;
  platform_attachment_id?: string | null;
}): { batchId: string; platformId: string } {
  const batchId = String(
    item.attachmentId ?? item.attachment_id ?? "",
  ).trim();
  const platformId = String(
    item.platformAttachmentId ?? item.platform_attachment_id ?? "",
  ).trim();
  return { batchId, platformId };
}

/** True when ``targetId`` matches the Batch-1 id or platform attachment id. */
export function isSameCmBatch1Attachment(
  item: {
    attachmentId?: string | null;
    platformAttachmentId?: string | null;
    attachment_id?: string | null;
    platform_attachment_id?: string | null;
  },
  targetId: string | null | undefined,
): boolean {
  const id = String(targetId ?? "").trim();
  if (!id) return false;
  const { batchId, platformId } = cmBatch1AttachmentIds(item);
  return id === batchId || id === platformId;
}

/** Prefer Batch-1 id for void; fall back to platform id (API-512 accepts both). */
export function cmBatch1VoidTargetId(item: {
  attachmentId?: string | null;
  platformAttachmentId?: string | null;
  attachment_id?: string | null;
  platform_attachment_id?: string | null;
}): string | null {
  const { batchId, platformId } = cmBatch1AttachmentIds(item);
  return batchId || platformId || null;
}

/** Normalize API payload (camelCase or snake_case) into the FE attachment shape. */
export function normalizeCmBatch1Attachment(
  raw: Record<string, unknown> | CmBatch1AttachmentLike,
): {
  attachmentId: string;
  platformAttachmentId: string;
  status: string;
  classification: string;
  stagingToken?: string | null;
  complaintId?: string | null;
  originalName: string;
  mimeType: string;
  sizeBytes: number;
  checksumSha256: string;
  supersedesId?: string | null;
  voidReason?: string | null;
  createdAt: string;
} {
  const r = raw as Record<string, unknown>;
  const { batchId, platformId } = cmBatch1AttachmentIds(
    raw as {
      attachmentId?: string | null;
      platformAttachmentId?: string | null;
      attachment_id?: string | null;
      platform_attachment_id?: string | null;
    },
  );
  return {
    attachmentId: batchId,
    platformAttachmentId: platformId,
    status: String(r.status ?? "STAGED"),
    classification: String(r.classification ?? ""),
    stagingToken: (r.stagingToken ?? r.staging_token ?? null) as string | null,
    complaintId: (r.complaintId ?? r.complaint_id ?? null) as string | null,
    originalName: String(r.originalName ?? r.original_name ?? ""),
    mimeType: String(r.mimeType ?? r.mime_type ?? ""),
    sizeBytes: Number(r.sizeBytes ?? r.size_bytes ?? 0),
    checksumSha256: String(r.checksumSha256 ?? r.checksum_sha256 ?? ""),
    supersedesId: (r.supersedesId ?? r.supersedes_id ?? null) as string | null,
    voidReason: (r.voidReason ?? r.void_reason ?? null) as string | null,
    createdAt: String(r.createdAt ?? r.created_at ?? ""),
  };
}

type CmBatch1AttachmentLike = {
  attachmentId?: string | null;
  platformAttachmentId?: string | null;
  attachment_id?: string | null;
  platform_attachment_id?: string | null;
  status?: string;
  classification?: string;
  stagingToken?: string | null;
  staging_token?: string | null;
  complaintId?: string | null;
  complaint_id?: string | null;
  originalName?: string;
  original_name?: string;
  mimeType?: string;
  mime_type?: string;
  sizeBytes?: number;
  size_bytes?: number;
  checksumSha256?: string;
  checksum_sha256?: string;
  supersedesId?: string | null;
  supersedes_id?: string | null;
  voidReason?: string | null;
  void_reason?: string | null;
  createdAt?: string;
  created_at?: string;
};

/**
 * Open a blank tab during the user gesture (before await).
 *
 * Do not pass ``noopener`` / ``noreferrer`` to ``window.open`` — those features
 * make the return value ``null`` even when the tab opened, which falsely
 * surfaces "popup blocked" while the file is visible.
 */
export function openBlankAttachmentTab(): Window | null {
  const opened = window.open("about:blank", "_blank");
  if (!opened) return null;
  try {
    opened.opener = null;
  } catch {
    /* ignore */
  }
  return opened;
}

/** Navigate a reserved preview tab to an object URL after the blob is ready. */
export function showAttachmentInTab(
  tab: Window,
  objectUrl: string,
): void {
  try {
    tab.location.replace(objectUrl);
  } catch {
    tab.location.href = objectUrl;
  }
}
