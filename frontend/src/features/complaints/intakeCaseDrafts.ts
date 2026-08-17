import { toCreateCaseRequest, type CreateCaseFormValues } from "@/features/cases/caseForms";
import {
  closeCmCase,
  createCmCase,
  recordCmCaseAcceptance,
  resolveCmCase,
  updateCmCaseStatus,
  type CmCase,
  type CmCaseStatus,
} from "@/lib/api/cmCase";
import type { CreateComplaintFormValues } from "./createComplaintForm";

/** BQ-003 Mode A: max Cases per Complaint including Case 1 from intake description. */
export const MAX_INTAKE_CASES = 5;
export const MAX_EXTRA_INTAKE_CASES = MAX_INTAKE_CASES - 1;

export type IntakeCaseAction = "register" | "close" | "escalate";

export interface IntakeExtraCaseDraft {
  id: string;
  description: string;
  priority?: string;
  note?: string;
  action?: IntakeCaseAction;
}

export interface IntakeCaseDecisionRow {
  id: string;
  n: number;
  description: string;
  priority: string;
  note: string;
  action: IntakeCaseAction;
}

export function parseIntakeCaseAction(raw: unknown): IntakeCaseAction {
  if (raw === "close" || raw === "escalate" || raw === "register") return raw;
  return "register";
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
    description: "",
    priority: "",
    note: "",
    action: "register",
  };
}

export function sanitizeExtraCaseDrafts(raw: unknown): IntakeExtraCaseDraft[] {
  if (!Array.isArray(raw)) return [];
  const out: IntakeExtraCaseDraft[] = [];
  for (const item of raw) {
    if (!item || typeof item !== "object") continue;
    const rec = item as Record<string, unknown>;
    const description =
      typeof rec.description === "string" ? rec.description : "";
    const id =
      typeof rec.id === "string" && rec.id.trim()
        ? rec.id.trim()
        : newIntakeExtraCaseId();
    out.push({
      id,
      description,
      priority: parseIntakePriority(rec.priority),
      note: typeof rec.note === "string" ? rec.note : "",
      action: parseIntakeCaseAction(rec.action),
    });
    if (out.length >= MAX_EXTRA_INTAKE_CASES) break;
  }
  return out;
}

export function buildIntakeDecisionRows(
  values: CreateComplaintFormValues,
  extraDrafts: IntakeExtraCaseDraft[],
  case1Action: IntakeCaseAction = "register",
): IntakeCaseDecisionRow[] {
  const rows: IntakeCaseDecisionRow[] = [
    {
      id: "primary",
      n: 1,
      description: values.description.trim() || values.subject.trim(),
      priority: parseIntakePriority(values.priority) || "",
      note: values.resolution.trim(),
      action: parseIntakeCaseAction(case1Action),
    },
  ];
  for (const draft of extraDrafts) {
    if (rows.length >= MAX_INTAKE_CASES) break;
    if (!draft.description.trim()) continue;
    rows.push({
      id: draft.id,
      n: rows.length + 1,
      description: draft.description.trim(),
      priority: parseIntakePriority(draft.priority),
      note: (draft.note ?? "").trim(),
      action: parseIntakeCaseAction(draft.action),
    });
  }
  return rows;
}

export function extrasFromDecisionRows(
  rows: IntakeCaseDecisionRow[],
): IntakeExtraCaseDraft[] {
  return rows.slice(1).map((row) => ({
    id: row.id,
    description: row.description,
    priority: row.priority,
    note: row.note,
    action: row.action,
  }));
}

export function anyIntakeCaseEscalates(rows: IntakeCaseDecisionRow[]): boolean {
  return rows.some((row) => row.action === "escalate");
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
    row.n === 1
      ? values.subject.trim() || description
      : description.slice(0, 500);
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
      }
    } catch {
      // Complaint already registered — remaining Cases can be added from Penanganan.
    }
  }
  return created;
}
