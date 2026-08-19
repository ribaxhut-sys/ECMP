/** Attachment preview classification helpers (TASK-032). */

const IMAGE_MIME = new Set([
  "image/jpeg",
  "image/jpg",
  "image/png",
  "image/gif",
  "image/webp",
]);

const IMAGE_EXT = new Set([".jpg", ".jpeg", ".png", ".gif", ".webp"]);
const PDF_EXT = new Set([".pdf"]);

/**
 * Only OOXML Word (.docx) can be rendered in-browser (docx-preview).
 * Legacy binary .doc has no client-side renderer — stays download-only.
 */
const DOCX_MIME = "application/vnd.openxmlformats-officedocument.wordprocessingml.document";
const DOCX_EXT = new Set([".docx"]);

export type PreviewKind = "image" | "pdf" | "docx" | "unsupported";

/** Internal complaint create/detail — images + ZIP only. */
export const INTERNAL_COMPLAINT_FILE_ACCEPT =
  "image/jpeg,image/png,image/gif,image/webp,application/zip,.jpg,.jpeg,.png,.gif,.webp,.zip";

const INTERNAL_ALLOWED_EXT = new Set([
  ".jpg",
  ".jpeg",
  ".png",
  ".gif",
  ".webp",
  ".zip",
]);
const INTERNAL_ALLOWED_MIME = new Set([
  "image/jpeg",
  "image/jpg",
  "image/png",
  "image/gif",
  "image/webp",
  "application/zip",
  "application/x-zip",
  "application/x-zip-compressed",
]);

export function isAllowedInternalComplaintFile(file: File): boolean {
  const name = file.name.trim().toLowerCase();
  const idx = name.lastIndexOf(".");
  const ext = idx > 0 ? name.slice(idx) : "";
  if (INTERNAL_ALLOWED_EXT.has(ext)) return true;
  return INTERNAL_ALLOWED_MIME.has((file.type || "").trim().toLowerCase());
}

export function normalizeExtension(extension: string | null | undefined, filename: string): string {
  const fromMeta = (extension ?? "").trim().toLowerCase();
  if (fromMeta) {
    return fromMeta.startsWith(".") ? fromMeta : `.${fromMeta}`;
  }
  const name = filename.trim().toLowerCase();
  const idx = name.lastIndexOf(".");
  if (idx <= 0) return "";
  return name.slice(idx);
}

export function getPreviewKind(
  mimeType: string,
  extension: string | null | undefined,
  filename: string,
): PreviewKind {
  const mime = (mimeType || "").trim().toLowerCase();
  const ext = normalizeExtension(extension, filename);

  if (mime === "application/pdf" || PDF_EXT.has(ext)) {
    return "pdf";
  }
  if (IMAGE_MIME.has(mime) || IMAGE_EXT.has(ext)) {
    return "image";
  }
  if (mime === DOCX_MIME || DOCX_EXT.has(ext)) {
    return "docx";
  }
  return "unsupported";
}

export function formatFileSize(bytes: number): string {
  if (!Number.isFinite(bytes) || bytes < 0) return "—";
  if (bytes < 1024) return `${bytes} B`;
  const kb = bytes / 1024;
  if (kb < 1024) return `${kb < 10 ? kb.toFixed(1) : Math.round(kb)} KB`;
  const mb = kb / 1024;
  return `${mb < 10 ? mb.toFixed(1) : Math.round(mb)} MB`;
}

export function formatUploadDate(
  value: string | null | undefined,
  locale: string,
): string {
  if (!value) return "—";
  try {
    return new Intl.DateTimeFormat(locale, {
      day: "2-digit",
      month: "short",
      year: "numeric",
      hour: "2-digit",
      minute: "2-digit",
      hour12: false,
    }).format(new Date(value));
  } catch {
    return value;
  }
}

export function fileTypeLabel(
  mimeType: string,
  extension: string | null | undefined,
  filename: string,
): string {
  const ext = normalizeExtension(extension, filename).replace(".", "").toUpperCase();
  if (ext) return ext;
  const mime = mimeType.trim();
  if (!mime) return "FILE";
  const subtype = mime.split("/")[1];
  return (subtype || mime).toUpperCase();
}
