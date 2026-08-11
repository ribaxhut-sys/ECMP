/**
 * `@[title](knowledge:<uuid>)` reference marker — Knowledge Reference on
 * Penyelesaian (Complaint Resolution). Mirrors the backend parser
 * (app/modules/resolutions/knowledge_markers.py) exactly; this module is
 * the Resolution feature's own interpretation of text it stores — the
 * Knowledge module itself is untouched.
 *
 * The `title` is a display snapshot only (stability, LOCKED — a reference
 * never re-resolves by title on read); `knowledgeId` is the sole
 * identifier used for validation and navigation.
 */

const MARKER_RE = /@\[([^\]\n]*)\]\(knowledge:([0-9a-fA-F-]{36})\)/g;

/** Trigger detection: an `@` immediately before the caret, not already
 * inside a marker, followed only by non-bracket/non-whitespace-run text. */
const TRIGGER_RE = /(?:^|[\s([])@([^\s@[\]()]{0,40})$/;

export type KnowledgeReferenceSegment =
  | { type: "text"; value: string }
  | { type: "reference"; knowledgeId: string; title: string };

/** Strip characters that would break the marker's own grammar. Cosmetic
 * only — never affects the referenced Knowledge, only the inline snapshot. */
function sanitizeTitleForMarker(title: string): string {
  return title.replace(/[[\]()]/g, "").replace(/\s+/g, " ").trim();
}

export function buildKnowledgeMarker(title: string, knowledgeId: string): string {
  return `@[${sanitizeTitleForMarker(title)}](knowledge:${knowledgeId})`;
}

/** Split text into alternating plain-text and reference segments for
 * read-mode rendering. Malformed markers are left as plain text. */
export function parseKnowledgeReferenceSegments(
  text: string,
): KnowledgeReferenceSegment[] {
  const segments: KnowledgeReferenceSegment[] = [];
  let lastIndex = 0;
  MARKER_RE.lastIndex = 0;
  let match: RegExpExecArray | null;
  while ((match = MARKER_RE.exec(text)) !== null) {
    if (match.index > lastIndex) {
      segments.push({ type: "text", value: text.slice(lastIndex, match.index) });
    }
    segments.push({ type: "reference", knowledgeId: match[2], title: match[1] });
    lastIndex = match.index + match[0].length;
  }
  if (lastIndex < text.length) {
    segments.push({ type: "text", value: text.slice(lastIndex) });
  }
  return segments;
}

/** Ordered, de-duplicated Knowledge ids referenced in `text`. */
export function extractKnowledgeIds(text: string): string[] {
  const ids: string[] = [];
  const seen = new Set<string>();
  for (const segment of parseKnowledgeReferenceSegments(text)) {
    if (segment.type === "reference" && !seen.has(segment.knowledgeId)) {
      seen.add(segment.knowledgeId);
      ids.push(segment.knowledgeId);
    }
  }
  return ids;
}

export interface MentionQuery {
  /** Index of the `@` character that starts the query. */
  start: number;
  query: string;
}

/** Detects an in-progress `@query` right before `caretIndex`, or null when
 * the caret isn't in mention-typing position (e.g. mid-marker, or `@`
 * followed by a space). */
export function detectMentionQuery(
  text: string,
  caretIndex: number,
): MentionQuery | null {
  const before = text.slice(0, caretIndex);
  const match = TRIGGER_RE.exec(before);
  if (!match) return null;
  const query = match[1] ?? "";
  const at = before.length - query.length - 1;
  return { start: at, query };
}

/** Replace the `@query` span (from `mention.start` to `caretIndex`) with the
 * inserted marker. A trailing space is added only when needed (end of text,
 * or the following character isn't already whitespace) so selecting a
 * reference mid-sentence never produces a double space. Returns the new
 * text and the caret position right after the inserted text. */
export function insertKnowledgeMarker(
  text: string,
  mention: MentionQuery,
  caretIndex: number,
  title: string,
  knowledgeId: string,
): { text: string; caret: number } {
  const marker = buildKnowledgeMarker(title, knowledgeId);
  const after = text.slice(caretIndex);
  const needsSpace = after.length === 0 || !/^\s/.test(after);
  const insertion = needsSpace ? `${marker} ` : marker;
  const next = text.slice(0, mention.start) + insertion + after;
  return { text: next, caret: mention.start + insertion.length };
}
