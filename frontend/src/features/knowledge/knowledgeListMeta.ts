/**
 * Pure helpers for the dense Knowledge catalog list meta line.
 */

import type { Knowledge, KnowledgeFile, KnowledgeStatus } from "@/lib/api/types";
import { fileTypeLabel } from "@/features/attachments/fileTypes";

export function knowledgeStatusLabelKey(
  status: KnowledgeStatus,
): "statusActive" | "statusArchived" | "statusDraft" {
  if (status === "ACTIVE") return "statusActive";
  if (status === "ARCHIVED") return "statusArchived";
  return "statusDraft";
}

/** Compact status cue — one scan column like GitHub Actions run list. */
export function knowledgeStatusDotClass(status: KnowledgeStatus): string {
  if (status === "ACTIVE") return "bg-ecmp-success";
  if (status === "DRAFT") return "bg-ecmp-warning";
  return "bg-ecmp-text-secondary";
}

export function isKnowledgeListInactive(
  row: Pick<Knowledge, "status" | "effectiveTo">,
  now: Date = new Date(),
): boolean {
  if (row.status === "ARCHIVED") return true;
  const to = row.effectiveTo?.trim();
  if (!to) return false;
  const end = new Date(to);
  return !Number.isNaN(end.getTime()) && end.getTime() < now.getTime();
}

/** Prefer PRIMARY for display; otherwise first file in API order. */
export function pickKnowledgeDisplayFile(
  files: readonly KnowledgeFile[] | null | undefined,
): KnowledgeFile | null {
  if (!files || files.length === 0) return null;
  return files.find((f) => f.role === "PRIMARY") ?? files[0] ?? null;
}

/** Newest upload (`createdAt`) first — stable for catalog paging. */
export function sortKnowledgeByUploadedAtDesc<T extends Pick<Knowledge, "createdAt" | "id">>(
  rows: readonly T[],
): T[] {
  return [...rows].sort((a, b) => {
    const aTime = Date.parse(a.createdAt);
    const bTime = Date.parse(b.createdAt);
    const aOk = Number.isFinite(aTime);
    const bOk = Number.isFinite(bTime);
    if (aOk && bOk && aTime !== bTime) return bTime - aTime;
    if (aOk !== bOk) return aOk ? -1 : 1;
    return a.id < b.id ? 1 : a.id > b.id ? -1 : 0;
  });
}

export type KnowledgeListMetaLabels = {
  status: string;
  effective: (date: string) => string;
  uploaded: (date: string) => string;
  inactive: (date: string) => string;
  /** Berapa berkas yang menempel — hanya dipakai saat lebih dari satu. */
  files: (count: number) => string;
  emDash: string;
};

/**
 * Single-line meta segments: doc · version · status · berlaku · unggah · [type] ·
 * [n berkas] · [nonaktif]. The file-count segment appears only when a record
 * carries more than one document — a single file is already implied by the
 * type label next to it.
 */
export function buildKnowledgeListMeta(
  row: Pick<
    Knowledge,
    | "documentNumber"
    | "versionLabel"
    | "status"
    | "effectiveFrom"
    | "effectiveTo"
    | "createdAt"
    | "updatedAt"
    | "files"
  >,
  labels: KnowledgeListMetaLabels,
  formatShortDate: (value: string | null | undefined) => string,
  now: Date = new Date(),
): string {
  const parts: string[] = [];
  const doc = row.documentNumber?.trim();
  if (doc) parts.push(doc);
  const version = row.versionLabel?.trim();
  if (version) parts.push(`v${version}`);
  parts.push(labels.status);

  const effective = formatShortDate(row.effectiveFrom) || labels.emDash;
  parts.push(labels.effective(effective));

  const uploaded = formatShortDate(row.createdAt) || labels.emDash;
  parts.push(labels.uploaded(uploaded));

  const displayFile = pickKnowledgeDisplayFile(row.files);
  if (displayFile) {
    parts.push(fileTypeLabel(displayFile.mimeType, null, displayFile.fileName));
  }

  const fileCount = row.files?.length ?? 0;
  if (fileCount > 1) {
    parts.push(labels.files(fileCount));
  }

  if (isKnowledgeListInactive(row, now)) {
    const inactiveRaw =
      row.effectiveTo?.trim() ||
      (row.status === "ARCHIVED" ? row.updatedAt : null);
    const inactive = formatShortDate(inactiveRaw);
    if (inactive) parts.push(labels.inactive(inactive));
  }

  return parts.join(" · ");
}
