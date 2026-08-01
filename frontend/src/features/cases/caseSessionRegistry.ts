/** Session registry of known Case IDs per Complaint (no List API in Mode A). */

const PREFIX = "ecmp.cmCase.ids.";

export function listKnownCaseIds(complaintId: string): string[] {
  if (typeof window === "undefined") return [];
  const key = `${PREFIX}${complaintId.trim()}`;
  try {
    const raw = window.sessionStorage.getItem(key);
    if (!raw) return [];
    const parsed = JSON.parse(raw) as unknown;
    if (!Array.isArray(parsed)) return [];
    return parsed
      .filter((x): x is string => typeof x === "string" && x.trim().length > 0)
      .map((x) => x.trim());
  } catch {
    return [];
  }
}

export function rememberCaseId(complaintId: string, caseId: string): void {
  if (typeof window === "undefined") return;
  const cid = complaintId.trim();
  const id = caseId.trim();
  if (!cid || !id) return;
  const existing = listKnownCaseIds(cid);
  if (existing.includes(id)) return;
  const next = [...existing, id];
  window.sessionStorage.setItem(`${PREFIX}${cid}`, JSON.stringify(next));
}

export function clearKnownCaseIds(complaintId: string): void {
  if (typeof window === "undefined") return;
  window.sessionStorage.removeItem(`${PREFIX}${complaintId.trim()}`);
}
