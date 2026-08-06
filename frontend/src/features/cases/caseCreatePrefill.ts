/** One-shot prefill for Create Case after Aggregate complaint create. */

export interface CaseCreatePrefill {
  complaintId: string;
  caseType: string;
  category: string;
  subject: string;
  description: string;
  priority: string;
  destinationUnitId: string;
}

const STORAGE_KEY = "ecmp.cm.caseCreatePrefill.v1";

export function stashCaseCreatePrefill(prefill: CaseCreatePrefill): void {
  if (typeof window === "undefined") return;
  try {
    sessionStorage.setItem(STORAGE_KEY, JSON.stringify(prefill));
  } catch {
    // ignore quota / private mode
  }
}

/** Read and clear prefill when it matches the complaint. */
export function takeCaseCreatePrefill(
  complaintId: string,
): CaseCreatePrefill | null {
  if (typeof window === "undefined") return null;
  try {
    const raw = sessionStorage.getItem(STORAGE_KEY);
    if (!raw) return null;
    sessionStorage.removeItem(STORAGE_KEY);
    const parsed = JSON.parse(raw) as CaseCreatePrefill;
    if (!parsed || parsed.complaintId !== complaintId) return null;
    return parsed;
  } catch {
    try {
      sessionStorage.removeItem(STORAGE_KEY);
    } catch {
      /* ignore */
    }
    return null;
  }
}
