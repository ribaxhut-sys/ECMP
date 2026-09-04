/**
 * The Announcement model only stores a title + full body (no separate short
 * "ringkasan" field — see the Pengelolaan Pengumuman create form). The
 * landing card needs a short summary line, so derive one by truncating the
 * body at a word boundary instead of adding a field the backend never asked
 * for.
 */
export function summarize(body: string, maxLength = 160): string {
  const trimmed = body.trim().replace(/\s+/g, " ");
  if (trimmed.length <= maxLength) return trimmed;
  const cut = trimmed.slice(0, maxLength);
  const lastSpace = cut.lastIndexOf(" ");
  const safe = lastSpace > 0 ? cut.slice(0, lastSpace) : cut;
  return `${safe}…`;
}
