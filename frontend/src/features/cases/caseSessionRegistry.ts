/** Session registry of known Case IDs per Complaint (no List API in Mode A). */

import { sameUserId } from "./handlingClaim";

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

const HANDLE_PREFIX = "ecmp.cmCase.handle.";

export type CaseHandleDecision = "claimed" | "viewed";

function handleKey(caseId: string): string {
  return `${HANDLE_PREFIX}${caseId.trim()}`;
}

export function getCaseHandleDecision(caseId: string): CaseHandleDecision | null {
  if (typeof window === "undefined") return null;
  const id = caseId.trim();
  if (!id) return null;
  try {
    const raw = window.sessionStorage.getItem(handleKey(id));
    if (raw === "claimed" || raw === "viewed") return raw;
    return null;
  } catch {
    return null;
  }
}

export function markCaseHandleClaimed(caseId: string): void {
  if (typeof window === "undefined") return;
  const id = caseId.trim();
  if (!id) return;
  window.sessionStorage.setItem(handleKey(id), "claimed");
}

export function markCaseHandleViewed(caseId: string): void {
  if (typeof window === "undefined") return;
  const id = caseId.trim();
  if (!id) return;
  window.sessionStorage.setItem(handleKey(id), "viewed");
}

/** Offer the handle-claim CTA unless terminal, no permission, or already claimed. */
export function shouldAskHandleClaim(opts: {
  status: string | null | undefined;
  canAct: boolean;
  decision: CaseHandleDecision | null;
  handlingClaimedBy?: string | null;
  userId?: string | null;
}): boolean {
  if (!opts.canAct) return false;
  if (opts.decision) return false;
  const status = (opts.status || "").trim().toUpperCase();
  if (!status) return false;
  if (status === "CLOSED" || status === "CANCELLED") return false;
  const claimed = (opts.handlingClaimedBy || "").trim();
  if (claimed && !sameUserId(claimed, opts.userId)) return false;
  if (claimed && sameUserId(claimed, opts.userId)) return false;
  return true;
}
