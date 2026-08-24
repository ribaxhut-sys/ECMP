import { toCreateCaseRequest, type CreateCaseFormValues } from "@/features/cases/caseForms";
import {
  closeCmCase,
  createCmCase,
  escalateCmCaseToPusat,
  recordCmCaseAcceptance,
  resolveCmCase,
  updateCmCaseStatus,
  type CmCase,
  type CmCaseStatus,
} from "@/lib/api/cmCase";
import { isPusatUnitCode } from "@/shared/utils";
import type { CreateComplaintFormValues } from "./createComplaintForm";

/** BQ-003 Mode A: max Cases per Complaint including Case 1 from intake description. */
export const MAX_INTAKE_CASES = 5;
export const MAX_EXTRA_INTAKE_CASES = MAX_INTAKE_CASES - 1;
/** API-520 / DEC-029 — same floor as Case-page escalate-to-Pusat. */
export const ESCALATE_TO_PUSAT_REASON_MIN = 20;

export type IntakeCaseAction = "register" | "close" | "escalate";

export interface IntakeExtraCaseDraft {
  id: string;
  /** Case title — required when the extra card is filled. */
  subject?: string;
  description: string;
  priority?: string;
  note?: string;
  action?: IntakeCaseAction;
  /** Local lock on the priority step; not sent to the API. */
  locked?: boolean;
}

export type IntakeCaseRowIssue = "priority" | "note" | "escalateShort";

export interface IntakeCaseDecisionRow {
  id: string;
  n: number;
  subject: string;
  description: string;
  priority: string;
  note: string;
  action: IntakeCaseAction;
  locked?: boolean;
}

export function parseIntakeCaseAction(raw: unknown): IntakeCaseAction {
  if (raw === "close" || raw === "register" || raw === "escalate") return raw;
  return "register";
}

/** Cabang → Pusat only. Recording at Pusat has nowhere to escalate. */
export function intakeMayEscalateToPusat(
  recordingUnitCode: string | null | undefined,
): boolean {
  return !isPusatUnitCode(recordingUnitCode);
}

export function parseIntakePriority(raw: unknown): string {
  const p = typeof raw === "string" ? raw.trim().toUpperCase() : "";
  if (p === "LOW" || p === "MEDIUM" || p === "HIGH" || p === "CRITICAL") return p;
  return "";
}

export function newIntakeExtraCaseId(): string {
  if (typeof crypto !== "undefined" && "randomUUID" in crypto) {
    return crypto.randomUUID();
  }
  return `extra-${Date.now()}-${Math.random().toString(16).slice(2)}`;
}

export function emptyExtraCaseDraft(): IntakeExtraCaseDraft {
  return {
    id: newIntakeExtraCaseId(),
    subject: "",
    description: "",
    priority: "",
    note: "",
    action: "register",
  };
}

/** Extra cards left blank (no uraian and no catatan) are dropped on Lanjut. */
export function filledExtraCaseDrafts(
  drafts: IntakeExtraCaseDraft[],
): IntakeExtraCaseDraft[] {
  return drafts.filter(
    (draft) => draft.description.trim() || (draft.note ?? "").trim(),
  );
}

export type ExtraIntakeCaseIssue = {
  id: string;
  subject?: "required" | "max";
  description?: "required" | "max";
  note?: "required" | "max";
};

export function extraIntakeCaseIssues(
  drafts: IntakeExtraCaseDraft[],
): ExtraIntakeCaseIssue[] {
  const issues: ExtraIntakeCaseIssue[] = [];
  for (const draft of filledExtraCaseDrafts(drafts)) {
    const issue: ExtraIntakeCaseIssue = { id: draft.id };
    const subject = (draft.subject ?? "").trim();
    if (!subject) issue.subject = "required";
    else if (subject.length > 200) issue.subject = "max";
    if (!draft.description.trim()) issue.description = "required";
    else if (draft.description.length > 5000) issue.description = "max";
    if (!(draft.note ?? "").trim()) issue.note = "required";
    else if ((draft.note ?? "").length > 5000) issue.note = "max";
    if (issue.subject || issue.description || issue.note) issues.push(issue);
  }
  return issues;
}

