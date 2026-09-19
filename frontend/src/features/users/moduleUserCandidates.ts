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

const LONG_ID_BASE = 3_100_000_000_000_000;

/** 3100000000000001 → 3101. Unrelated strings return null. */
export function shortLabUsernameFromLongId(value: string): string | null {
  const digits = value.trim();
  if (!/^\d{16}$/.test(digits) || !digits.startsWith("3100")) return null;
  const seq = Number(digits) - LONG_ID_BASE;
  if (!Number.isInteger(seq) || seq < 1) return null;
  return `31${String(seq).padStart(2, "0")}`;
}

/** 3101 → 3100000000000001. Unrelated strings return null. */
export function longLabIdFromShortUsername(value: string): string | null {
  const digits = value.trim();
  const match = /^31(\d+)$/.exec(digits);
  if (!match) return null;
  const seq = Number(match[1]);
  if (!Number.isInteger(seq) || seq < 1) return null;
  return String(LONG_ID_BASE + seq).padStart(16, "0");
}

export function emailLocalPart(email: string): string {
  const at = email.indexOf("@");
  return (at >= 0 ? email.slice(0, at) : email).trim();
}

/** Username, 16-digit identity, and email local-part for one directory row. */
export function candidateIdentityKeys(row: ModuleUserCandidate): string[] {
  return labIdentityAliases(row.username, row.email);
}

export function labIdentityAliases(...values: Array<string | null | undefined>): string[] {
  const out = new Set<string>();
  for (const raw of values) {
    const value = (raw ?? "").trim();
    if (!value) continue;
    out.add(value);
    const local = emailLocalPart(value);
    if (local) out.add(local);
    const short = shortLabUsernameFromLongId(local);
    const long = longLabIdFromShortUsername(local);
    if (short) out.add(short);
    if (long) out.add(long);
  }
  return [...out];
}

function searchNeedles(query: string): string[] {
  const q = query.trim().toLowerCase().replace(/\s+/g, " ");
  if (!q) return [];
  const needles = new Set<string>([q]);
  const compact = q.replace(/\s+/g, "");
  if (compact !== q) needles.add(compact);
  const digits = compact.replace(/\D/g, "");
  if (digits.length >= 2) {
    needles.add(digits);
    const short = shortLabUsernameFromLongId(digits);
    const long = longLabIdFromShortUsername(digits);
    if (short) needles.add(short.toLowerCase());
    if (long) needles.add(long.toLowerCase());
  }
  return [...needles];
}

function candidateHaystack(row: ModuleUserCandidate): string {
  return [
    row.username,
    row.displayName,
    row.email,
    emailLocalPart(row.email),
    row.homeBranchCode,
    row.homeBranchName,
    row.region,
    ...candidateIdentityKeys(row),
  ]
    .join(" ")
    .toLowerCase();
}

function rankCandidate(row: ModuleUserCandidate, query: string): number {
  const q = query.trim().toLowerCase();
  const username = row.username.toLowerCase();
  const name = row.displayName.toLowerCase();
  const keys = candidateIdentityKeys(row).map((key) => key.toLowerCase());
  if (keys.includes(q) || username === q) return 0;
  if (username.startsWith(q) || keys.some((key) => key.startsWith(q))) return 1;
  if (name.startsWith(q)) return 2;
  return 3;
}

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

function isRegisteredCandidate(
  row: ModuleUserCandidate,
  exclude?: ReadonlySet<string>,
): boolean {
  if (!exclude || exclude.size === 0) return false;
  return candidateIdentityKeys(row).some((key) => exclude.has(key));
}

/** Search by short ID (3101), 16-digit ID, name, email, or unit. */
export function searchModuleUserCandidates(
  query: string,
  options?: {
    excludeUsernames?: ReadonlySet<string>;
    limit?: number;
  },
): ModuleUserCandidate[] {
  const needles = searchNeedles(query);
  if (needles.length === 0) return [];
  const exclude = options?.excludeUsernames;
  const limit = options?.limit ?? 8;
  const hits: ModuleUserCandidate[] = [];
  for (const row of MODULE_USER_CANDIDATES) {
    if (isRegisteredCandidate(row, exclude)) continue;
    const hay = candidateHaystack(row);
    if (!needles.some((needle) => hay.includes(needle))) continue;
    hits.push(row);
  }
  hits.sort((a, b) => rankCandidate(a, query) - rankCandidate(b, query));
  return hits.slice(0, limit);
}

export type HighlightSegment = {
  text: string;
  matched: boolean;
};

/**
 * Split ``text`` so the first case-insensitive occurrence of ``query``
 * is a matched segment (for bolding typed ID/name prefixes in results).
 * Example: query ``31``, text ``3101`` →
 * ``[{ text: "31", matched: true }, { text: "01", matched: false }]``.
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
