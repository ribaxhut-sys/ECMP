import { toCreateCaseRequest, type CreateCaseFormValues } from "@/features/cases/caseForms";
import { createCmCase } from "@/lib/api/cmCase";
import type { CreateComplaintFormValues } from "./createComplaintForm";

/** BQ-003 Mode A: max Cases per Complaint including Case 1 from intake description. */
export const MAX_INTAKE_CASES = 5;
export const MAX_EXTRA_INTAKE_CASES = MAX_INTAKE_CASES - 1;

export interface IntakeExtraCaseDraft {
  id: string;
  description: string;
}

export function newIntakeExtraCaseId(): string {
  if (typeof crypto !== "undefined" && "randomUUID" in crypto) {
    return crypto.randomUUID();
  }
  return `extra-${Date.now()}-${Math.random().toString(16).slice(2)}`;
}

export function emptyExtraCaseDraft(): IntakeExtraCaseDraft {
  return { id: newIntakeExtraCaseId(), description: "" };
}

export function sanitizeExtraCaseDrafts(raw: unknown): IntakeExtraCaseDraft[] {
  if (!Array.isArray(raw)) return [];
  const out: IntakeExtraCaseDraft[] = [];
  for (const item of raw) {
    if (!item || typeof item !== "object") continue;
    const rec = item as { id?: unknown; description?: unknown };
    const description =
      typeof rec.description === "string" ? rec.description : "";
    const id =
      typeof rec.id === "string" && rec.id.trim()
        ? rec.id.trim()
        : newIntakeExtraCaseId();
    out.push({ id, description });
    if (out.length >= MAX_EXTRA_INTAKE_CASES) break;
  }
  return out;
}

function caseTypeFromComplaint(values: CreateComplaintFormValues): string {
  const category = values.category.trim() || "GENERAL";
  return category;
}

function priorityFromComplaint(values: CreateComplaintFormValues): string {
  const p = values.priority.trim().toUpperCase();
  if (p === "LOW" || p === "MEDIUM" || p === "HIGH" || p === "CRITICAL") {
    return p;
  }
  return "MEDIUM";
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
  const caseType = caseTypeFromComplaint(values);
  const priority = priorityFromComplaint(values);
  const subject = values.subject.trim();
  const dest = destinationUnitId.trim();
  const forms: CreateCaseFormValues[] = [
    {
      caseType,
      category: caseType,
      subject,
      description: values.description.trim() || subject,
      priority,
      destinationUnitId: dest,
    },
  ];
  for (const draft of extraDrafts) {
    if (forms.length >= MAX_INTAKE_CASES) break;
    const description = draft.description.trim();
    if (!description) continue;
    forms.push({
      caseType,
      category: caseType,
      subject,
      description,
      priority,
      destinationUnitId: dest,
    });
  }
  return forms;
}

export async function createIntakeCasesForRegisteredComplaint(options: {
  complaintId: string;
  values: CreateComplaintFormValues;
  extraDrafts: IntakeExtraCaseDraft[];
  destinationUnitId: string;
}): Promise<number> {
  const forms = buildIntakeCaseForms(
    options.values,
    options.extraDrafts,
    options.destinationUnitId,
  );
  let created = 0;
  for (const form of forms) {
    try {
      await createCmCase(toCreateCaseRequest(options.complaintId, form), {
        idempotencyKey:
          typeof crypto !== "undefined" && "randomUUID" in crypto
            ? crypto.randomUUID()
            : undefined,
      });
      created += 1;
    } catch {
      // Complaint already registered — extra Cases can be added from Penanganan.
    }
  }
  return created;
}
