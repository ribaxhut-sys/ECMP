import { apiRequest } from "./client";
import type {
  Announcement,
  AnnouncementAttachment,
  AnnouncementAttachmentLibraryItem,
  AnnouncementAttachmentLinkRequest,
  AnnouncementAttachmentAccessUpdateRequest,
  AnnouncementAttachmentVisibility,
  AnnouncementCreateRequest,
  AnnouncementPublishRequest,
  AnnouncementUpdateRequest,
  DataResponse,
} from "./types";

/** Management list — all statuses. Requires announcement:manage. */
export function fetchAnnouncements(): Promise<DataResponse<Announcement[]>> {
  return apiRequest<DataResponse<Announcement[]>>("/api/v1/announcements");
}

/** Detail — attachments are visibility-filtered unless the caller is one of
 * the 3 manage roles (Admin/Supervisor/Manager Pusat). */
export function fetchAnnouncement(
  id: string,
): Promise<DataResponse<Announcement>> {
  return apiRequest<DataResponse<Announcement>>(
    `/api/v1/announcements/${encodeURIComponent(id)}`,
  );
}

/**
 * Landing page list — PUBLISHED, in-window. Global for every
 * announcement:read holder — announcements have no audience/target
 * (business decision, LOCKED).
 */
export function fetchActiveAnnouncements(): Promise<DataResponse<Announcement[]>> {
  return apiRequest<DataResponse<Announcement[]>>("/api/v1/announcements/active");
}

/**
 * Reader archive — PUBLISHED (incl. EXPIRED) + ARCHIVED, global.
 * Same announcement:read gate as fetchActiveAnnouncements. DRAFT and
 * SCHEDULED (future startAt) are excluded; expired stays visible.
 */
export function fetchAnnouncementHistory(): Promise<DataResponse<Announcement[]>> {
  return apiRequest<DataResponse<Announcement[]>>("/api/v1/announcements/history");
}

/**
 * Post-login entry-point gate (§17, LOCKED) — a single EXISTS-shaped boolean,
 * never the full /active list. Same announcement:read gate as
 * fetchActiveAnnouncements.
 */
export function fetchHasUnreadAnnouncements(): Promise<DataResponse<boolean>> {
  return apiRequest<DataResponse<boolean>>("/api/v1/announcements/unread");
}

/**
 * Mark an announcement as read by the caller — idempotent. Call only when
 * the reader opens the detail view (§4, LOCKED); never from the list.
 */
export function markAnnouncementRead(id: string): Promise<void> {
  return apiRequest<void>(
    `/api/v1/announcements/${encodeURIComponent(id)}/read`,
    { method: "PUT" },
  );
}

export function createAnnouncement(
  body: AnnouncementCreateRequest,
): Promise<DataResponse<Announcement>> {
  return apiRequest<DataResponse<Announcement>>("/api/v1/announcements", {
    method: "POST",
    body: JSON.stringify(body),
  });
}

export function updateAnnouncement(
  id: string,
  body: AnnouncementUpdateRequest,
): Promise<DataResponse<Announcement>> {
  return apiRequest<DataResponse<Announcement>>(
    `/api/v1/announcements/${encodeURIComponent(id)}`,
    { method: "PUT", body: JSON.stringify(body) },
  );
}

export function publishAnnouncement(
  id: string,
  body?: AnnouncementPublishRequest | null,
): Promise<DataResponse<Announcement>> {
  return apiRequest<DataResponse<Announcement>>(
    `/api/v1/announcements/${encodeURIComponent(id)}/publish`,
    {
      method: "PUT",
      ...(body != null ? { body: JSON.stringify(body) } : {}),
    },
  );
}

export function unpublishAnnouncement(
  id: string,
): Promise<DataResponse<Announcement>> {
  return apiRequest<DataResponse<Announcement>>(
    `/api/v1/announcements/${encodeURIComponent(id)}/unpublish`,
    { method: "PUT" },
  );
}

export function deleteAnnouncement(id: string): Promise<void> {
  return apiRequest<void>(`/api/v1/announcements/${encodeURIComponent(id)}`, {
    method: "DELETE",
  });
}

