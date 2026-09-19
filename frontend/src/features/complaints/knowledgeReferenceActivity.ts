import { fetchAnnouncement, fetchAttachment, fetchKnowledge } from "@/lib/api";
import type { Announcement, Attachment, Knowledge, KnowledgeStatus, KnowledgeType } from "@/lib/api/types";
import type { MentionKind } from "./knowledgeReferenceMarker";

/** ACTIVE + within effective window — same idea as backend `within_effective_window`. */
export function isKnowledgeReferenceActive(
  knowledge: Pick<Knowledge, "status" | "effectiveFrom" | "effectiveTo">,
  now: Date = new Date(),
): boolean {
  if (knowledge.status !== "ACTIVE") return false;
  if (knowledge.effectiveFrom) {
    const from = new Date(knowledge.effectiveFrom);
    if (!Number.isNaN(from.getTime()) && from > now) return false;
  }
  if (knowledge.effectiveTo) {
    const to = new Date(knowledge.effectiveTo);
    if (!Number.isNaN(to.getTime()) && to < now) return false;
  }
  return true;
}

/** Same window the `@` picker offers (fetchActiveAnnouncements) — PUBLISHED
 * effective status. An announcement that expired/was unpublished after the
 * mention was inserted reads as inactive, same as an archived Knowledge. */
export function isAnnouncementReferenceActive(
  announcement: Pick<Announcement, "effectiveStatus">,
): boolean {
  return announcement.effectiveStatus === "PUBLISHED";
}

/** Soft-deleted catalog files stay fetchable (status flips to DELETED)
 * instead of 404ing — check status explicitly, same idea as Knowledge. */
export function isAttachmentReferenceActive(
  attachment: Pick<Attachment, "status">,
): boolean {
  return attachment.status === "AVAILABLE";
}

export type KnowledgeReferenceMeta = {
  active: boolean;
  knowledgeType?: KnowledgeType;
  status?: KnowledgeStatus;
};

export type MentionReferenceMeta = {
  active: boolean;
  /** Pre-resolved badge text (Knowledge sub-type, or a fixed "Pengumuman"/"Lampiran" label). */
  typeLabel: string;
};

/**
 * Single source of truth for "is this @ mention still valid" — used both at
 * write-time (KnowledgeMentionTextarea recolors a stale chip red while
 * editing) and read-time (KnowledgeReferenceText). A rejected promise
 * (404/403/network) is left for the caller to turn into `active: false`,
 * matching the existing Knowledge chip pattern.
 */
export async function resolveMentionReferenceMeta(
  kind: MentionKind,
  id: string,
  labels: {
    knowledgeType: (type: KnowledgeType) => string;
    announcement: string;
    attachment: string;
  },
): Promise<MentionReferenceMeta> {
  if (kind === "knowledge") {
    const res = await fetchKnowledge(id);
    return {
      active: isKnowledgeReferenceActive(res.data),
      typeLabel: labels.knowledgeType(res.data.knowledgeType),
    };
  }
  if (kind === "announcement") {
    const res = await fetchAnnouncement(id);
    return {
      active: isAnnouncementReferenceActive(res.data),
      typeLabel: labels.announcement,
    };
  }
  const res = await fetchAttachment(id);
  return {
    active: isAttachmentReferenceActive(res.data),
    typeLabel: labels.attachment,
  };
}
