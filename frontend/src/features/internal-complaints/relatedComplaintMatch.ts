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

/** Advisory banner on create: empty, confirmed pick, or unmatched text. */
export type RelatedComplaintNoticeKind = "empty" | "linked" | "unresolved";

export function relatedComplaintNoticeKind(
  raw: string,
  matched: RelatedComplaintRef | null,
): RelatedComplaintNoticeKind | null {
  if (!raw.trim()) return "empty";
  if (matched) return "linked";
  if (!looksLikeRelatedComplaintQuery(raw)) return null;
  return "unresolved";
}

export type RelatedComplaintIssueKind =
  | "unresolved"
  | "not_found"
  | "closed"
  | "not_visible";

/** Block create unless the field is empty or a list pick — avoids opaque 404. */
export function relatedComplaintSubmitIssue(
  payload: RelatedComplaintPayload,
): RelatedComplaintIssueKind | null {
  if (payload.status === "unresolved") return "unresolved";
  if (payload.status === "literal") return "not_found";
  return null;
}

export function relatedComplaintIssueFromApiCode(
  code: string | undefined,
): RelatedComplaintIssueKind | null {
  if (code === "RELATED_COMPLAINT_NOT_FOUND" || code === "NOT_FOUND") {
    return "not_found";
  }
  if (code === "RELATED_COMPLAINT_CLOSED") return "closed";
  if (code === "RELATED_COMPLAINT_NOT_VISIBLE") return "not_visible";
  return null;
}

export function relatedComplaintIssueCopyKeys(
  kind: RelatedComplaintIssueKind,
): {
  title: string;
  lead: string;
  why: string;
  how: string;
} {
  if (kind === "closed") {
    return {
      title: "relatedComplaintIssueClosedTitle",
      lead: "relatedComplaintIssueClosedLead",
      why: "relatedComplaintIssueClosedWhy",
      how: "relatedComplaintIssueClosedHow",
    };
  }
  if (kind === "not_visible") {
    return {
      title: "relatedComplaintIssueNotVisibleTitle",
      lead: "relatedComplaintIssueNotVisibleLead",
      why: "relatedComplaintIssueNotVisibleWhy",
      how: "relatedComplaintIssueNotVisibleHow",
    };
  }
  if (kind === "not_found") {
    return {
      title: "relatedComplaintIssueNotFoundTitle",
      lead: "relatedComplaintIssueNotFoundLead",
      why: "relatedComplaintIssueNotFoundWhy",
      how: "relatedComplaintIssueNotFoundHow",
    };
  }
  return {
    title: "relatedComplaintIssueUnresolvedTitle",
    lead: "relatedComplaintIssueUnresolvedLead",
    why: "relatedComplaintIssueUnresolvedWhy",
    how: "relatedComplaintIssueUnresolvedHow",
  };
}