export function sanitizeExtraCaseDrafts(raw: unknown): IntakeExtraCaseDraft[] {
  if (!Array.isArray(raw)) return [];
  const out: IntakeExtraCaseDraft[] = [];
  for (const item of raw) {
    if (!item || typeof item !== "object") continue;
    const rec = item as Record<string, unknown>;
    const description =
      typeof rec.description === "string" ? rec.description : "";
    const subject = typeof rec.subject === "string" ? rec.subject.slice(0, 200) : "";
    const id =
      typeof rec.id === "string" && rec.id.trim()
        ? rec.id.trim()
        : newIntakeExtraCaseId();
    out.push({
      id,
      subject,
      description,
      priority: parseIntakePriority(rec.priority),
      note: typeof rec.note === "string" ? rec.note : "",
      action: parseIntakeCaseAction(rec.action),
      locked: rec.locked === true,
    });
    if (out.length >= MAX_EXTRA_INTAKE_CASES) break;
  }
  return out;
}

export function buildIntakeDecisionRows(
  values: CreateComplaintFormValues,
  extraDrafts: IntakeExtraCaseDraft[],
  case1Action: IntakeCaseAction = "register",
  case1Locked = false,
): IntakeCaseDecisionRow[] {
  const rows: IntakeCaseDecisionRow[] = [
    {
      id: "primary",
      n: 1,
      subject: values.subject.trim(),
      description: values.description.trim() || values.subject.trim(),
      priority: parseIntakePriority(values.priority) || "",
      note: values.resolution.trim(),
      action: parseIntakeCaseAction(case1Action),
      locked: case1Locked,
    },
  ];
  for (const draft of extraDrafts) {
    if (rows.length >= MAX_INTAKE_CASES) break;
    if (!draft.description.trim()) continue;
    rows.push({
      id: draft.id,
      n: rows.length + 1,
      subject: (draft.subject ?? "").trim(),
      description: draft.description.trim(),
      priority: parseIntakePriority(draft.priority),
      note: (draft.note ?? "").trim(),
      action: parseIntakeCaseAction(draft.action),
      locked: draft.locked === true,
    });
  }
  return rows;
}

export function extrasFromDecisionRows(
  rows: IntakeCaseDecisionRow[],
): IntakeExtraCaseDraft[] {
  return rows.slice(1).map((row) => ({
    id: row.id,
    subject: row.subject,
    description: row.description,
    priority: row.priority,
    note: row.note,
    action: row.action,
    locked: row.locked === true,
  }));
}

export function anyIntakeCaseEscalates(rows: IntakeCaseDecisionRow[]): boolean {
  return rows.some((row) => row.action === "escalate");
}

export function validateIntakeCaseRow(
  row: IntakeCaseDecisionRow,
): IntakeCaseRowIssue | null {
  if (!parseIntakePriority(row.priority)) return "priority";
  if (!row.note.trim()) return "note";
  if (
    row.action === "escalate" &&
    row.note.trim().length < ESCALATE_TO_PUSAT_REASON_MIN
  ) {
    return "escalateShort";
  }
  return null;
}

export function intakeDecisionLockSummary(rows: IntakeCaseDecisionRow[]): {
  total: number;
  locked: number;
  escalate: number;
  requiresLock: boolean;
  allLocked: boolean;
} {
  const total = rows.length;
  const requiresLock = total >= 1;
  const locked = rows.filter((row) => row.locked === true).length;
  const escalate = rows.filter((row) => row.action === "escalate").length;
  return {
    total,
    locked,
    escalate,
    requiresLock,
    allLocked: !requiresLock || (total > 0 && locked === total),
  };
}

function caseTypeFromComplaint(values: CreateComplaintFormValues): string {
  const category = values.category.trim() || "GENERAL";
  return category;
}

