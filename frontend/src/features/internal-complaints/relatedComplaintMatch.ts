/** Match typed related WP complaint input to list rows (create form). */

export type RelatedComplaintRef = {
  id: string;
  number: string;
  subject: string | null;
  createdAt: string | null;
  createdByName: string | null;
};

export type RelatedComplaintPayload =
  | { status: "empty"; id: null }
  | { status: "matched"; id: string }
  | { status: "literal"; id: string }
  | { status: "unresolved" };

const UUID_RE =
  /^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$/i;
const WP_NUMBER_RE = /^CM[-/]/i;

export function relatedComplaintFromListRow(row: {
  complaintId?: string | null;
  complaintNumber?: string | null;
  subject?: string | null;
  createdAt?: string | null;
  createdByName?: string | null;
}): RelatedComplaintRef | null {
  const id = (row.complaintId || "").trim();
  const number = (row.complaintNumber || "").trim();
  if (!id || !number) return null;
  return {
    id,
    number,
    subject: row.subject?.trim() || null,
    createdAt: row.createdAt?.trim() || null,
    createdByName: row.createdByName?.trim() || null,
  };
}

function uniqueMatch(
  rows: readonly RelatedComplaintRef[],
  predicate: (row: RelatedComplaintRef) => boolean,
): RelatedComplaintRef | null {
  const hits = rows.filter(predicate);
  return hits.length === 1 ? hits[0] : null;
}

export function matchRelatedComplaint(
  raw: string,
  rows: readonly RelatedComplaintRef[],
): RelatedComplaintRef | null {
  const value = raw.trim();
  if (!value) return null;
  const upper = value.toUpperCase();
  const exact =
    rows.find(
      (row) => row.number.toUpperCase() === upper || row.id === value,
    ) ?? null;
  if (exact) return exact;

  const bySubject = uniqueMatch(
    rows,
    (row) => (row.subject || "").toUpperCase() === upper,
  );
  if (bySubject) return bySubject;

  const byName = uniqueMatch(
    rows,
    (row) => (row.createdByName || "").toUpperCase() === upper,
  );
  if (byName) return byName;

  if (value.length < 2) return null;
  return uniqueMatch(
    rows,
    (row) =>
      row.number.toUpperCase().includes(upper) ||
      (row.subject || "").toUpperCase().includes(upper) ||
      (row.createdByName || "").toUpperCase().includes(upper),
  );
}

/** UUID or WP number (CM-…) — may be sent to the server even if not in the list. */
export function looksLikeRelatedComplaintRef(raw: string): boolean {
  const value = raw.trim();
  return UUID_RE.test(value) || WP_NUMBER_RE.test(value);
}

export function resolveRelatedComplaintPayload(
  raw: string,
  rows: readonly RelatedComplaintRef[],
): RelatedComplaintPayload {
  const value = raw.trim();
  if (!value) return { status: "empty", id: null };
  const hit = matchRelatedComplaint(value, rows);
  if (hit) return { status: "matched", id: hit.id };
  if (looksLikeRelatedComplaintRef(value)) {
    return { status: "literal", id: value };
  }
  return { status: "unresolved" };
}

/** True when the field looks complete enough to search by keyword. */
export function looksLikeRelatedComplaintQuery(raw: string): boolean {
  return raw.trim().length >= 2;
}

export function mergeRelatedComplaintRefs(
  current: readonly RelatedComplaintRef[],
  incoming: readonly RelatedComplaintRef[],
): RelatedComplaintRef[] {
  const byId = new Map<string, RelatedComplaintRef>();
  for (const row of current) byId.set(row.id, row);
  for (const row of incoming) byId.set(row.id, row);
  return [...byId.values()];
}
