/**
 * Mock Enterprise Directory (UX-CU-003 §5.1 — development / end-to-end only).
 *
 * Enterprise owns Identity, Authentication, and the Enterprise Directory; ECMP
 * owns Membership and Authorization only. This local seed stands in for the
 * Enterprise Directory until Enterprise integration is officially enabled — it
 * is NOT the permanent Enterprise User source, and it is not a sanctioned copy
 * of Enterprise master data.
 *
 * ECMP only *searches* this directory and *displays* what it returns. It never
 * creates or edits an Enterprise identity. Replacing this module with a real
 * Enterprise API must not require any UX change: the screen depends on the
 * search/select shape below, not on where the rows come from.
 *
 * Fields present here are the only identity fields available to the UI. The
 * document's target set also names Organization / Department / Position; those
 * do not exist in this repository and must not be invented (UX-CU-003 §10.1).
 */
import candidatesJson from "./data/moduleUserCandidates.json";

/** Enterprise Directory identity only — role/unit are assigned by ECMP at registration. */
export type ModuleUserCandidate = {
  username: string;
  displayName: string;
  email: string;
  homeBranchCode: string;
  homeBranchName: string;
  region: string;
  cohort: string;
};

export const MODULE_USER_CANDIDATES: ModuleUserCandidate[] =
  candidatesJson as ModuleUserCandidate[];

/**
 * Directory marker for a person based at head office rather than a branch.
 * Head office is not an ECMP branch row, so it cannot be expressed as a
 * `branches.code` — the directory names it explicitly instead.
 */
export const HEAD_OFFICE_UNIT_CODE = "PUSAT";

/** True when the candidate's home unit is head office, not a branch. */
export function isHeadOfficeCandidate(
  candidate: Pick<ModuleUserCandidate, "homeBranchCode">,
): boolean {
  const code = candidate.homeBranchCode?.trim().toUpperCase();
  return !code || code === HEAD_OFFICE_UNIT_CODE;
}

/** Search central-directory candidates by 16-digit ID or display name. */
export function searchModuleUserCandidates(
  query: string,
  options?: {
    excludeUsernames?: ReadonlySet<string>;
    limit?: number;
  },
): ModuleUserCandidate[] {
  const q = query.trim().toLowerCase();
  if (q.length < 1) return [];
  const exclude = options?.excludeUsernames;
  const limit = options?.limit ?? 8;
  const out: ModuleUserCandidate[] = [];
  for (const row of MODULE_USER_CANDIDATES) {
    if (exclude?.has(row.username)) continue;
    const hay = `${row.username} ${row.displayName}`.toLowerCase();
    if (!hay.includes(q)) continue;
    out.push(row);
    if (out.length >= limit) break;
  }
  return out;
}

export type HighlightSegment = {
  text: string;
  matched: boolean;
};

/**
 * Split ``text`` so the first case-insensitive occurrence of ``query``
 * is a matched segment (for bolding typed ID/name prefixes in results).
 * Example: query ``31000``, text ``3100000000000001`` →
 * ``[{ text: "31000", matched: true }, { text: "00000000001", matched: false }]``.
 */
export function highlightMatchSegments(
  text: string,
  query: string,
): HighlightSegment[] {
  const q = query.trim();
  if (!q) return [{ text, matched: false }];
  const lowerText = text.toLowerCase();
  const lowerQuery = q.toLowerCase();
  const index = lowerText.indexOf(lowerQuery);
  if (index < 0) return [{ text, matched: false }];
  const before = text.slice(0, index);
  const match = text.slice(index, index + q.length);
  const after = text.slice(index + q.length);
  const segments: HighlightSegment[] = [];
  if (before) segments.push({ text: before, matched: false });
  segments.push({ text: match, matched: true });
  if (after) segments.push({ text: after, matched: false });
  return segments;
}