// --- Attachments — manage-only mutations (require_announcement_manage) ---

/** Multipart upload onto an announcement. Default visibility (server-side)
 * is PUBLISHED — the safest choice — when omitted. */
export function uploadAnnouncementAttachment(
  announcementId: string,
  file: File,
  visibility: AnnouncementAttachmentVisibility,
): Promise<DataResponse<AnnouncementAttachment>> {
  const form = new FormData();
  form.append("file", file);
  form.append("visibility", visibility);
  return apiRequest<DataResponse<AnnouncementAttachment>>(
    `/api/v1/announcements/${encodeURIComponent(announcementId)}/attachments`,
    { method: "POST", body: form },
  );
}

export function uploadAnnouncementAttachmentToCatalog(
  file: File,
  accessLevel: "PUBLIC" | "PRIVATE" = "PRIVATE",
): Promise<DataResponse<AnnouncementAttachmentLibraryItem>> {
  const form = new FormData();
  form.append("file", file);
  form.append("accessLevel", accessLevel);
  return apiRequest<DataResponse<AnnouncementAttachmentLibraryItem>>(
    `/api/v1/announcements/attachment-library`,
    { method: "POST", body: form },
  );
}

export function fetchAnnouncementAttachmentLibrary(opts?: {
  q?: string;
  excludeAnnouncementId?: string;
  orgScope?: "all" | "pusat" | "cabang";
}): Promise<DataResponse<AnnouncementAttachmentLibraryItem[]>> {
  const params = new URLSearchParams();
  if (opts?.q?.trim()) params.set("q", opts.q.trim());
  if (opts?.excludeAnnouncementId) {
    params.set("excludeAnnouncementId", opts.excludeAnnouncementId);
  }
  if (opts?.orgScope && opts.orgScope !== "all") {
    params.set("orgScope", opts.orgScope);
  }
  const query = params.toString();
  return apiRequest<DataResponse<AnnouncementAttachmentLibraryItem[]>>(
    `/api/v1/announcements/attachment-library${query ? `?${query}` : ""}`,
  );
}

export function updateAnnouncementAttachmentAccess(
  attachmentId: string,
  body: AnnouncementAttachmentAccessUpdateRequest,
): Promise<DataResponse<AnnouncementAttachmentLibraryItem>> {
  return apiRequest<DataResponse<AnnouncementAttachmentLibraryItem>>(
    `/api/v1/announcements/attachment-library/${encodeURIComponent(attachmentId)}/access`,
    { method: "PUT", body: JSON.stringify(body) },
  );
}

export function deleteAnnouncementAttachmentFromCatalog(
  attachmentId: string,
): Promise<void> {
  return apiRequest<void>(
    `/api/v1/announcements/attachment-library/${encodeURIComponent(attachmentId)}`,
    { method: "DELETE" },
  );
}

export function linkAnnouncementAttachment(
  announcementId: string,
  body: AnnouncementAttachmentLinkRequest,
): Promise<DataResponse<AnnouncementAttachment>> {
  return apiRequest<DataResponse<AnnouncementAttachment>>(
    `/api/v1/announcements/${encodeURIComponent(announcementId)}/attachments/link`,
    { method: "POST", body: JSON.stringify(body) },
  );
}

export function updateAnnouncementAttachmentVisibility(
  announcementId: string,
  attachmentId: string,
  visibility: AnnouncementAttachmentVisibility,
): Promise<DataResponse<AnnouncementAttachment>> {
  return apiRequest<DataResponse<AnnouncementAttachment>>(
    `/api/v1/announcements/${encodeURIComponent(announcementId)}/attachments/${encodeURIComponent(attachmentId)}`,
    { method: "PUT", body: JSON.stringify({ visibility }) },
  );
}

export function removeAnnouncementAttachment(
  announcementId: string,
  attachmentId: string,
): Promise<void> {
  return apiRequest<void>(
    `/api/v1/announcements/${encodeURIComponent(announcementId)}/attachments/${encodeURIComponent(attachmentId)}`,
    { method: "DELETE" },
  );
}
