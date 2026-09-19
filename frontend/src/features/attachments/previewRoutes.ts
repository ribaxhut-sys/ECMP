/**
 * In-app preview URL for one attachment.
 *
 * "Open in new tab" used to hand the tab a `blob:` URL. Browsers only render
 * types they have a built-in viewer for (images, PDF, text), so Word/Excel/ZIP
 * blobs turned straight into downloads — and the URL died on revoke, so the
 * tab could not be refreshed or shared. A real route fixes all three.
 */
export function attachmentPreviewPath(attachmentId: string): string {
  return `/attachments/${encodeURIComponent(attachmentId)}/preview`;
}
