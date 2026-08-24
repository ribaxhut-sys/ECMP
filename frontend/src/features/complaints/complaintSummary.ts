/**
 * Complaint-card summary of the WP narrative.
 * Full Case description + notes stay on the Case page.
 */

export const COMPLAINT_SUMMARY_MAX_CHARS = 280;

export function summarizeComplaintNarrative(
  text: string,
  maxChars: number = COMPLAINT_SUMMARY_MAX_CHARS,
): { text: string; truncated: boolean } {
  const trimmed = text.trim();
  if (!trimmed) return { text: "", truncated: false };
  if (trimmed.length <= maxChars) return { text: trimmed, truncated: false };
  const slice = trimmed.slice(0, maxChars);
  const lastSpace = slice.lastIndexOf(" ");
  const cut =
    lastSpace > Math.floor(maxChars * 0.6) ? slice.slice(0, lastSpace) : slice;
  return { text: `${cut.trimEnd()}…`, truncated: true };
}
