import type {
  Knowledge,
  KnowledgeCreateRequest,
  KnowledgeType,
  KnowledgeUpdateRequest,
} from "@/lib/api/types";

export interface KnowledgeFormValues {
  title: string;
  knowledgeType: KnowledgeType;
  documentNumber: string;
  summary: string;
  versionLabel: string;
  /** datetime-local input value ("" = unset). */
  effectiveFrom: string;
  effectiveTo: string;
}

export type KnowledgeFieldErrors = Partial<
  Record<keyof KnowledgeFormValues, string>
>;

export function createEmptyKnowledgeForm(): KnowledgeFormValues {
  return {
    title: "",
    knowledgeType: "SOP",
    documentNumber: "",
    summary: "",
    versionLabel: "",
    effectiveFrom: "",
    effectiveTo: "",
  };
}

/** ISO 8601 → "YYYY-MM-DDTHH:mm" for a native datetime-local input. */
function toDatetimeLocalValue(iso: string): string {
  const date = new Date(iso);
  if (Number.isNaN(date.getTime())) return "";
  const pad = (n: number) => String(n).padStart(2, "0");
  return `${date.getFullYear()}-${pad(date.getMonth() + 1)}-${pad(date.getDate())}T${pad(date.getHours())}:${pad(date.getMinutes())}`;
}

export function knowledgeFormFromExisting(existing: Knowledge): KnowledgeFormValues {
  return {
    title: existing.title,
    knowledgeType: existing.knowledgeType,
    documentNumber: existing.documentNumber ?? "",
    summary: existing.summary ?? "",
    versionLabel: existing.versionLabel ?? "",
    effectiveFrom: existing.effectiveFrom
      ? toDatetimeLocalValue(existing.effectiveFrom)
      : "",
    effectiveTo: existing.effectiveTo ? toDatetimeLocalValue(existing.effectiveTo) : "",
  };
}

export function validateKnowledgeForm(
  values: KnowledgeFormValues,
): KnowledgeFieldErrors {
  const errors: KnowledgeFieldErrors = {};

  if (!values.title.trim()) {
    errors.title = "required";
  } else if (values.title.trim().length > 200) {
    errors.title = "knowledgeTitleMax";
  }

  let fromDate: Date | null = null;
  if (values.effectiveFrom) {
    fromDate = new Date(values.effectiveFrom);
    if (Number.isNaN(fromDate.getTime())) {
      errors.effectiveFrom = "knowledgeEffectiveFromInvalid";
      fromDate = null;
    }
  }

  let toDate: Date | null = null;
  if (values.effectiveTo) {
    toDate = new Date(values.effectiveTo);
    if (Number.isNaN(toDate.getTime())) {
      errors.effectiveTo = "knowledgeEffectiveToInvalid";
      toDate = null;
    }
  }

  if (fromDate && toDate && fromDate >= toDate) {
    errors.effectiveTo = "knowledgeEffectiveToBeforeFrom";
  }

  return errors;
}

export function toKnowledgeCreateRequest(
  values: KnowledgeFormValues,
  opts?: { supersedesKnowledgeId?: string },
): KnowledgeCreateRequest {
  return {
    title: values.title.trim(),
    knowledgeType: values.knowledgeType,
    documentNumber: values.documentNumber.trim() || null,
    summary: values.summary.trim() || null,
    versionLabel: values.versionLabel.trim() || null,
    effectiveFrom: values.effectiveFrom
      ? new Date(values.effectiveFrom).toISOString()
      : null,
    effectiveTo: values.effectiveTo ? new Date(values.effectiveTo).toISOString() : null,
    supersedesKnowledgeId: opts?.supersedesKnowledgeId ?? null,
  };
}

export function toKnowledgeUpdateRequest(
  values: KnowledgeFormValues,
): KnowledgeUpdateRequest {
  return {
    title: values.title.trim(),
    knowledgeType: values.knowledgeType,
    documentNumber: values.documentNumber.trim() || null,
    summary: values.summary.trim() || null,
    versionLabel: values.versionLabel.trim() || null,
    effectiveFrom: values.effectiveFrom
      ? new Date(values.effectiveFrom).toISOString()
      : null,
    effectiveTo: values.effectiveTo ? new Date(values.effectiveTo).toISOString() : null,
  };
}
