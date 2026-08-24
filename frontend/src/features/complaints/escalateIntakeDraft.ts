/** One-shot draft for priority step after create-form "Lanjut". */

import type { CreateComplaintFormValues } from "./createComplaintForm";
import {
  parseIntakeCaseAction,
  sanitizeExtraCaseDrafts,
  type IntakeCaseAction,
  type IntakeExtraCaseDraft,
} from "./intakeCaseDrafts";

export type IntakePriorityDraftIntent = "register" | "escalate";

export interface EscalateIntakeDraft {
  values: CreateComplaintFormValues;
  stagingToken: string;
  hasStagedAttachments: boolean;
  overrideJustification: string | null;
  /** Branch.code for recordingUnitId (preferred over values.branchId UUID). */
  recordingUnitCode?: string | null;
  /**
   * Chosen on the priority step (Daftarkan vs Ajukan eskalasi).
   * Omitted / undefined after "Lanjut" until the user picks an action.
   */
  intent?: IntakePriorityDraftIntent;
  /** Extra Case drafts (Case 2…n). Case 1 is the main complaint description. */
  extraCaseDrafts?: IntakeExtraCaseDraft[];
  /** Putusan Case 1 di langkah prioritas (default daftarkan). */
  case1Action?: IntakeCaseAction;
  /** Local lock for Case 1 on the priority step. */
  case1Locked?: boolean;
  /** Advisory HQ arrival proposal — sent only when a Case escalates. */
  proposedArrivalDate?: string | null;
  proposedArrivalTime?: string | null;
}

const STORAGE_KEY = "ecmp.cm.escalateIntakeDraft.v1";
/**
 * Legacy one-shot Back flag (pre always-restore). Still cleared for hygiene;
 * create form restores whenever a draft exists — breadcrumb / browser Back too.
 */
const RESUME_FLAG_KEY = "ecmp.cm.intakeFormResume.v1";

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
    if (parsed.intent !== "register" && parsed.intent !== "escalate") {
      delete parsed.intent;
    }
    parsed.extraCaseDrafts = sanitizeExtraCaseDrafts(parsed.extraCaseDrafts);
    parsed.case1Action = parseIntakeCaseAction(parsed.case1Action);
    parsed.case1Locked = parsed.case1Locked === true;
    parsed.proposedArrivalDate =
      typeof parsed.proposedArrivalDate === "string"
        ? parsed.proposedArrivalDate
        : undefined;
    parsed.proposedArrivalTime =
      typeof parsed.proposedArrivalTime === "string"
        ? parsed.proposedArrivalTime
        : undefined;
    return parsed;
  } catch {
    return null;
  }
}

export function clearEscalateIntakeDraft(): void {
  if (typeof window === "undefined") return;
  try {
    sessionStorage.removeItem(STORAGE_KEY);
    sessionStorage.removeItem(RESUME_FLAG_KEY);
  } catch {
    /* ignore */
  }
}

/** @deprecated No longer required — create form restores any stashed draft on mount. */
export function markIntakeFormResume(): void {
  if (typeof window === "undefined") return;
  try {
    sessionStorage.setItem(RESUME_FLAG_KEY, "1");
  } catch {
    /* ignore */
  }
}

/** @deprecated Clears legacy flag only; restore no longer depends on this. */
export function consumeIntakeFormResume(): boolean {
  if (typeof window === "undefined") return false;
  try {
    const marked = sessionStorage.getItem(RESUME_FLAG_KEY) === "1";
    sessionStorage.removeItem(RESUME_FLAG_KEY);
    return marked;
  } catch {
    return false;
  }
}
