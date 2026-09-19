import type { Attachment } from "@/lib/api";

function str(value: unknown): string | null {
  return typeof value === "string" && value.trim() ? value : null;
}

/**
 * GET /api/v1/attachments/{id} answers with one of two shapes: the platform
 * Attachment, or the Batch 1 orchestration record (`attachmentId` /
 * `platformAttachmentId` / `createdAt`, no `extension`). The preview page reads
 * both, so a Batch 1 evidence file opens in a tab like any other attachment.
 *
 * Returns null when the payload carries neither an id nor a file name.
 */
export function normalizeAttachmentMeta(raw: unknown): Attachment | null {
  if (!raw || typeof raw !== "object") return null;
  const r = raw as Record<string, unknown>;

  const id = str(r.id) ?? str(r.platformAttachmentId) ?? str(r.attachmentId);
  const originalName = str(r.originalName) ?? str(r.fileName);
  if (!id || !originalName) return null;

  return {
    id,
    aggregateType: (str(r.aggregateType) ??
      "Complaint") as Attachment["aggregateType"],
    aggregateId: str(r.aggregateId) ?? str(r.complaintId) ?? "",
    fileName: str(r.fileName) ?? originalName,
    originalName,
    mimeType: str(r.mimeType) ?? "",
    extension: str(r.extension),
    sizeBytes: typeof r.sizeBytes === "number" ? r.sizeBytes : 0,
    checksumSha256: str(r.checksumSha256) ?? "",
    storageProvider: str(r.storageProvider) ?? "",
    uploadedBy: str(r.uploadedBy),
    uploadedAt: str(r.uploadedAt) ?? str(r.createdAt) ?? "",
    status: (str(r.status) ?? "AVAILABLE") as Attachment["status"],
  };
}
