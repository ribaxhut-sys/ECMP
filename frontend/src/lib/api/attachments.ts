import { apiRequest, apiRequestBlob } from "./client";
import type {
  Attachment,
  AttachmentAggregateType,
  DataResponse,
  ListResponse,
} from "./types";

/** API-386 — GET /api/v1/attachments?aggregateType=&aggregateId= */
export function fetchAttachments(
  aggregateType: AttachmentAggregateType,
  aggregateId: string,
  pageSize = 50,
): Promise<ListResponse<Attachment>> {
  const params = new URLSearchParams({
    aggregateType,
    aggregateId,
    pageSize: String(pageSize),
  });
  return apiRequest<ListResponse<Attachment>>(
    `/api/v1/attachments?${params.toString()}`,
  );
}

/** API-324 — GET /api/v1/attachments/{id} (metadata only; no file bytes). */
export function fetchAttachment(
  attachmentId: string,
): Promise<DataResponse<Attachment>> {
  return apiRequest<DataResponse<Attachment>>(
    `/api/v1/attachments/${encodeURIComponent(attachmentId)}`,
  );
}

/** API-323 — POST /api/v1/attachments (multipart). */
export function uploadAttachment(
  aggregateType: AttachmentAggregateType,
  aggregateId: string,
  file: File,
): Promise<DataResponse<Attachment>> {
  const form = new FormData();
  form.append("aggregateType", aggregateType);
  form.append("aggregateId", aggregateId);
  form.append("file", file);
  return apiRequest<DataResponse<Attachment>>("/api/v1/attachments", {
    method: "POST",
    body: form,
  });
}

export interface AttachmentDownloadResult {
  blob: Blob;
  filename: string | null;
  mimeType: string;
  checksum: string | null;
}

/**
 * API-325 — GET /api/v1/attachments/{id}/download
 * Call only when the user opens Preview / Download / Open in new tab.
 */
export async function downloadAttachment(
  attachmentId: string,
): Promise<AttachmentDownloadResult> {
  const result = await apiRequestBlob(
    `/api/v1/attachments/${encodeURIComponent(attachmentId)}/download`,
  );

  let filename: string | null = null;
  if (result.contentDisposition) {
    const utfMatch = /filename\*=UTF-8''([^;]+)/i.exec(result.contentDisposition);
    const plainMatch = /filename="([^"]+)"/i.exec(result.contentDisposition);
    const raw = utfMatch?.[1] ?? plainMatch?.[1];
    if (raw) {
      try {
        filename = decodeURIComponent(raw);
      } catch {
        filename = raw;
      }
    }
  }

  return {
    blob: result.blob,
    filename,
    mimeType:
      result.contentType || result.blob.type || "application/octet-stream",
    checksum: result.checksumSha256,
  };
}
