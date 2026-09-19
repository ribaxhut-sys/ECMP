import type { Announcement, AnnouncementAttachment, Attachment } from "@/lib/api/types";

/**
 * Adapts the lightweight AnnouncementAttachment (embedded in the Announcement
 * response) into the shape the existing generic attachment UI
 * (AttachmentCard / AttachmentViewer) already expects — reuses that
 * preview/download infrastructure instead of building a new one (§13/§15).
 * Fields unused by that UI (storageProvider, checksumSha256, uploadedBy,
 * status) get harmless placeholders; extension is left null so the existing
 * fileTypes helpers fall back to parsing it from the filename.
 */
export function toAttachmentCardModel(
  attachment: AnnouncementAttachment,
  announcement: Pick<Announcement, "id">,
): Attachment {
  return {
    id: attachment.id,
    aggregateType: "Announcement",
    aggregateId: announcement.id,
    fileName: attachment.fileName,
    originalName: attachment.fileName,
    mimeType: attachment.mimeType,
    extension: null,
    sizeBytes: attachment.sizeBytes,
    storageProvider: "local",
    checksumSha256: "",
    uploadedBy: null,
    uploadedAt: attachment.createdAt,
    status: "AVAILABLE",
  };
}