function fallbackPriority(values: CreateComplaintFormValues): string {
  const p = parseIntakePriority(values.priority);
  return p || "MEDIUM";
}

function formFromRow(
  values: CreateComplaintFormValues,
  row: IntakeCaseDecisionRow,
  destinationUnitId: string,
): CreateCaseFormValues {
  const caseType = caseTypeFromComplaint(values);
  const description = row.description.trim() || values.subject.trim();
  const subject =
    (row.subject ?? "").trim() ||
    (row.n === 1 ? values.subject.trim() : "") ||
    description.slice(0, 200);
  return {
    caseType,
    category: caseType,
    subject,
    description,
    priority: parseIntakePriority(row.priority) || fallbackPriority(values),
    destinationUnitId: destinationUnitId.trim(),
  };
}

/**
 * Case 1 = main complaint description (always first).
 * Extra drafts with empty description are skipped.
 */
export function buildIntakeCaseForms(
  values: CreateComplaintFormValues,
  extraDrafts: IntakeExtraCaseDraft[],
  destinationUnitId: string,
): CreateCaseFormValues[] {
  return buildIntakeDecisionRows(values, extraDrafts).map((row) =>
    formFromRow(values, row, destinationUnitId),
  );
}

async function closeIntakeCase(created: CmCase, note: string): Promise<void> {
  const comment = note.trim();
  if (!comment) return;
  const dest = (created.owningUnitId || created.ownerUnitId || "").trim();
  let current = created;
  const claimed = await updateCmCaseStatus(current.caseId, {
    toStatus: current.status,
    reason: "HANDLE_CLAIM",
  });
  current = claimed.data;
  if (current.status === "CREATED") {
    const assigned = await updateCmCaseStatus(current.caseId, {
      toStatus: "ASSIGNED",
      destinationUnitId: dest || undefined,
    });
    current = assigned.data;
  }
  if (current.status === "ASSIGNED") {
    const started = await updateCmCaseStatus(current.caseId, {
      toStatus: "IN_PROGRESS" satisfies CmCaseStatus,
    });
    current = started.data;
  }
  if (current.status !== "IN_PROGRESS") return;
  const resolved = await resolveCmCase(current.caseId, {
    action: "ACCEPT",
    comment,
  });
  current = resolved.data;
  if (current.status === "CLOSED") return;
  if (current.status === "RESOLVED") {
    const accepted = await recordCmCaseAcceptance(current.caseId, {
      party: "OWNER",
      decision: "ACCEPT",
      note: comment,
    });
    current = accepted.data;
  }
  if (current.status === "CLOSED") return;
  await closeCmCase(current.caseId, { note: comment });
}

export async function createIntakeCasesForRegisteredComplaint(options: {
  complaintId: string;
  values: CreateComplaintFormValues;
  extraDrafts: IntakeExtraCaseDraft[];
  destinationUnitId: string;
  rows?: IntakeCaseDecisionRow[];
}): Promise<number> {
  const rows =
    options.rows ??
    buildIntakeDecisionRows(options.values, options.extraDrafts);
  let created = 0;
  for (const row of rows) {
    try {
      const form = formFromRow(
        options.values,
        row,
        options.destinationUnitId,
      );
      const res = await createCmCase(
        toCreateCaseRequest(options.complaintId, form, {
          note: row.note,
          intakeAction: row.action,
        }),
        {
          idempotencyKey:
            typeof crypto !== "undefined" && "randomUUID" in crypto
              ? crypto.randomUUID()
              : undefined,
        },
      );
      created += 1;
      if (row.action === "close") {
        await closeIntakeCase(res.data, row.note || options.values.resolution);
      } else if (row.action === "escalate") {
        const reason = (row.note || options.values.resolution).trim();
        await escalateCmCaseToPusat(res.data.caseId, { reason });
      }
    } catch (err) {
      if (row.action === "escalate") throw err;
      // Complaint already registered — remaining Cases can be added from Penanganan.
    }
  }
  return created;
}
