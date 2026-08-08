/** One-shot draft for escalate priority step after create-form CTA. */

import type { CreateComplaintFormValues } from "./createComplaintForm";

export interface EscalateIntakeDraft {
  values: CreateComplaintFormValues;
  stagingToken: string;
  hasStagedAttachments: boolean;
  overrideJustification: string | null;
  /** Branch.code for recordingUnitId (preferred over values.branchId UUID). */
  recordingUnitCode?: string | null;
}

const STORAGE_KEY = "ecmp.cm.escalateIntakeDraft.v1";

export function stashEscalateIntakeDraft(draft: EscalateIntakeDraft): void {
  if (typeof window === "undefined") return;
  try {
    sessionStorage.setItem(STORAGE_KEY, JSON.stringify(draft));
  } catch {
    // ignore quota / private mode
  }
}

export function peekEscalateIntakeDraft(): EscalateIntakeDraft | null {
  if (typeof window === "undefined") return null;
  try {
    const raw = sessionStorage.getItem(STORAGE_KEY);
    if (!raw) return null;
    const parsed = JSON.parse(raw) as EscalateIntakeDraft;
    if (!parsed?.values?.customerId?.trim()) return null;
    return parsed;
  } catch {
    return null;
  }
}

export function clearEscalateIntakeDraft(): void {
  if (typeof window === "undefined") return;
  try {
    sessionStorage.removeItem(STORAGE_KEY);
  } catch {
    /* ignore */
  }
}
