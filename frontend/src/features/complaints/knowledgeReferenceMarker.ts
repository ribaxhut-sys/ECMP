/**
 * `@[title](<kind>:<uuid>)` reference marker — inline `@` mentions on
 * Catatan (Batch-1 intake note) and Penyelesaian (Complaint Resolution).
 * Mirrors the backend parser (app/modules/resolutions/knowledge_markers.py,
 * `knowledge` kind only — see note below) exactly for that one kind; this
 * module is the Resolution/Intake feature's own interpretation of text it
 * stores — the Knowledge/Announcement/Attachment modules themselves are
 * untouched.
 *
 * Three mention kinds share this one grammar:
 *   - `knowledge`    — Pengetahuan (SOP/Peraturan/…)
 *   - `announcement` — Pengumuman aktif
 *   - `attachment`   — Lampiran PUBLIC (announcement attachment catalog)
 *
 * The `title` is a display snapshot only (stability, LOCKED — a reference
 * never re-resolves by title on read); `id` is the sole identifier used
 * for validation and navigation.
 */

export type MentionKind = "knowledge" | "announcement" | "attachment";

/** Catalog order for the `@` empty-query source picker. */
export const MENTION_KINDS: readonly MentionKind[] = [
  "knowledge",
  "announcement",
  "attachment",
] as const;

const MARKER_RE =
  /@\[([^\]\n]*)\]\((knowledge|announcement|attachment):([0-9a-fA-F-]{36})\)/g;

/** Trigger detection: an `@` immediately before the caret, not already
 * inside a marker, followed only by non-bracket/non-whitespace-run text. */
const TRIGGER_RE = /(?:^|[\s([])@([^\s@[\]()]{0,40})$/;

export type KnowledgeReferenceSegment =
  | { type: "text"; value: string }
  | { type: "reference"; kind: MentionKind; id: string; title: string };

/** Strip characters that would break the marker's own grammar. Cosmetic
 * only — never affects the referenced record, only the inline snapshot. */
function sanitizeTitleForMarker(title: string): string {
  return title.replace(/[[\]()]/g, "").replace(/\s+/g, " ").trim();
}

export function buildMentionMarker(
  kind: MentionKind,
  title: string,
  id: string,
): string {
  return `@[${sanitizeTitleForMarker(title)}](${kind}:${id})`;
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
    segments.push({
      type: "reference",
      kind: match[2] as MentionKind,
      id: match[3],
      title: match[1],
    });
    lastIndex = match.index + match[0].length;
  }
  if (lastIndex < text.length) {
    segments.push({ type: "text", value: text.slice(lastIndex) });
  }
  return segments;
}

/** Ordered, de-duplicated (by kind+id) references in `text`. */
export function extractMentionRefs(
  text: string,
): { kind: MentionKind; id: string }[] {
  const refs: { kind: MentionKind; id: string }[] = [];
  const seen = new Set<string>();
  for (const segment of parseKnowledgeReferenceSegments(text)) {
    if (segment.type !== "reference") continue;
    const key = `${segment.kind}:${segment.id}`;
    if (seen.has(key)) continue;
    seen.add(key);
    refs.push({ kind: segment.kind, id: segment.id });
  }
  return refs;
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
export function insertMentionMarker(
  text: string,
  mention: MentionQuery,
  caretIndex: number,
  kind: MentionKind,
  title: string,
  id: string,
): { text: string; caret: number } {
  const marker = buildMentionMarker(kind, title, id);
  const after = text.slice(caretIndex);
  const needsSpace = after.length === 0 || !/^\s/.test(after);
  const insertion = needsSpace ? `${marker} ` : marker;
  const next = text.slice(0, mention.start) + insertion + after;
  return { text: next, caret: mention.start + insertion.length };
}
